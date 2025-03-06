from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required
from time import time

leaderboard_blueprint = Blueprint("leaderboard", __name__)

# 🔹 Submit Score API (Requires Token)
@leaderboard_blueprint.route("/submit_score", methods=["POST"])
@token_required
def submit_score(user_id):
    try:
        data = request.json
        score = data.get("score")

        if score is None:
            return jsonify({"error": "Score is required"}), 400

        # Insert score with Unix timestamp
        response = supabase_client.table("leaderboard").insert({
            "user_id": user_id,
            "score": score,
            "timestamp": int(time())  # Store Unix timestamp (BIGINT)
        }).execute()

        return jsonify({"message": "Score submitted successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Get Leaderboard API
@leaderboard_blueprint.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        response = supabase_client.table("leaderboard").select("user_id, score, timestamp").order("score", desc=True).execute()
        return jsonify(response.data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
