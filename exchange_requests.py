from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_create, odoo_write
from auth_utils import login_required
from helpers import success, error, required_fields, paginate_params
from config import MODEL_CRM_LEAD, MODEL_CONTACT
try:
    from email_notify import notify_new_request, notify_request_accepted, notify_request_rejected
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False

requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

FIELDS = ["id", "name", "x_sender_id", "x_receiver_id",
          "x_offered_skill", "x_wanted_skill",
          "x_message", "x_status", "create_date", "write_date"]


@requests_bp.route("", methods=["POST"])
@login_required
def send_request():
    data    = request.get_json(silent=True) or {}
    missing = required_fields(data, ["receiver_id", "offered_skill", "wanted_skill"])
    if missing:
        return error(f"حقول ناقصة: {', '.join(missing)}")

    sender_id   = request.current_user["user_id"]
    receiver_id = int(data["receiver_id"])

    if sender_id == receiver_id:
        return error("مينفعش تبعت طلب لنفسك")

    r = odoo_search_read(MODEL_CONTACT,
                         [["id", "=", receiver_id], ["x_is_skillswap_user", "=", True]],
                         fields=["id"], limit=1)
    if not r:
        return error("المستخدم ده مش موجود", 404)

    dup = odoo_search_read(MODEL_CRM_LEAD,
                           [["x_sender_id", "=", sender_id],
                            ["x_receiver_id", "=", receiver_id],
                            ["x_status", "=", "pending"]],
                           fields=["id"], limit=1)
    if dup:
        return error("عندك طلب pending لنفس الشخص", 409)

    lead_id = odoo_create(MODEL_CRM_LEAD, {
        "name":            f"Skill Exchange: {data['offered_skill']} ↔ {data['wanted_skill']}",
        "x_sender_id":     sender_id,
        "x_receiver_id":   receiver_id,
        "x_offered_skill": data["offered_skill"],
        "x_wanted_skill":  data["wanted_skill"],
        "x_message":       data.get("message", ""),
        "x_status":        "pending",
        "type":            "lead",
    })

    # ══ إرسال إشعار بالإيميل للمستلم ══
    if EMAIL_ENABLED:
        try:
            sender_info = odoo_search_read(MODEL_CONTACT, [["id", "=", sender_id]],
                                           fields=["name", "x_email"], limit=1)
            receiver_info = odoo_search_read(MODEL_CONTACT, [["id", "=", receiver_id]],
                                             fields=["name", "x_email"], limit=1)
            if sender_info and receiver_info:
                s = sender_info[0]
                rv = receiver_info[0]
                if rv.get("x_email"):
                    notify_new_request(
                        receiver_email=rv["x_email"],
                        receiver_name=rv["name"],
                        sender_name=s["name"],
                        offered_skill=data["offered_skill"],
                        wanted_skill=data["wanted_skill"],
                        message=data.get("message", ""),
                        request_id=lead_id
                    )
        except Exception as e:
            print(f"⚠️ Email notification failed: {e}")

    return success({"request_id": lead_id}, "تم إرسال الطلب", 201)


@requests_bp.route("", methods=["GET"])
@login_required
def list_requests():
    page, limit, offset = paginate_params()
    my_id  = request.current_user["user_id"]
    kind   = request.args.get("kind", "all")
    status = request.args.get("status")

    if kind == "sent":
        domain = [["x_sender_id", "=", my_id]]
    elif kind == "received":
        domain = [["x_receiver_id", "=", my_id]]
    else:
        domain = ["|", ["x_sender_id", "=", my_id], ["x_receiver_id", "=", my_id]]

    if status:
        domain.append(["x_status", "=", status])

    records = odoo_search_read(MODEL_CRM_LEAD, domain, fields=FIELDS,
                               limit=limit, offset=offset, order="create_date desc")
    return success({"requests": [_fmt(r) for r in records], "page": page, "limit": limit})


@requests_bp.route("/<int:req_id>", methods=["GET"])
@login_required
def get_request(req_id):
    my_id   = request.current_user["user_id"]
    records = odoo_search_read(MODEL_CRM_LEAD, [["id", "=", req_id]], fields=FIELDS, limit=1)
    if not records:
        return error("الطلب مش موجود", 404)
    rec = records[0]
    if rec["x_sender_id"] != my_id and rec["x_receiver_id"] != my_id:
        return error("مش مسموح", 403)
    return success(_fmt(rec))


@requests_bp.route("/<int:req_id>/accept", methods=["PUT"])
@login_required
def accept_request(req_id):
    return _update_status(req_id, "accepted", role="receiver")


@requests_bp.route("/<int:req_id>/reject", methods=["PUT"])
@login_required
def reject_request(req_id):
    return _update_status(req_id, "rejected", role="receiver")


@requests_bp.route("/<int:req_id>/cancel", methods=["PUT"])
@login_required
def cancel_request(req_id):
    return _update_status(req_id, "cancelled", role="sender")


def _update_status(req_id, new_status, role):
    my_id   = request.current_user["user_id"]
    records = odoo_search_read(MODEL_CRM_LEAD, [["id", "=", req_id]], fields=FIELDS, limit=1)
    if not records:
        return error("الطلب مش موجود", 404)
    rec = records[0]

    if role == "receiver" and rec["x_receiver_id"] != my_id:
        return error("بس المستلم يقدر يعمل الحاجة دي", 403)
    if role == "sender" and rec["x_sender_id"] != my_id:
        return error("بس المرسل يقدر يعمل الحاجة دي", 403)
    if rec["x_status"] != "pending":
        return error(f"الطلب حالته '{rec['x_status']}' مش pending")

    odoo_write(MODEL_CRM_LEAD, [req_id], {"x_status": new_status})

    # ══ إرسال إشعار بالإيميل ══
    if EMAIL_ENABLED and new_status in ("accepted", "rejected"):
        try:
            rec = records[0]
            sender_info   = odoo_search_read(MODEL_CONTACT, [["id", "=", rec["x_sender_id"]]],
                                             fields=["name", "x_email"], limit=1)
            receiver_info = odoo_search_read(MODEL_CONTACT, [["id", "=", rec["x_receiver_id"]]],
                                             fields=["name", "x_email"], limit=1)
            if sender_info and receiver_info:
                s  = sender_info[0]
                rv = receiver_info[0]
                if new_status == "accepted" and s.get("x_email"):
                    notify_request_accepted(
                        sender_email=s["x_email"],
                        sender_name=s["name"],
                        receiver_name=rv["name"],
                        offered_skill=rec.get("x_offered_skill", ""),
                        wanted_skill=rec.get("x_wanted_skill", "")
                    )
                elif new_status == "rejected" and s.get("x_email"):
                    notify_request_rejected(
                        sender_email=s["x_email"],
                        sender_name=s["name"],
                        receiver_name=rv["name"]
                    )
        except Exception as e:
            print(f"⚠️ Email notification failed: {e}")

    return success(message=f"تم تغيير الحالة إلى {new_status}")


def _fmt(r):
    return {
        "id":            r["id"],
        "title":         r.get("name", ""),
        "sender_id":     r.get("x_sender_id"),
        "receiver_id":   r.get("x_receiver_id"),
        "offered_skill": r.get("x_offered_skill", ""),
        "wanted_skill":  r.get("x_wanted_skill", ""),
        "message":       r.get("x_message", ""),
        "status":        r.get("x_status", "pending"),
        "created_at":    r.get("create_date", ""),
        "updated_at":    r.get("write_date", ""),
    }
