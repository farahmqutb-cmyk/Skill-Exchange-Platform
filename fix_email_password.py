"""
سكريبت بيصلح الـ users ويحط ليهم email و password
"""
import sys, random
sys.path.insert(0, '.')

from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
import xmlrpc.client
from werkzeug.security import generate_password_hash

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# الـ password الافتراضي لكل الـ users
DEFAULT_PASSWORD = "skillswap123"
password_hash = generate_password_hash(DEFAULT_PASSWORD)

# جلب كل الـ users
partners = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search_read',
    [[['x_is_skillswap_user', '=', True]]],
    {'fields': ['id', 'name', 'x_email', 'x_password_hash'], 'limit': 500}
)

print(f"🔍 لقينا {len(partners)} شخص — جاري إضافة email و password...")
print(f"🔑 الـ password الافتراضي: {DEFAULT_PASSWORD}")
print()

fixed = 0
for p in partners:
    name = p.get('name', f"user_{p['id']}")
    
    # عمل email من الاسم
    email_name = name.lower().replace(' ', '.').replace(',', '').replace("'", '')
    email = f"{email_name}_{p['id']}@skillswap.com"

    # تحديث email و password بس اللي مالهومش
    update = {}
    if not p.get('x_email'):
        update['x_email'] = email
    if not p.get('x_password_hash'):
        update['x_password_hash'] = password_hash

    if update:
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'write',
            [[p['id']], update]
        )
        print(f"   ✅ {name} → {email}")
        fixed += 1

print()
print(f"🎉 تم إصلاح {fixed} شخص!")
print()
print("=" * 50)
print("📋 تقدر تعمل login بأي email من فوق")
print(f"🔑 والـ password هو: {DEFAULT_PASSWORD}")
print("=" * 50)
