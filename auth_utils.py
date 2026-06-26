import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import SECRET_KEY, JWT_EXPIRY_HOURS


def hash_password(plain):
    return generate_password_hash(plain)


def verify_password(plain, hashed):
    return check_password_hash(hashed, plain)


def generate_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email":   email,
        "exp":     datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "يجب تسجيل الدخول أولاً"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "انتهت صلاحية الجلسة، سجلي الدخول مجدداً"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token غير صالح"}), 401
        return f(*args, **kwargs)
    return decorated
