import xmlrpc.client

ODOO_URL      = "http://localhost:8069"
ODOO_DB       = "Skill_Exchange"
ODOO_USERNAME = "farahmqutb@gmail.com"
ODOO_PASSWORD = "53295245Farah"

# اتصال
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid    = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# جيب كل المستخدمين المسجلين في المنصة
users = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    "res.partner", "search_read",
    [[ ["x_is_skillswap_user", "=", True] ]],
    {"fields": ["id", "name", "x_email", "x_skills_offered", "x_skills_wanted", "x_rating"]}
)

print(f"\n{'='*60}")
print(f"  إجمالي المستخدمين: {len(users)}")
print(f"{'='*60}\n")

for u in users:
    print(f"ID:       {u['id']}")
    print(f"الاسم:    {u['name']}")
    print(f"الإيميل:  {u.get('x_email', '---')}")
    print(f"يعلّم:    {u.get('x_skills_offered', '---')}")
    print(f"يتعلم:    {u.get('x_skills_wanted', '---')}")
    print(f"التقييم:  {u.get('x_rating', 0)}")
    print(f"{'-'*40}")
