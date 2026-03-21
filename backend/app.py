#!/usr/bin/python3

'''

[user profile]:
- follow ?
- gmap


[api]:
[+] account:
- /api/create-account
- /api/update-account
- /api/delete-account
- /api/login
- /api/logout

[+] group:
- /api/groups
- /api/create-group
- /api/join-group
- /api/update-group
- /api/delete-group
- /api/group/allow
- /api/group/reject
- /api/group/leave
- /api/group/requests

[+] chat:
- /api/chat/send
- /api/chat/messages
- /api/chat/unread
- /api/chat/read
- /api/group/chat/send
- /api/group/chat

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
def get_db_connection(retries = 5):
    host = getenv("DB_HOST")
    user = getenv("DB_USER")
    password = getenv("DB_PASSWD")
    database = getenv("DB")

    # retry logic
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(host = host, user = user, password = password, database = database)
            return conn
        except Exception as e:
            sleep(5)

    raise Exception("Cannot connect to Database after several retries")


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
    app = app,                                      # forgot to init lol :(
    key_func = get_remote_address,
    default_limits = ["200 per day", "30 per hour"]
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
@limiter.limit("30 per hour")
def create_account():
    try:
        data = request.get_json()
        month=data.get("travel_month")
        if month is not None:
            if not isinstance(month, int) or month < 1 or month > 12:
                return jsonify({"error": "Invalid travel month"}), 400

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
        user_id = str(uuid.uuid4())

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

        return jsonify({
            "message": "Account created successfully. Please login.",
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/update-account", methods=[ "PUT" ])
@token_required
def update_account():
    try:
        data = request.get_json()
        age = data.get("age")
        budget = data.get("budget")
        beach = data.get("beach")
        trekking = data.get("trekking")
        culture = data.get("culture")
        adventure = data.get("adventure")
        travel_month = data.get("travel_month")
        destination_id = data.get("destination_id")

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # check destination exists
        if destination_id is not None:
            cursor.execute(
                "SELECT 1 FROM destination WHERE destination_id=%s",
                (destination_id,)
            )
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Invalid destination_id"}), 400


        # validate month
        if travel_month is not None:
            if not isinstance(travel_month, int) or travel_month < 1 or travel_month > 12:
                return jsonify({"error": "Invalid travel month"}), 400
        

        query = """
        UPDATE users SET 
            age = COALESCE(%s, age),
            budget = COALESCE(%s, budget),
            beach = COALESCE(%s, beach),
            trekking = COALESCE(%s, trekking),
            culture = COALESCE(%s, culture),
            adventure = COALESCE(%s, adventure),
            travel_month = COALESCE(%s, travel_month),
            destination_id = COALESCE(%s, destination_id)
        WHERE user_id = %s
        """

        values = (
            age,
            budget,
            beach,
            trekking,
            culture,
            adventure,
            travel_month,
            destination_id,
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


# display name, age, curr location, bio, travel history
@app.route("/api/profile", methods = [ "GET" ])
@limiter.limit("30 per hour")
def profile():
    pass



@app.route("/api/login",methods = [ "POST" ])
@limiter.limit("30 per hour")
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

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
@token_required
def create_group():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id
        max_members = data.get("max_members", 4)
        group_id = str(uuid.uuid4())
        month = data.get("travel_month")


        if month is not None:
            if not isinstance(month, int) or month < 1 or month > 12:
                return jsonify({"error": "Invalid travel month"}), 400

        if not isinstance(max_members, int):
            return jsonify({"error": "max_members must be integer"}), 400

        if max_members is not None and (max_members < 2 or max_members > 10):
            return jsonify({"error": "Group size must be between 2 and 10"}), 400

        if ((data.get("group_name") and len(data["group_name"]) > 100) or (data.get("description") and len(data["description"]) > 500) or (data.get("destination_name") and len(data["destination_name"]) > 100)):
            return jsonify({"error":"string too long"}), 400
        
        if not data.get("group_name") or not data.get("destination_name"):
            return jsonify({"error": "group_name and destination_name required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # check for duplicate group name
        cursor.execute("""
        SELECT group_id FROM travel_groups WHERE group_name = %s""", (data["group_name"],))
        existing = cursor.fetchone()
        if existing:
             return jsonify({"error": "Group name already exists"}), 400

        cursor.execute("""
        INSERT INTO travel_groups (group_id, group_name, destination_name, travel_month, description, max_members, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)""", (
            group_id,
            data["group_name"],
            data["destination_name"],
            month,
            data.get("description"),
            max_members,
            user_id
        ))

        cursor.execute("""INSERT INTO group_members (group_id, user_id, role) VALUES (%s,%s,'admin')""",(group_id,user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message":"Group created","group_id": group_id}), 201

    except Exception as e:
        return jsonify({"error":str(e)}), 500



@app.route("/api/join-group", methods = [ "POST" ])
@token_required
def join_group():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id
        group_id = data["group_id"]

        if not group_id:
            return jsonify({"error": "group_id required"}), 400


        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        # check group exists
        cursor.execute("SELECT max_members FROM travel_groups WHERE group_id=%s",(group_id,))
        group = cursor.fetchone()

        if not group:
            cursor.close()
            conn.close()
            return jsonify({"error": "Group not found"}), 404

        # check if already member
        cursor.execute("SELECT 1 FROM group_members WHERE group_id=%s AND user_id=%s",(group_id, user_id))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Already a member"}), 400

        # check existing join request
        cursor.execute("SELECT status FROM group_join_requests WHERE group_id=%s AND user_id=%s",(group_id, user_id))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Join request already exists"}), 400

        # count current members
        cursor.execute("SELECT COUNT(*) AS members FROM group_members WHERE group_id=%s",(group_id,))
        members = cursor.fetchone()["members"]

        # check capacity
        if members >= group["max_members"]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Group is already full"}), 400

        request_id = str(uuid.uuid4())

        cursor.execute("""INSERT INTO group_join_requests (request_id, group_id, user_id) VALUES (%s,%s,%s)""",(request_id, group_id, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Join request sent"}), 200

    except Exception as e:
        return jsonify({"error":str(e)}), 500



@app.route("/api/update-group", methods = [ "PUT" ])
@token_required
def update_group():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id
        group_id = data["group_id"]
        month = data.get("travel_month")
        group_name = data.get("group_name")
        description = data.get("description")
        destination = data.get("destination_name")
        max_members = data.get("max_members")

        if not group_id:
            return jsonify({"error": "group_id required"}), 400

        if ((data.get("group_name") and len(data["group_name"]) > 100) or (data.get("description") and len(data["description"]) > 500) or (data.get("destination_name") and len(data["destination_name"]) > 100)):
            return jsonify({"error":"string too long"}), 400

        if month is not None:
            if not isinstance(month, int) or month < 1 or month > 12:
                return jsonify({"error": "Invalid travel month"}), 400

        if max_members is not None:
            if not isinstance(max_members, int):
                return jsonify({"error": "max_members must be integer"}), 400
            if max_members < 2 or max_members > 10:
                return jsonify({"error": "Group size must be between 2 and 10"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)


        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, user_id))
        role = cursor.fetchone()

        if not role or role["role"] != "admin":
            return jsonify({"error": "Only admin can update group"}), 403


        # return the first non-null value in a list
        cursor.execute("""
            UPDATE travel_groups SET group_name = COALESCE(%s, group_name), description = COALESCE(%s, description), destination_name = COALESCE(%s, destination_name),travel_month = COALESCE(%s, travel_month),
            max_members = COALESCE(%s, max_members) WHERE group_id = %s """, (group_name, description, destination, month, max_members, group_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Group updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/delete-group", methods = [ "DELETE" ])
@token_required
def delete_group():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400


        user_id = request.user_id
        group_id = data["group_id"]

        if not group_id:
            return jsonify({"error": "group_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """,(group_id,user_id))
        role = cursor.fetchone()

        if not role or role["role"] != "admin":
            return jsonify({"error":"Only admin can delete group"}), 403

        cursor.execute("DELETE FROM travel_groups WHERE group_id=%s",(group_id,))


        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message":"Group deleted"}), 200

    except Exception as e:
        return jsonify({"error":str(e)}), 500



@app.route("/api/groups", methods=[ "GET" ])
@token_required
def get_groups():
    try:
        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT g.group_id, g.group_name, g.destination_name, g.travel_month, g.description, g.max_members, u.username AS admin,COUNT(m.user_id) AS current_members,
        MAX(CASE WHEN m.user_id = %s THEN 1 ELSE 0 END) AS joined,
        MAX(CASE WHEN r.user_id = %s AND r.status='pending' THEN 1 ELSE 0 END) AS request_pending
        FROM travel_groups g
        LEFT JOIN group_members m 
            ON g.group_id = m.group_id
        LEFT JOIN users u
            ON g.created_by = u.user_id
        LEFT JOIN group_join_requests r ON g.group_id = r.group_id AND r.user_id=%s
        GROUP BY g.group_id, g.group_name, g.destination_name, g.travel_month, g.description, g.max_members, u.username 
        ORDER BY g.created_at DESC""", (user_id, user_id, user_id))

        groups = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"groups": groups}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/group/allow", methods=[ "POST" ])
@token_required
def allow_request():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        admin_id = request.user_id
        group_id = data["group_id"]
        user_id = data["user_id"]

        if not group_id or not user_id:
            return jsonify({"error": "group_id and user_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, admin_id))
        role = cursor.fetchone()

        if not role or role["role"] != "admin":
            return jsonify({"error": "Only admin allowed"}), 403


        # verify request exists
        cursor.execute("""SELECT status FROM group_join_requests WHERE group_id=%s AND user_id=%s """, (group_id, user_id))
        req = cursor.fetchone()

        if not req:
            return jsonify({"error": "Request not found"}), 404

        if req["status"] != "pending":
            return jsonify({"error": "Request already processed"}), 400

        # check membership
        cursor.execute("""SELECT 1 FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        if cursor.fetchone():
            return jsonify({"error": "User already a member"}), 400

        # check group capacity
        cursor.execute("""SELECT COUNT(*) AS members FROM group_members WHERE group_id=%s """, (group_id,))
        members = cursor.fetchone()["members"]

        cursor.execute("""SELECT max_members FROM travel_groups WHERE group_id=%s """, (group_id,))
        group = cursor.fetchone()

        if not group:
            return jsonify({"error": "Group not found"}), 404

        if members >= group["max_members"]:
            return jsonify({"error": "Group is full"}), 400

        cursor.execute("""INSERT INTO group_members (group_id, user_id, role) VALUES (%s,%s,'member') """, (group_id, user_id))
        cursor.execute("""UPDATE group_join_requests SET status='approved' WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User approved"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/group/reject", methods=[ "POST" ])
@token_required
def reject_request():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        admin_id = request.user_id

        group_id = data["group_id"]
        user_id = data["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, admin_id))
        role = cursor.fetchone()

        if not role or role["role"] != "admin":
            return jsonify({"error": "Only admin allowed"}), 403
        

        cursor.execute("""SELECT status FROM group_join_requests WHERE group_id=%s AND user_id=%s """, (group_id, user_id))
        req = cursor.fetchone()

        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        if req["status"] != "pending":
            return jsonify({"error": "Request already processed"}), 400

        cursor.execute("""UPDATE group_join_requests SET status='rejected' WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Request rejected"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/group/leave", methods=[ "POST" ])
@token_required
def leave():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id
        group_id = data["group_id"]

        if not group_id:
            return jsonify({"error": "group_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        # check membership
        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, user_id))
        member = cursor.fetchone()

        if not member:
            return jsonify({"error": "You are not a member of this group"}), 400

        # admin cannot leave
        if member["role"] == "admin":
            return jsonify({"error": "Admin cannot leave the group"}), 400

        # remove member
        cursor.execute("""DELETE FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        # rm old join request
        cursor.execute("""DELETE FROM group_join_requests WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Left group successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# list the join requests
@app.route("/api/group/requests", methods=[ "GET" ])
@token_required
def group_requests():
    try:
        admin_id = request.user_id
        group_id = request.args.get("group_id")

        if not group_id:
            return jsonify({"error": "group_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # verify admin
        cursor.execute("""SELECT role FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, admin_id))

        role = cursor.fetchone()

        if not role or role["role"] != "admin":
            return jsonify({"error": "Only admin allowed"}), 403


        # get pending requests
        cursor.execute("""
        SELECT r.user_id, u.username, r.requested_at
        FROM group_join_requests r JOIN users u ON r.user_id = u.user_id WHERE r.group_id=%s AND r.status='pending' ORDER BY r.requested_at ASC""", (group_id,))

        requests = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"group_id": group_id, "pending_requests": requests}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



''' ============== chat ================= '''

# private chat
@app.route("/api/chat/send", methods=["POST"])
@limiter.limit("5 per minute")
@token_required
def send_private_message():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        sender_id = request.user_id
        receiver_id = data.get("receiver_id")
        message = data.get("message")

        if not receiver_id or not message:
            return jsonify({"error": "receiver_id and message required"}), 400

        message = message.strip()

        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        if len(message) > 2000:
            return jsonify({"error": "Message too long"}), 400

        if receiver_id == sender_id:
            return jsonify({"error": "Cannot message yourself"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # verify receiver exists
        cursor.execute("SELECT 1 FROM users WHERE user_id=%s", (receiver_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "User unavailable"}), 404

        message_id = str(uuid.uuid4())

        cursor.execute("""INSERT INTO private_messages (message_id, sender_id, receiver_id, message) VALUES (%s,%s,%s,%s)""", (message_id, sender_id, receiver_id, message))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Message sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/chat/messages", methods=["GET"])
@token_required
def get_private_messages():
    try:
        user_id = request.user_id
        other_user = request.args.get("user_id")

        if not other_user:
            return jsonify({"error": "user_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT sender_id, receiver_id, message, sent_at FROM private_messages WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s) ORDER BY sent_at ASC LIMIT 100""", (user_id, other_user, other_user, user_id))

        messages = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"messages": messages}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/chat/unread", methods=["GET"])
@token_required
def unread_messages():
    try:
        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT pm.sender_id AS user_id, u.username, COUNT(*) AS unread
        FROM private_messages pm JOIN users u ON pm.sender_id = u.user_id
        WHERE pm.receiver_id = %s
        AND pm.is_read = FALSE GROUP BY pm.sender_id """, (user_id,))

        rows = cursor.fetchall()
        total_unread = sum(row["unread"] for row in rows)

        cursor.close()
        conn.close()

        return jsonify({
            "total_unread": total_unread,
            "conversations": rows
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/chat/read", methods=["POST"])
@token_required
def mark_chat_read():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        receiver_id = request.user_id
        sender_id = data.get("user_id")

        if not sender_id:
            return jsonify({"error": "user_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE private_messages SET is_read = TRUE
        WHERE receiver_id = %s AND sender_id = %s AND is_read = FALSE""", (receiver_id, sender_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Messages marked as read"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# group chat
@app.route("/api/group/chat/send", methods=[ "POST" ])
@limiter.limit("5 per minute")
@token_required
def send_group_message():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        user_id = request.user_id
        group_id = data.get("group_id")
        message = data.get("message")

        if not group_id or not message:
            return jsonify({"error": "group_id and message required"}), 400

        message = message.strip()

        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        if len(message) > 2000:
            return jsonify({"error": "Message too long"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary = True)

        # verify membership
        cursor.execute("""SELECT 1 FROM group_members WHERE group_id=%s AND user_id=%s""", (group_id, user_id))

        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Not a group member"}), 403

        message_id = str(uuid.uuid4())

        cursor.execute("""INSERT INTO group_messages (message_id, group_id, sender_id, message) VALUES (%s,%s,%s,%s) """, (message_id, group_id, user_id, message))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Message sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/group/chat", methods=["GET"])
@token_required
def get_group_messages():
    try:
        user_id = request.user_id
        group_id = request.args.get("group_id")

        if not group_id:
            return jsonify({"error": "group_id required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # verify membership
        cursor.execute("""
        SELECT 1 FROM group_members WHERE group_id=%s AND user_id=%s """, (group_id, user_id))

        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Not a group member"}), 403

        cursor.execute("""SELECT gm.sender_id, u.username, gm.message, gm.sent_at FROM group_messages gm JOIN users u ON gm.sender_id = u.user_id WHERE gm.group_id=%s ORDER BY gm.sent_at ASC LIMIT 100""", (group_id,))

        messages = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"messages": messages}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





''' ========== model ============== '''

# recomend top n users
@app.route("/api/recommend", methods =[ "POST" ])
@limiter.limit("30 per hour")
@token_required
def recommend():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        user_id = request.user_id   # from jwt
        top_n = data.get("top_n", 5)
        # type check
        if not isinstance(top_n, int):
            return jsonify({"error": "top_n must be an integer"}), 400

        # range check
        if top_n < 1 or top_n > 20:
            return jsonify({"error": "top_n must be between 1 and 20"}), 400

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