from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import SECRET_KEY, DEBUG, UPLOAD_FOLDER, MAX_CONTENT_MB
import os

from auth import auth_bp
from users import users_bp
from exchange_requests import requests_bp
from sessions import sessions_bp
from files import files_bp
from ratings import ratings_bp
from chat import chat_bp

def create_app():
    app = Flask(__name__, static_folder='.', static_url_path='')
    
    # إعدادات CORS للسماح للملف المحلي بالتواصل مع الـ API
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024

    # إنشاء مجلد الرفع إذا لم يكن موجوداً
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # إضافة رؤوس CORS لجميع الردود
    @app.after_request
    def add_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            return jsonify({}), 200

    # تسجيل الـ Blueprints
    app.register_blueprint(auth_bp)           # /api/auth/*
    app.register_blueprint(users_bp)          # /api/users/*
    app.register_blueprint(requests_bp)       # /api/requests/*
    app.register_blueprint(sessions_bp)       # /api/sessions/*
    app.register_blueprint(files_bp)          # /api/files/*
    app.register_blueprint(ratings_bp)        # /api/ratings/*
    app.register_blueprint(chat_bp)           # /api/chat/*

    # ✅ Endpoint لفحص صحة النظام
    @app.route("/api/health", methods=["GET"])
    def health():
        try:
            from odoo_client import get_uid
            uid = get_uid()
            odoo_status = f"connected (uid={uid})"
        except Exception as e:
            odoo_status = f"error: {str(e)}"
        return jsonify({"status": "ok", "service": "SkillSwap API", "odoo": odoo_status})

    # ✅ **الصفحة الرئيسية - تعرض ملف index_full.html مباشرة**
    @app.route("/")
    def serve_index():
        return send_from_directory('.', 'index_full.html')

    # ✅ **خدمة الملفات الثابتة (CSS, JS, Images)**
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(path):
            return send_from_directory('.', path)
        return jsonify({"error": "File not found"}), 404

    # ✅ **Endpoint للمستخدمين (تأكد من وجوده)**
    @app.route("/api/users", methods=["GET"])
    def get_users_list():
        """جلب قائمة المستخدمين - متاح للجميع"""
        from users import list_users
        return list_users()

    # ✅ **معالجة الأخطاء**
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": str(e)}), 500

    return app

# إنشاء التطبيق
app = create_app()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 Skill Exchange Hub - Server Running")
    print("="*60)
    print(f"  📍 Local:    http://localhost:5000")
    print(f"  📍 API:      http://localhost:5000/api/")
    print(f"  📍 Health:   http://localhost:5000/api/health")
    print(f"  📍 Users:    http://localhost:5000/api/users")
    print("="*60)
    print("  ⭐ Press CTRL+C to stop the server\n")
    
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)