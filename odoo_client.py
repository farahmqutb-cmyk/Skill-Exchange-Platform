import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


def get_uid():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise ConnectionError("فشل الاتصال بـ Odoo – تحققي من config.py")
    return uid


def get_models():
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def odoo_search_read(model, domain=None, fields=None, limit=100, offset=0, order=None):
    uid    = get_uid()
    models = get_models()
    kwargs = {"limit": limit, "offset": offset}
    if fields: kwargs["fields"] = fields
    if order:  kwargs["order"]  = order
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                             model, "search_read", [domain or []], kwargs)


def odoo_create(model, values):
    uid    = get_uid()
    models = get_models()
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                             model, "create", [values])


def odoo_write(model, ids, values):
    uid    = get_uid()
    models = get_models()
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                             model, "write", [ids, values])


def odoo_unlink(model, ids):
    uid    = get_uid()
    models = get_models()
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                             model, "unlink", [ids])
