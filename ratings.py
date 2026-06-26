from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_create, odoo_write
from auth_utils import login_required
from helpers import success, error, required_fields
from config import MODEL_CONTACT, RATING_MODEL

ratings_bp = Blueprint("ratings", __name__, url_prefix="/api/ratings")

FIELDS = ["id", "x_rater_id", "x_ratee_id", "x_session_id",
          "x_score", "x_comment", "create_date"]


@ratings_bp.route("", methods=["POST"])
@login_required
def submit_rating():
    data    = request.get_json(silent=True) or {}
    missing = required_fields(data, ["ratee_id", "session_id", "score"])
    if missing:
        return error(f"حقول ناقصة: {', '.join(missing)}")

    rater_id = request.current_user["user_id"]
    ratee_id = int(data["ratee_id"])
    score    = float(data["score"])

    if rater_id == ratee_id:
        return error("مينفعش تقيّم نفسك")
    if not (1 <= score <= 5):
        return error("التقييم لازم يكون من 1 لـ 5")

    existing = odoo_search_read(RATING_MODEL,
                                [["x_rater_id", "=", rater_id],
                                 ["x_session_id", "=", int(data["session_id"])]],
                                fields=["id"], limit=1)
    if existing:
        return error("قيّمت الجلسة دي قبل كده", 409)

    odoo_create(RATING_MODEL, {
        "x_rater_id":   rater_id,
        "x_ratee_id":   ratee_id,
        "x_session_id": int(data["session_id"]),
        "x_score":      score,
        "x_comment":    data.get("comment", ""),
    })

    all_ratings = odoo_search_read(RATING_MODEL, [["x_ratee_id", "=", ratee_id]],
                                   fields=["x_score"], limit=500)
    if all_ratings:
        avg = sum(r["x_score"] for r in all_ratings) / len(all_ratings)
        odoo_write(MODEL_CONTACT, [ratee_id], {"x_rating": round(avg, 2)})

    return success(message="تم إرسال التقييم", status=201)


@ratings_bp.route("/<int:user_id>", methods=["GET"])
@login_required
def get_ratings(user_id):
    records = odoo_search_read(RATING_MODEL, [["x_ratee_id", "=", user_id]],
                               fields=FIELDS, limit=50, order="create_date desc")
    avg = round(sum(r["x_score"] for r in records) / len(records), 2) if records else 0.0
    return success({
        "user_id":        user_id,
        "average":        avg,
        "total_ratings":  len(records),
        "ratings": [{
            "id":         r["id"],
            "rater_id":   r.get("x_rater_id"),
            "score":      r.get("x_score"),
            "comment":    r.get("x_comment", ""),
            "created_at": r.get("create_date", ""),
        } for r in records]
    })
