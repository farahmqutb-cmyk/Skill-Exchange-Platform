"""
admin_links.py — دليل روابط الإدارة لنظام Skill Exchange Hub
شغّلي هذا الملف لعرض كل روابط الأدمن
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║         🌟 Skill Exchange Hub — روابط الإدارة               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📌 الـ Flask API (Backend)                                  ║
║  http://localhost:5000                                       ║
║                                                              ║
║  ✅ فحص صحة النظام:                                          ║
║  http://localhost:5000/api/health                           ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🔧 لوحة تحكم Odoo (الأدمن)                                 ║
║  http://localhost:8069/web                                   ║
║  المستخدم: farahmqutb@gmail.com                              ║
║                                                              ║
║  📋 إدارة طلبات التبادل (CRM Leads):                        ║
║  http://localhost:8069/odoo/crm                              ║
║                                                              ║
║  👥 إدارة المستخدمين (Contacts):                             ║
║  http://localhost:8069/odoo/contacts                         ║
║                                                              ║
║  📅 إدارة الجلسات (Calendar):                               ║
║  http://localhost:8069/odoo/calendar                         ║
║                                                              ║
║  📁 إدارة الملفات (Documents):                              ║
║  http://localhost:8069/odoo/documents                        ║
║                                                              ║
║  ⭐ إدارة التقييمات (Custom Model):                          ║
║  http://localhost:8069/odoo/x_skillswap.rating               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🔌 API Endpoints المتاحة                                    ║
║                                                              ║
║  POST   /api/auth/register        ← تسجيل مستخدم جديد       ║
║  POST   /api/auth/login           ← تسجيل دخول              ║
║  GET    /api/auth/me              ← بيانات المستخدم الحالي   ║
║                                                              ║
║  GET    /api/users                ← قائمة المستخدمين        ║
║  GET    /api/users/<id>           ← بروفايل مستخدم           ║
║  PUT    /api/users/<id>           ← تعديل البروفايل          ║
║  GET    /api/users/match          ← مطابقة المهارات          ║
║                                                              ║
║  POST   /api/requests             ← إرسال طلب تبادل         ║
║  GET    /api/requests             ← عرض الطلبات             ║
║  PUT    /api/requests/<id>/accept ← قبول طلب               ║
║  PUT    /api/requests/<id>/reject ← رفض طلب                ║
║  PUT    /api/requests/<id>/cancel ← إلغاء طلب              ║
║                                                              ║
║  POST   /api/sessions             ← حجز جلسة               ║
║  GET    /api/sessions             ← عرض الجلسات            ║
║  PUT    /api/sessions/<id>/complete ← إتمام جلسة           ║
║  PUT    /api/sessions/<id>/cancel   ← إلغاء جلسة           ║
║                                                              ║
║  POST   /api/ratings              ← إضافة تقييم             ║
║  GET    /api/ratings/<user_id>    ← عرض تقييمات مستخدم      ║
║                                                              ║
║  POST   /api/files/upload         ← رفع ملف                ║
║  GET    /api/files                ← عرض ملفات جلسة          ║
║  GET    /api/files/<id>/download  ← تحميل ملف              ║
║  DELETE /api/files/<id>           ← حذف ملف                ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🛠️ كيف الأدمن يضيف/يعدل مهارات؟                            ║
║                                                              ║
║  1. افتح Odoo: http://localhost:8069/odoo/contacts           ║
║  2. ابحث عن المستخدم بالاسم                                  ║
║  3. افتح البروفايل                                           ║
║  4. عدّل حقل "Skills Offered" أو "Skills Wanted"            ║
║  5. احفظ التغييرات                                          ║
║                                                              ║
║  أو عن طريق الـ API:                                         ║
║  PUT /api/users/<id>                                         ║
║  Body: {"skills_offered": ["Python", "Web Dev"]}             ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  📊 إعداد الإيميل (في email_notify.py):                     ║
║  1. فعّلي 2-Step Verification في Gmail                       ║
║  2. اعمل App Password من:                                    ║
║     myaccount.google.com/apppasswords                        ║
║  3. ضعي الإيميل والـ Password في:                            ║
║     SMTP_EMAIL = "skillexchangehub@gmail.com"                ║
║     SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"                    ║
╚══════════════════════════════════════════════════════════════╝
""")
