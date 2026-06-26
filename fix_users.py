"""
سكريبت بيضيف x_is_skillswap_user = True
لكل الأشخاص الموجودين في Odoo
"""
import sys
sys.path.insert(0, '.')

from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
import xmlrpc.client

print("🔌 جاري الاتصال بـ Odoo...")
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
if not uid:
    print("❌ فشل الاتصال. تأكدي من config.py")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# جلب كل الأشخاص اللي مش عندهم الفلاج
print("🔍 جاري البحث عن الأشخاص...")
partners = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search_read',
    [[['x_is_skillswap_user', '=', False], ['active', '=', True]]],
    {'fields': ['id', 'name'], 'limit': 500}
)

if not partners:
    print("⚠️ مفيش أشخاص جدد للإضافة")
else:
    ids = [p['id'] for p in partners]
    print(f"✅ لقينا {len(ids)} شخص — جاري الإضافة...")
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'write',
        [ids, {'x_is_skillswap_user': True}]
    )
    for p in partners:
        print(f"   ✅ {p['name']}")
    print(f"\n🎉 تم! {len(ids)} شخص اتضافوا للموقع.")

# إجمالي المستخدمين
total = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search_count',
    [[['x_is_skillswap_user', '=', True]]]
)
print(f"📊 إجمالي المستخدمين في الموقع: {total}")
