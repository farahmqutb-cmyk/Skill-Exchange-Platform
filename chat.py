from flask import Blueprint, request
from odoo_client import odoo_search_read, odoo_create
from auth_utils import login_required
from helpers import success, error
from config import MODEL_CONTACT

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

MODEL_CHAT = "x_skillswap.chat"

@chat_bp.route("/send", methods=["POST"])
@login_required
def send_message():
    data = request.get_json(silent=True) or {}
    receiver_id = data.get("receiver_id")
    message     = data.get("message", "").strip()

    if not receiver_id or not message:
        return error("receiver_id والرسالة مطلوبين")

    sender_id = request.current_user["user_id"]
    if sender_id == int(receiver_id):
        return error("مينفعش تبعت رسالة لنفسك")

    msg_id = odoo_create(MODEL_CHAT, {
        "x_sender_id":   sender_id,
        "x_receiver_id": int(receiver_id),
        "x_message":     message,
        "x_is_read":     False,
        "name":          f"msg_{sender_id}_{receiver_id}",
    })
    return success({"message_id": msg_id}, "تم إرسال الرسالة", 201)


@chat_bp.route("/messages/<int:other_user_id>", methods=["GET"])
@login_required
def get_messages(other_user_id):
    my_id = request.current_user["user_id"]
    since = request.args.get("since", "")  # للتحديث التدريجي

    domain = [
        "|",
        "&", ["x_sender_id", "=", my_id],   ["x_receiver_id", "=", other_user_id],
        "&", ["x_sender_id", "=", other_user_id], ["x_receiver_id", "=", my_id],
    ]
    if since:
        domain.append(["write_date", ">", since])

    msgs = odoo_search_read(MODEL_CHAT, domain,
                            fields=["id", "x_sender_id", "x_receiver_id",
                                    "x_message", "x_is_read", "create_date"],
                            limit=100, order="create_date asc")

    # تحديد الرسائل المستلمة كـ مقروءة
    unread_ids = [m["id"] for m in msgs
                  if m["x_receiver_id"] == my_id and not m["x_is_read"]]
    if unread_ids:
        from odoo_client import odoo_write
        odoo_write(MODEL_CHAT, unread_ids, {"x_is_read": True})

    return success({"messages": [_fmt(m, my_id) for m in msgs]})


@chat_bp.route("/conversations", methods=["GET"])
@login_required
def get_conversations():
    """قائمة المحادثات بتاعة المستخدم"""
    my_id = request.current_user["user_id"]

    msgs = odoo_search_read(MODEL_CHAT,
                            ["|", ["x_sender_id", "=", my_id],
                                  ["x_receiver_id", "=", my_id]],
                            fields=["id", "x_sender_id", "x_receiver_id",
                                    "x_message", "x_is_read", "create_date"],
                            limit=500, order="create_date desc")

    # تجميع المحادثات حسب الشخص التاني
    seen = {}
    for m in msgs:
        other = m["x_receiver_id"] if m["x_sender_id"] == my_id else m["x_sender_id"]
        if other not in seen:
            seen[other] = m

    # جلب أسماء الأشخاص
    if seen:
        partners = odoo_search_read(MODEL_CONTACT,
                                    [["id", "in", list(seen.keys())]],
                                    fields=["id", "name"], limit=100)
        names = {p["id"]: p["name"] for p in partners}
    else:
        names = {}

    convs = []
    for other_id, last_msg in seen.items():
        unread = sum(1 for m in msgs
                     if m["x_sender_id"] == other_id
                     and m["x_receiver_id"] == my_id
                     and not m["x_is_read"])
        convs.append({
            "user_id":      other_id,
            "user_name":    names.get(other_id, "Unknown"),
            "last_message": last_msg["x_message"],
            "last_date":    last_msg["create_date"],
            "unread":       unread,
        })

    convs.sort(key=lambda x: x["last_date"], reverse=True)
    return success({"conversations": convs})


def _fmt(m, my_id):
    return {
        "id":          m["id"],
        "sender_id":   m["x_sender_id"],
        "receiver_id": m["x_receiver_id"],
        "message":     m["x_message"],
        "is_mine":     m["x_sender_id"] == my_id,
        "is_read":     m["x_is_read"],
        "created_at":  m["create_date"],
    }
