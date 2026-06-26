from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_create
from auth_utils import hash_password, verify_password, generate_token, login_required
from helpers import success, error, required_fields
from config import MODEL_CONTACT

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

FIELDS = ["id", "name", "x_email", "x_password_hash",
          "x_rating", "x_total_sessions",
          "x_bio", "x_location",
          "x_skills_offered", "x_skills_wanted"]


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    missing = required_fields(data, ["name", "email", "password"])
    if missing:
        return error(f"حقول ناقصة: {', '.join(missing)}")

    existing = odoo_search_read(MODEL_CONTACT,
                                [["x_email", "=", data["email"]],
                                 ["x_is_skillswap_user", "=", True]],
                                fields=["id"], limit=1)
    if existing:
        return error("الإيميل ده مسجل قبل كده", 409)

    partner_id = odoo_create(MODEL_CONTACT, {
        "name":               data["name"],
        "email":              data["email"],
        "x_email":            data["email"],
        "x_password_hash":    hash_password(data["password"]),
        "x_bio":              data.get("bio", ""),
        "x_location":         data.get("location", ""),
        "x_skills_offered":   data.get("skills_offered", ""),
        "x_skills_wanted":    data.get("skills_wanted", ""),
        "x_rating":           0.0,
        "x_total_sessions":   0,
        "x_is_skillswap_user": True,
    })

    token = generate_token(partner_id, data["email"])
    return success({"token": token, "user_id": partner_id}, "تم التسجيل بنجاح", 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    missing = required_fields(data, ["email", "password"])
    if missing:
        return error(f"حقول ناقصة: {', '.join(missing)}")

    # بحث بـ x_email أولاً
    users = odoo_search_read(MODEL_CONTACT,
                             [["x_email", "=", data["email"]],
                              ["x_is_skillswap_user", "=", True]],
                             fields=FIELDS, limit=1)

    # لو مش لاقيين، نبحث بـ email الأصلي في Odoo
    if not users:
        users = odoo_search_read(MODEL_CONTACT,
                                 [["email", "=", data["email"]],
                                  ["x_is_skillswap_user", "=", True]],
                                 fields=FIELDS, limit=1)

    if not users:
        return error("الإيميل أو كلمة المرور غلط", 401)

    user = users[0]

    # التحقق من الباسوورد
    stored_hash = user.get("x_password_hash")
    if not stored_hash:
        return error("الحساب ده مش مسجل بكلمة مرور، جربي Sign Up", 401)

    if not verify_password(data["password"], stored_hash):
        return error("الإيميل أو كلمة المرور غلط", 401)

    email = user.get("x_email") or data["email"]
    token = generate_token(user["id"], email)
    return success({"token": token, "user": _fmt(user)}, "تم تسجيل الدخول")


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    user_id = request.current_user["user_id"]
    users = odoo_search_read(MODEL_CONTACT, [["id", "=", user_id]],
                             fields=["id", "name", "x_email", "x_rating",
                                     "x_total_sessions", "x_bio", "x_location",
                                     "x_skills_offered", "x_skills_wanted"],
                             limit=1)
    if not users:
        return error("مش لاقيين المستخدم", 404)
    return success(_fmt(users[0]))


def _fmt(u):
    return {
        "id":             u["id"],
        "name":           u["name"],
        "email":          u.get("x_email", ""),
        "bio":            u.get("x_bio", ""),
        "location":       u.get("x_location", ""),
        "skills_offered": [s.strip() for s in (u.get("x_skills_offered") or "").split(",") if s.strip()],
        "skills_wanted":  [s.strip() for s in (u.get("x_skills_wanted")  or "").split(",") if s.strip()],
        "rating":         u.get("x_rating", 0.0),
        "total_sessions": u.get("x_total_sessions", 0),
    }
