from flask import jsonify, request


def success(data=None, message="OK", status=200):
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    return jsonify(resp), status


def error(message="Error", status=400):
    return jsonify({"success": False, "error": message}), status


def paginate_params():
    page   = max(1, int(request.args.get("page", 1)))
    limit  = min(100, int(request.args.get("limit", 20)))
    offset = (page - 1) * limit
    return page, limit, offset


def required_fields(data, fields):
    return [f for f in fields if not data.get(f)]
