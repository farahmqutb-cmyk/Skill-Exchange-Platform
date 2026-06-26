"""
======================================================
  Odoo Custom Fields Setup  – skillswap_setup.py
  شغّل هذا الملف مرة واحدة لإنشاء الحقول المخصصة
  في Odoo عبر XML-RPC
======================================================

Usage:
    python skillswap_setup.py

ملاحظة: يجب أن يكون مستخدم Odoo لديه صلاحية Technical/Administrator
"""

import xmlrpc.client
import sys
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid    = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
if not uid:
    print("❌ Authentication failed. Check config.py")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def create_field(model, fname, ftype, fstring, extra=None):
    """Create a custom field if it doesn't exist"""
    existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        "ir.model.fields", "search",
        [[["model", "=", model], ["name", "=", fname]]])
    if existing:
        print(f"  ✓ {fname} already exists")
        return
    vals = {"model_id": _get_model_id(model),
            "name": fname, "field_description": fstring,
            "ttype": ftype, "store": True}
    if extra:
        vals.update(extra)
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "ir.model.fields", "create", [vals])
    print(f"  ✅ Created {fname}")

def _get_model_id(model_name):
    ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        "ir.model", "search", [[["model", "=", model_name]]])
    return ids[0]

def create_custom_model(model_name, description):
    existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        "ir.model", "search", [[["model", "=", model_name]]])
    if existing:
        print(f"  ✓ Model {model_name} already exists")
        return
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "ir.model", "create", [{
        "name": description, "model": model_name, "state": "manual"
    }])
    print(f"  ✅ Created model {model_name}")


print("\n🔧 Setting up SkillSwap custom fields in Odoo...\n")

# ══════════════════════════════════════════════════════
# 1. res.partner  (Users)
# ══════════════════════════════════════════════════════
print("📌 res.partner (Users)")
create_field("res.partner", "x_email",              "char",    "SkillSwap Email")
create_field("res.partner", "x_password_hash",      "char",    "Password Hash")
create_field("res.partner", "x_bio",                "text",    "Bio")
create_field("res.partner", "x_location",           "char",    "Location")
create_field("res.partner", "x_skills_offered",     "char",    "Skills Offered")
create_field("res.partner", "x_skills_wanted",      "char",    "Skills Wanted")
create_field("res.partner", "x_rating",             "float",   "Rating")
create_field("res.partner", "x_total_sessions",     "integer", "Total Sessions")
create_field("res.partner", "x_is_skillswap_user",  "boolean", "Is SkillSwap User")

# ══════════════════════════════════════════════════════
# 2. crm.lead  (Exchange Requests)
# ══════════════════════════════════════════════════════
print("\n📌 crm.lead (Exchange Requests)")
create_field("crm.lead", "x_sender_id",     "integer", "Sender ID")
create_field("crm.lead", "x_receiver_id",   "integer", "Receiver ID")
create_field("crm.lead", "x_offered_skill", "char",    "Offered Skill")
create_field("crm.lead", "x_wanted_skill",  "char",    "Wanted Skill")
create_field("crm.lead", "x_message",       "text",    "Message")
create_field("crm.lead", "x_status",        "char",    "SkillSwap Status")

# ══════════════════════════════════════════════════════
# 3. calendar.event  (Sessions)
# ══════════════════════════════════════════════════════
print("\n📌 calendar.event (Sessions)")
create_field("calendar.event", "x_request_id",    "integer", "Exchange Request ID")
create_field("calendar.event", "x_teacher_id",    "integer", "Teacher ID")
create_field("calendar.event", "x_learner_id",    "integer", "Learner ID")
create_field("calendar.event", "x_skill_name",    "char",    "Skill Name")
create_field("calendar.event", "x_duration_min",  "integer", "Duration (min)")
create_field("calendar.event", "x_location_type", "char",    "Location Type")
create_field("calendar.event", "x_meet_link",     "char",    "Meeting Link")
create_field("calendar.event", "x_address",       "char",    "Address")
create_field("calendar.event", "x_status",        "char",    "SkillSwap Status")

# ══════════════════════════════════════════════════════
# 4. documents.document  (Files)
# ══════════════════════════════════════════════════════
print("\n📌 documents.document (Files)")
try:
    create_field("documents.document", "x_session_id",  "integer", "Session ID")
    create_field("documents.document", "x_uploader_id", "integer", "Uploader ID")
    create_field("documents.document", "x_file_path",   "char",    "Local File Path")
except Exception as e:
    print(f"  ⚠️  documents.document not available ({e})")
    print("     Make sure the 'Documents' module is installed in Odoo")

# ══════════════════════════════════════════════════════
# 5. Custom model: x_skillswap.rating  (Ratings)
# ══════════════════════════════════════════════════════
print("\n📌 x_skillswap.rating (Ratings - Custom Model)")
create_custom_model("x_skillswap.rating", "SkillSwap Rating")
create_field("x_skillswap.rating", "x_rater_id",   "integer", "Rater ID")
create_field("x_skillswap.rating", "x_ratee_id",   "integer", "Ratee ID")
create_field("x_skillswap.rating", "x_session_id", "integer", "Session ID")
create_field("x_skillswap.rating", "x_score",      "float",   "Score")
create_field("x_skillswap.rating", "x_comment",    "text",    "Comment")

print("\n✅ Setup complete! You can now run: python app.py\n")
