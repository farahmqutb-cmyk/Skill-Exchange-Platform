"""
سكريبت بيضيف موديل الـ Chat في Odoo
شغليه مرة واحدة بس
"""
import sys
sys.path.insert(0, '.')
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
import xmlrpc.client

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

print("💬 إنشاء موديل الـ Chat...")

# إنشاء الموديل
try:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.model', 'create', [{
        'name': 'SkillSwap Chat',
        'model': 'x_skillswap.chat',
        'field_id': [
            [0, 0, {'name': 'x_sender_id',   'field_description': 'Sender',   'ttype': 'integer'}],
            [0, 0, {'name': 'x_receiver_id', 'field_description': 'Receiver', 'ttype': 'integer'}],
            [0, 0, {'name': 'x_message',     'field_description': 'Message',  'ttype': 'text'}],
            [0, 0, {'name': 'x_is_read',     'field_description': 'Is Read',  'ttype': 'boolean'}],
        ]
    }])
    print("✅ تم إنشاء موديل x_skillswap.chat")
except Exception as e:
    print(f"⚠️ الموديل موجود بالفعل أو: {e}")

print("\n🎉 Chat setup complete!")
