#!/usr/bin/python3

'''

[user profile]:
- friend recommendation
- follow ?
- 1v1 chat


- create group
- join group
- group chat




[api]:
[+] profile section


[+] interact with the recommendation model 
- /api/send
- /api/recommend




==== TO DO ===

[test]:
curl -X POST -H "Content-Type: application/json" http://127.0.0.1:8080/api/send -d '{"age" : 21, "budget" : 10000, "beach" : 0, "trekking" : 1, "culture" : 1, "adventure" : 1, "travel_month" : 3, "destination_id" : 2}' | jq
curl -X POST -H "Content-Type: application/json" http://127.0.0.1:8080/api/recommend -d '{"user_id" : 1, "top_n" : 10}' | jq


'''

import os
import mysql.connector
from flask import Flask, request, jsonify
from recommender import TravelRecommender


# init
app = Flask(__name__)
SECRET_KEY = os.getenv("KEY")
recommender = TravelRecommender()


def get_db_connection():
    return mysql.connector.connect(host = "localhost", user = "user", password = "1234!", database = "travel")   # hardcode is shit TT (replace it by getenv())



# post USER DATA to db 
@app.route("/api/send", methods=[ "POST" , "OPTIONS" ])
def create_user():
    if request.method == "POST":
        try:
            data = request.get_json()

            required_fields = [ "age", "budget", "beach", "trekking", "culture", "adventure", "travel_month", "destination_id" ]

            # check missing fields
            missing = [f for f in required_fields if f not in data]
            if missing:
                return jsonify({"error": f"Missing fields: {missing}"}), 400

            conn = get_db_connection()
            cursor = conn.cursor()

            query = """ 
            INSERT INTO users ( age, budget, beach, trekking, culture, adventure, travel_month, destination_id ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """

            values = (
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

            new_user_id = cursor.lastrowid

            cursor.close()
            conn.close()

            return jsonify({ "message": "User created successfully", "user_id": new_user_id }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    else:
        return "Method Not Allowed", 405





# recomend top n users
@app.route("/api/recommend", methods=[ "POST", "OPTIONS" ])
def recommend():
    if request.method == "POST":
        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON body provided"}), 400

            user_id = data.get("user_id")
            top_n = data.get("top_n", 5)

            if user_id is None:
                return jsonify({"error": "user_id is required"}), 400

            # call model
            results = recommender.recommend(user_id = int(user_id), top_n = int(top_n))

            return jsonify({ "user_id": user_id, "recommendations": results })

        except Exception as e:
            return jsonify({ "error" : str(e) }), 500

    else:
        return "Method Not Allowed", 405




@app.route("/")
def home():
    return jsonify({ "message": "API server is running"})




# main
if __name__ == "__main__":
    app.run("0.0.0.0", port = 8080)