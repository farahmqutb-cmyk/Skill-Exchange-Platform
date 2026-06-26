import os, base64, uuid
from flask import Blueprint, request, send_file
from odoo_client import odoo_search_read, odoo_create, odoo_unlink
from auth_utils import login_required
from helpers import success, error
from config import MODEL_DOCUMENT, MODEL_CALENDAR, UPLOAD_FOLDER, MAX_CONTENT_MB, ALLOWED_EXT

files_bp = Blueprint("files", __name__, url_prefix="/api/files")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FIELDS = ["id", "name", "x_session_id", "x_uploader_id",
          "x_file_path", "mimetype", "file_size", "create_date"]


@files_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    my_id      = request.current_user["user_id"]
    session_id = request.form.get("session_id")
    if not session_id:
        return error("session_id مطلوب")
    if "file" not in request.files:
        return error("مفيش ملف في الطلب")

    file = request.files["file"]
    if not file.filename:
        return error("اسم الملف فاضي")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        return error(f"نوع الملف '{ext}' مش مسموح")

    sess = odoo_search_read(MODEL_CALENDAR, [["id", "=", int(session_id)]],
                            fields=["id", "x_teacher_id", "x_learner_id"], limit=1)
    if not sess:
        return error("الجلسة مش موجودة", 404)
    s = sess[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)

    safe_name  = f"{uuid.uuid4().hex}.{ext}"
    local_path = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(local_path)
    file_size  = os.path.getsize(local_path)

    if file_size > MAX_CONTENT_MB * 1024 * 1024:
        os.remove(local_path)
        return error(f"الملف كبير، الحد الأقصى {MAX_CONTENT_MB} MB")

    with open(local_path, "rb") as f:
        raw = base64.b64encode(f.read()).decode()

    doc_id = odoo_create(MODEL_DOCUMENT, {
        "name":          file.filename,
        "x_session_id":  int(session_id),
        "x_uploader_id": my_id,
        "x_file_path":   local_path,
        "mimetype":      file.mimetype or "application/octet-stream",
        "file_size":     file_size,
        "datas":         raw,
    })
    return success({"file_id": doc_id, "filename": file.filename}, "تم رفع الملف", 201)


@files_bp.route("", methods=["GET"])
@login_required
def list_files():
    my_id      = request.current_user["user_id"]
    session_id = request.args.get("session_id")
    if not session_id:
        return error("session_id مطلوب")

    sess = odoo_search_read(MODEL_CALENDAR, [["id", "=", int(session_id)]],
                            fields=["id", "x_teacher_id", "x_learner_id"], limit=1)
    if not sess:
        return error("الجلسة مش موجودة", 404)
    s = sess[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)

    docs = odoo_search_read(MODEL_DOCUMENT, [["x_session_id", "=", int(session_id)]],
                            fields=FIELDS, limit=100, order="create_date desc")
    return success({"files": [_fmt(d) for d in docs]})


@files_bp.route("/<int:file_id>/download", methods=["GET"])
@login_required
def download_file(file_id):
    my_id = request.current_user["user_id"]
    docs  = odoo_search_read(MODEL_DOCUMENT, [["id", "=", file_id]], fields=FIELDS, limit=1)
    if not docs:
        return error("الملف مش موجود", 404)
    d = docs[0]

    sess = odoo_search_read(MODEL_CALENDAR, [["id", "=", d["x_session_id"]]],
                            fields=["x_teacher_id", "x_learner_id"], limit=1)
    if not sess:
        return error("الجلسة مش موجودة", 404)
    s = sess[0]
    if s["x_teacher_id"] != my_id and s["x_learner_id"] != my_id:
        return error("مش مسموح", 403)

    local_path = d.get("x_file_path", "")
    if not local_path or not os.path.exists(local_path):
        return error("الملف مش موجود على السيرفر", 404)

    return send_file(local_path, as_attachment=True, download_name=d["name"])


@files_bp.route("/<int:file_id>", methods=["DELETE"])
@login_required
def delete_file(file_id):
    my_id = request.current_user["user_id"]
    docs  = odoo_search_read(MODEL_DOCUMENT, [["id", "=", file_id]], fields=FIELDS, limit=1)
    if not docs:
        return error("الملف مش موجود", 404)
    if docs[0]["x_uploader_id"] != my_id:
        return error("بس اللي رفع الملف يقدر يحذفه", 403)

    local_path = docs[0].get("x_file_path", "")
    if local_path and os.path.exists(local_path):
        os.remove(local_path)

    odoo_unlink(MODEL_DOCUMENT, [file_id])
    return success(message="تم حذف الملف")


def _fmt(d):
    return {
        "id":          d["id"],
        "name":        d.get("name", ""),
        "session_id":  d.get("x_session_id"),
        "uploader_id": d.get("x_uploader_id"),
        "mimetype":    d.get("mimetype", ""),
        "file_size":   d.get("file_size", 0),
        "created_at":  d.get("create_date", ""),
    }
