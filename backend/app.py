#!/usr/bin/python3

'''

[user profile]:
- follow ?
- settings
- chat
- gmap


[api]:
[+] account:
- /api/create-account
- /api/update-account
- /api/delete-account
- /api/login
- /api/logout

[+] model:
- /api/recommend

'''


import jwt
import uuid       # can be implemented in more secure way
import mysql.connector
from os import getenv
from functools import wraps
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from recommender import TravelRecommender       # recommendation model
from werkzeug.security import generate_password_hash, check_password_hash


# init
app = Flask(__name__)
CORS(app)                                                               # browser pre-flight (OPTIONS)
load_dotenv()
app.config["JWT_SECRET"] = getenv("JWT_SECRET")
app.config["JWT_ALGORITHM"] = "HS256"                                   # symmetric
app.config["JWT_EXPIRATION_MINUTES"] = 120
recommender = TravelRecommender()


''' helping functions '''

# db conn
def get_db_connection():
    return mysql.connector.connect(host = "localhost", user = "user", password = "1234!", database = "travel")   # hardcode is shit TT (replace it by getenv())


def generate_token(user_id):
    jti = str(uuid.uuid4())

    payload = {
        "user_id": user_id,
        "jti": jti,
        "exp": datetime.utcnow() + timedelta(minutes = app.config["JWT_EXPIRATION_MINUTES"]),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm = app.config["JWT_ALGORITHM"])
    return token


# rate limit
limiter = Limiter(
    key_func = get_remote_address,
    default_limits = ["200 per day", "50 per hour"]
)


# decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or invalid"}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid authorization header"}), 401

        try:
            payload = jwt.decode(token, app.config["JWT_SECRET"], algorithms = [app.config["JWT_ALGORITHM"]])

            # JWT ID is used for blacklisting tokens
            jti = payload.get("jti")
            user_id = payload.get("user_id")

            if not jti or not user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM token_blacklist WHERE jti=%s LIMIT 1", (jti,))
            blacklisted = cursor.fetchone()

            cursor.close()
            conn.close()

            if blacklisted:
                return jsonify({"error": "Token revoked"}), 401

            request.user_id = user_id

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return f(*args, **kwargs)

    return decorated





''' ======== account creation ====================  '''


''' CRUD '''
@app.route("/api/create-account", methods = ["POST"])
@limiter.limit("30 per minute")
def create_account():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        required_fields = [
            "username", "password",
            "age", "budget",
            "beach", "trekking", "culture", "adventure",
            "travel_month", "destination_id"
        ]

        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": "Invalid request"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        # check username
        cursor.execute("SELECT user_id FROM users WHERE username=%s",(data["username"],))

        if cursor.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        # generate uuid
        user_id = str(uuid.uuid4()).replace("-", "")

        password_hash = generate_password_hash(data["password"])

        query = """
        INSERT INTO users
        (
            user_id,
            username,
            password_hash,
            age,
            budget,
            beach,
            trekking,
            culture,
            adventure,
            travel_month,
            destination_id
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            user_id,
            data["username"],
            password_hash,
            int(data["age"]),
            int(data["budget"]),
            int(data["beach"]),
            int(data["trekking"]),
            int(data["culture"]),
            int(data["adventure"]),
            int(data["travel_month"]),
            int(data["destination_id"])
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        token = generate_token(user_id)

        return jsonify({
            "message": "Account created",
            "token": token
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/update-account", methods = [ "PUT" ])
@token_required
def update_account():
    try:
        data = request.get_json()
        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE users
        SET age=%s, budget=%s, beach=%s, trekking=%s,
            culture=%s, adventure=%s,
            travel_month=%s, destination_id=%s
        WHERE user_id=%s
        """

        values = (
            data["age"],
            data["budget"],
            data["beach"],
            data["trekking"],
            data["culture"],
            data["adventure"],
            data["travel_month"],
            data["destination_id"],
            user_id
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Profile updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/delete-account", methods = [ "DELETE" ])
@token_required
def delete_account():
    try:
        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ratings WHERE user_id=%s", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Account deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/login",methods = [ "POST" ])
@limiter.limit("30 per minute")
def login():
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("SELECT * FROM users WHERE username=%s", (data["username"],))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not check_password_hash(user["password_hash"], data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_token(user["user_id"])

        return jsonify({
            "message": "Login successful",
            "token": token
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/logout", methods = [ "POST" ])
@token_required
def logout():
    try:
        auth_header = request.headers["Authorization"]
        token = auth_header.split(" ")[1]

        payload = jwt.decode(token, app.config["JWT_SECRET"], algorithms = [app.config["JWT_ALGORITHM"]])
        jti = payload["jti"]
        exp_timestamp = payload["exp"]

        expires_at = datetime.utcfromtimestamp(exp_timestamp)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO token_blacklist (jti, expires_at) VALUES (%s, %s)", (jti, expires_at))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Logout successful. Token revoked."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



''' to do '''
@app.route("/api/reset-passwd", methods = [ "POST" ])
def reset_passwd():
    pass





''' ========= group ===============   '''

''' CRUD '''
@app.route("/api/create-group", methods = [ "POST" ])
def create_group():
    pass


@app.route("/api/join-group", methods = [ "POST" ])
def join_group():
    pass


@app.route("/api/update-group", methods = [ "PUT" ])
def update_group():
    pass


@app.route("/api/delete-group", methods = [ "DELETE" ])
def delete_group():
    pass


# ========== model ==============

# recomend top n users
@app.route("/api/recommend", methods =[ "POST" ])
@limiter.limit("30 per minute")
@token_required
def recommend():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        user_id = request.user_id   # from jwt
        top_n = data.get("top_n", 5)

        # call model
        results = recommender.recommend(user_id = user_id, top_n = int(top_n)) or []

        if not results:
            return jsonify({"recommendations": []})

        return jsonify({ "user_id": user_id, "recommendations": results })

    except Exception as e:
        return jsonify({ "error" : str(e) }), 500




@app.route("/")
def home():
    return jsonify({ "message": "API server is running"})




# main
if __name__ == "__main__":
    app.run("0.0.0.0", port = 8080)