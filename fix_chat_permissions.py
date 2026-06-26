"""
سكريبت يصلح permissions للـ Chat model في Odoo
شغّليه مرة واحدة بس: python fix_chat_permissions.py
"""
import sys
sys.path.insert(0, '.')
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
import xmlrpc.client

print("🔌 جاري الاتصال بـ Odoo...")
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
if not uid:
    print("❌ فشل الاتصال")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
print(f"✅ اتصلنا (uid={uid})")

# جلب الـ model id بتاع x_skillswap.chat
model_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'ir.model', 'search', [[['model', '=', 'x_skillswap.chat']]])

if not model_ids:
    print("❌ موديل x_skillswap.chat مش موجود — شغّلي chat_setup.py الأول")
    sys.exit(1)

model_id = model_ids[0]
print(f"✅ لقينا الموديل id={model_id}")

# جلب group_id بتاع base.group_user (المستخدمين العاديين)
group_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'res.groups', 'search', [[['full_name', 'ilike', 'Internal User']]])

if not group_ids:
    group_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'res.groups', 'search', [[['full_name', 'ilike', 'Employee']]])

if not group_ids:
    # fallback: استخدم أي group موجود
    group_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'res.groups', 'search', [[]], {'limit': 1})

group_id = group_ids[0]
print(f"✅ Group id={group_id}")

# إضافة access rule
try:
    access_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'ir.model.access', 'create', [{
            'name':        'skillswap_chat_all_access',
            'model_id':    model_id,
            'group_id':    False,  # False = ينطبق على الكل بدون تقييد group
            'perm_read':   True,
            'perm_write':  True,
            'perm_create': True,
            'perm_unlink': True,
        }])
    print(f"✅ تم إضافة access rule id={access_id}")
except Exception as e:
    if 'already exists' in str(e) or 'unique' in str(e).lower():
        print("⚠️ الـ rule موجودة بالفعل")
    else:
        print(f"❌ خطأ: {e}")

# تأكيد
rules = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'ir.model.access', 'search_read',
    [[['model_id', '=', model_id]]],
    {'fields': ['name', 'perm_read', 'perm_write', 'perm_create']})

print(f"\n📋 الـ access rules الحالية للـ Chat model:")
for r in rules:
    print(f"   - {r['name']}: read={r['perm_read']}, write={r['perm_write']}, create={r['perm_create']}")

print("\n🎉 خلاص! جربي الشات دلوقتي.")
