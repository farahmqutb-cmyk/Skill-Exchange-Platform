from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_write
from auth_utils import login_required
from helpers import success, error, paginate_params
from config import MODEL_CONTACT
 
users_bp = Blueprint("users", __name__, url_prefix="/api/users")
 
FIELDS = ["id", "name", "x_email", "x_bio", "x_location",
          "x_skills_offered", "x_skills_wanted",
          "x_rating", "x_total_sessions", "image_128"]
 
 
def list_users():
    """جلب قائمة كل المستخدمين — متاح بدون token"""
    page, limit, offset = paginate_params()
    limit = min(500, limit)
 
    domain = [["x_is_skillswap_user", "=", True], ["active", "=", True]]
    records = odoo_search_read(MODEL_CONTACT, domain,
                               fields=FIELDS, limit=limit, offset=offset,
                               order="name asc")
    return success({
        "users": [_fmt(u) for u in records],
        "page":  page,
        "limit": limit,
        "total": len(records),
    })
 
 
@users_bp.route("", methods=["GET"])
def get_users():
    return list_users()
 
 
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    records = odoo_search_read(MODEL_CONTACT,
                               [["id", "=", user_id],
                                ["x_is_skillswap_user", "=", True]],
                               fields=FIELDS, limit=1)
    if not records:
        return error("المستخدم مش موجود", 404)
    return success({"user": _fmt(records[0])})
 
 
@users_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    my_id = request.current_user["user_id"]
    if my_id != user_id:
        return error("مش مسموح تعدل بروفايل حد تاني", 403)
 
    data = request.get_json(silent=True) or {}
    update = {}
 
    if "name" in data and data["name"]:
        update["name"] = data["name"]
    if "bio" in data:
        update["x_bio"] = data["bio"]
    if "location" in data:
        update["x_location"] = data["location"]
    if "skills_offered" in data:
        offered = data["skills_offered"]
        update["x_skills_offered"] = ", ".join(offered) if isinstance(offered, list) else offered
    if "skills_wanted" in data:
        wanted = data["skills_wanted"]
        update["x_skills_wanted"] = ", ".join(wanted) if isinstance(wanted, list) else wanted
 
    if not update:
        return error("مفيش بيانات للتعديل")
 
    odoo_write(MODEL_CONTACT, [user_id], update)
 
    records = odoo_search_read(MODEL_CONTACT, [["id", "=", user_id]],
                               fields=FIELDS, limit=1)
    return success({"user": _fmt(records[0])}, "تم تعديل البروفايل")
 
 
@users_bp.route("/match", methods=["GET"])
@login_required
def match_users():
    my_id = request.current_user["user_id"]
    me = odoo_search_read(MODEL_CONTACT, [["id", "=", my_id]],
                          fields=FIELDS, limit=1)
    if not me:
        return error("مش لاقيينك", 404)
 
    my_wanted = [s.strip().lower() for s in (me[0].get("x_skills_wanted") or "").split(",") if s.strip()]
 
    all_users = odoo_search_read(MODEL_CONTACT,
                                 [["x_is_skillswap_user", "=", True],
                                  ["active", "=", True],
                                  ["id", "!=", my_id]],
                                 fields=FIELDS, limit=200)
 
    matches = []
    for u in all_users:
        offered = [s.strip().lower() for s in (u.get("x_skills_offered") or "").split(",") if s.strip()]
        common = set(my_wanted) & set(offered)
        if common:
            fmt = _fmt(u)
            fmt["match_score"] = len(common)
            fmt["matched_skills"] = list(common)
            matches.append(fmt)
 
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return success({"matches": matches[:20]})
 
 
def _fmt(u):
    offered_raw = u.get("x_skills_offered") or ""
    wanted_raw  = u.get("x_skills_wanted")  or ""
    name        = u.get("name", "")
    # صورة Odoo — image_128 هي base64، نحولها لـ data URL
    img_b64 = u.get("image_128")
    if img_b64 and isinstance(img_b64, str) and len(img_b64) > 10:
        avatar = f"data:image/png;base64,{img_b64}"
    else:
        # fallback: ui-avatars بالاسم
        import urllib.parse
        avatar = f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=B76E79&color=fff&size=128"
 
    return {
        "id":             u["id"],
        "name":           name,
        "email":          u.get("x_email", ""),
        "bio":            u.get("x_bio", ""),
        "location":       u.get("x_location", ""),
        "skills_offered": [s.strip() for s in offered_raw.split(",") if s.strip()],
        "skills_wanted":  [s.strip() for s in wanted_raw.split(",")  if s.strip()],
        "rating":         u.get("x_rating", 0.0),
        "total_sessions": u.get("x_total_sessions", 0),
        "avatar":         avatar,
    }
