from flask import jsonify, request
import jwt
from functools import wraps

from settings import secret

def custom_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
            authorization = token.split(" ")
            if authorization[0] == "Bearer":
                auth = ""
                try:
                    auth = jwt.decode(authorization[1], secret)
                    kwargs['auth'] = auth
                except:
                    return jsonify({"status": "Failed", "message": "Unauthorized"}), 401
                return f(*args, **kwargs)
            return jsonify({"status": "Failed", "message": "Unauthorized"}), 401
        else:
            return jsonify({"status": "Failed", "message": "Unauthorized"}), 401
    return decorated

    