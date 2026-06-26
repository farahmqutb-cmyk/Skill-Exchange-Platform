import os

# ══ غيري البيانات دي بتاعت Odoo ══
ODOO_URL      = os.getenv("ODOO_URL",      "http://localhost:8069")
ODOO_DB       = os.getenv("ODOO_DB",       "Skill_Exchange")
ODOO_USERNAME = "farahmqutb@gmail.com"
ODOO_PASSWORD = "53295245Farah"

# ══ Flask ══
SECRET_KEY  = os.getenv("SECRET_KEY", "skillswap-secret-2025")
DEBUG       = True

# ══ JWT ══
JWT_EXPIRY_HOURS = 24

# ══ Upload ══
UPLOAD_FOLDER  = "./uploads"
MAX_CONTENT_MB = 10
ALLOWED_EXT    = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "ppt", "pptx", "zip"}

# ══ Odoo Models ══
MODEL_CONTACT  = "res.partner"
MODEL_CRM_LEAD = "crm.lead"
MODEL_CALENDAR = "calendar.event"
MODEL_DOCUMENT = "documents.document"
RATING_MODEL   = "x_skillswap.rating"
