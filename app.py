from datetime import timedelta
import base64

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

# ================================
# In-memory user store
# ================================
users = {
    "admin": {
        "password": "admin123",
        "role": "admin",
    },
    "john": {
        "password": "john123",
        "role": "user",
    },
}


def _json_error(message: str, status: int):
    return jsonify({"error": message}), status


# ================================
# JWT error handlers (consistent JSON)
# ================================
@jwt.unauthorized_loader
def _missing_token_callback(err):
    return _json_error("Missing or invalid Authorization header", 401)


@jwt.invalid_token_loader
def _invalid_token_callback(err):
    return _json_error("Invalid token", 401)


@jwt.expired_token_loader
def _expired_token_callback(jwt_header, jwt_payload):
    return _json_error("Token has expired", 401)


# ================================
# 1. BASIC AUTHENTICATION
# ================================
@app.route("/basic-protected")
def basic_protected():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return _json_error("Missing Basic Auth", 401)

    user = users.get(auth.username)

    if user and user["password"] == auth.password:
        return jsonify({"message": f"Basic Auth Success. Welcome {auth.username}!"})

    return _json_error("Invalid credentials", 401)


# ================================
# 2. SIMPLE TOKEN AUTHENTICATION
# ================================

# Generate simple token (not JWT)
@app.route("/token-login", methods=["POST"])
def token_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return _json_error("username and password are required", 400)

    user = users.get(username)

    if user and user["password"] == password:
        token = base64.b64encode(username.encode()).decode()
        return jsonify({"token": token})

    return _json_error("Invalid credentials", 401)


@app.route("/token-protected")
def token_protected():
    token = request.headers.get("x-auth-token")

    if not token:
        return _json_error("Missing Token", 401)

    try:
        username = base64.b64decode(token).decode()
        if username in users:
            return jsonify({"message": f"Token Auth Success. Welcome {username}!"})
    except Exception:
        pass

    return _json_error("Invalid Token", 401)


# ================================
# 3. JWT AUTHENTICATION
# ================================

@app.route("/jwt-login", methods=["POST"])
def jwt_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return _json_error("username and password are required", 400)

    user = users.get(username)

    if user and user["password"] == password:
        token = create_access_token(
            identity=username,
            additional_claims={"role": user.get("role")},
        )
        return jsonify({"access_token": token})

    return _json_error("Invalid credentials", 401)


@app.route("/jwt-protected")
@jwt_required()
def jwt_protected():
    current_user = get_jwt_identity()
    claims = get_jwt()

    return jsonify(
        {
            "message": f"JWT Auth Success. Welcome {current_user}!",
            "identity": current_user,
            "role": claims.get("role"),
        }
    )


@app.route("/jwt-admin")
@jwt_required()
def jwt_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return _json_error("Admins only", 403)

    current_user = get_jwt_identity()
    return jsonify({"message": f"Admin access granted for {current_user}"})


# ================================
# ROOT ROUTE
# ================================
@app.route("/")
def home():
    return jsonify(
        {
            "message": "Authentication Experiment Running",
            "routes": [
                "/basic-protected (Basic Auth)",
                "/token-login (POST)",
                "/token-protected (x-auth-token header)",
                "/jwt-login (POST)",
                "/jwt-protected (Bearer Token)",
                "/jwt-admin (Bearer Token + admin role)",
            ],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
