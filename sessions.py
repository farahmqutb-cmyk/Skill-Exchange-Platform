from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_create, odoo_write
from auth_utils import login_required
from helpers import success, error, required_fields, paginate_params
from config import MODEL_CALENDAR, MODEL_CRM_LEAD, MODEL_CONTACT

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

FIELDS = ["id", "name", "x_request_id", "x_teacher_id", "x_learner_id",
          "x_skill_name", "start", "x_duration_min", "x_location_type",
          "x_meet_link", "x_address", "x_status", "description", "create_date"]


@sessions_bp.route("", methods=["POST"])
@login_required
def create_session():
    data    = request.get_json(silent=True) or {}
    missing = required_fields(data, ["request_id", "teacher_id", "learner_id",
                                     "skill_name", "scheduled_at"])
    if missing:
        return error(f"حقول ناقصة: {', '.join(missing)}")

    my_id      = request.current_user["user_id"]
    teacher_id = int(data["teacher_id"])
    learner_id = int(data["learner_id"])

    if my_id not in (teacher_id, learner_id):
        return error("لازم تكون التيتشر أو اللارنر في الجلسة", 403)

    reqs = odoo_search_read(MODEL_CRM_LEAD,
                            [["id", "=", int(data["request_id"])],
                             ["x_status", "=", "accepted"]],
                            fields=["id"], limit=1)
    if not reqs:
        return error("الطلب مش موجود أو مش accepted", 400)

    event_id = odoo_create(MODEL_CALENDAR, {
        "name":            f"Skill Session: {data['skill_name']}",
        "start":           data["scheduled_at"],
        "stop":            data["scheduled_at"],
        "x_request_id":   int(data["request_id"]),
        "x_teacher_id":   teacher_id,
        "x_learner_id":   learner_id,
        "x_skill_name":   data["skill_name"],
        "x_duration_min": int(data.get("duration_min", 60)),
        "x_location_type": data.get("location_type", "online"),
        "x_meet_link":    data.get("meet_link", ""),
        "x_address":      data.get("address", ""),
        "x_status":       "scheduled",
        "description":    data.get("notes", ""),
    })
    return success({"session_id": event_id}, "تم حجز الجلسة", 201)


@sessions_bp.route("", methods=["GET"])
@login_required
def list_sessions():
    page, limit, offset = paginate_params()
    my_id  = request.current_user["user_id"]
    role   = request.args.get("role")
    status = request.args.get("status")

    if role == "teacher":
        domain = [["x_teacher_id", "=", my_id]]
    elif role == "learner":
        domain = [["x_learner_id", "=", my_id]]
    else:
        domain = ["|", ["x_teacher_id", "=", my_id], ["x_learner_id", "=", my_id]]

    if status:
        domain.append(["x_status", "=", status])

    records = odoo_search_read(MODEL_CALENDAR, domain, fields=FIELDS,
                               limit=limit, offset=offset, order="start desc")
    return success({"sessions": [_fmt(s) for s in records], "page": page, "limit": limit})


@sessions_bp.route("/<int:sess_id>", methods=["GET"])
@login_required
def get_session(sess_id):
    my_id   = request.current_user["user_id"]
    records = odoo_search_read(MODEL_CALENDAR, [["id", "=", sess_id]], fields=FIELDS, limit=1)
    if not records:
        return error("الجلسة مش موجودة", 404)
    s = records[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)
    return success(_fmt(s))


@sessions_bp.route("/<int:sess_id>/complete", methods=["PUT"])
@login_required
def complete_session(sess_id):
    my_id   = request.current_user["user_id"]
    records = odoo_search_read(MODEL_CALENDAR, [["id", "=", sess_id]], fields=FIELDS, limit=1)
    if not records:
        return error("الجلسة مش موجودة", 404)
    s = records[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)
    if s["x_status"] != "scheduled":
        return error("الجلسة مش في حالة scheduled")

    odoo_write(MODEL_CALENDAR, [sess_id], {"x_status": "completed"})

    for uid in [s["x_teacher_id"], s["x_learner_id"]]:
        users = odoo_search_read(MODEL_CONTACT, [["id", "=", uid]],
                                 fields=["x_total_sessions"], limit=1)
        if users:
            current = users[0].get("x_total_sessions", 0) or 0
            odoo_write(MODEL_CONTACT, [uid], {"x_total_sessions": current + 1})

    return success(message="تمت الجلسة بنجاح")


@sessions_bp.route("/<int:sess_id>/cancel", methods=["PUT"])
@login_required
def cancel_session(sess_id):
    my_id   = request.current_user["user_id"]
    records = odoo_search_read(MODEL_CALENDAR, [["id", "=", sess_id]], fields=FIELDS, limit=1)
    if not records:
        return error("الجلسة مش موجودة", 404)
    s = records[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)

    odoo_write(MODEL_CALENDAR, [sess_id], {"x_status": "cancelled"})
    return success(message="تم إلغاء الجلسة")


def _fmt(s):
    return {
        "id":            s["id"],
        "request_id":    s.get("x_request_id"),
        "teacher_id":    s.get("x_teacher_id"),
        "learner_id":    s.get("x_learner_id"),
        "skill_name":    s.get("x_skill_name", ""),
        "scheduled_at":  s.get("start", ""),
        "duration_min":  s.get("x_duration_min", 60),
        "location_type": s.get("x_location_type", "online"),
        "meet_link":     s.get("x_meet_link", ""),
        "address":       s.get("x_address", ""),
        "status":        s.get("x_status", "scheduled"),
        "notes":         s.get("description", ""),
        "created_at":    s.get("create_date", ""),
    }
