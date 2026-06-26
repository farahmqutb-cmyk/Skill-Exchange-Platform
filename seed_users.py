"""
سكريبت بيضيف بيانات وهمية لكل الأشخاص في Odoo
"""
import sys, random
sys.path.insert(0, '.')

from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
import xmlrpc.client

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

SKILLS = [
    "Web Development", "Python", "JavaScript", "UI/UX Design", "Graphic Design",
    "Photography", "Video Editing", "English", "Arabic", "French", "Spanish",
    "Digital Marketing", "SEO", "Content Writing", "Data Analysis", "Machine Learning",
    "Flutter", "React", "Node.js", "Figma", "Adobe Photoshop", "Music", "Guitar",
    "Piano", "Cooking", "Baking", "Fitness Training", "Yoga", "Public Speaking",
    "Project Management", "Excel", "PowerPoint", "3D Design", "AutoCAD",
]

LOCATIONS = [
    "Cairo, Egypt", "Alexandria, Egypt", "Giza, Egypt",
    "Dubai, UAE", "Riyadh, Saudi Arabia", "Amman, Jordan",
    "Beirut, Lebanon", "Tunis, Tunisia", "Casablanca, Morocco",
]

BIOS = [
    "Passionate about sharing knowledge and learning new skills.",
    "Professional with years of experience, happy to teach and learn.",
    "Love connecting with people and exchanging expertise.",
    "Always looking to grow and help others grow too.",
    "Experienced professional seeking skill exchange opportunities.",
    "Enthusiastic learner and dedicated teacher.",
    "Building connections through the power of skill sharing.",
    "Expert in my field, eager to learn something new every day.",
]

# جلب كل الأشخاص اللي مالهمش bio
partners = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search_read',
    [[['x_is_skillswap_user', '=', True]]],
    {'fields': ['id', 'name', 'x_bio', 'x_skills_offered'], 'limit': 500}
)

print(f"🔍 لقينا {len(partners)} شخص — جاري إضافة البيانات...")

for p in partners:
    # بس اللي مالهمش بيانات
    if p.get('x_bio') and p.get('x_skills_offered'):
        continue

    offered = random.sample(SKILLS, random.randint(2, 4))
    wanted  = random.sample([s for s in SKILLS if s not in offered], random.randint(2, 3))

    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'write',
        [[p['id']], {
            'x_bio':            random.choice(BIOS),
            'x_location':       random.choice(LOCATIONS),
            'x_skills_offered': ", ".join(offered),
            'x_skills_wanted':  ", ".join(wanted),
            'x_rating':         round(random.uniform(3.5, 5.0), 1),
            'x_total_sessions': random.randint(0, 20),
        }]
    )
    print(f"   ✅ {p['name']} ← {', '.join(offered)}")

print(f"\n🎉 تم! كل الأشخاص عندهم بيانات دلوقتي.")
