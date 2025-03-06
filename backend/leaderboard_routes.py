from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required, admin_required
from time import time  # For Unix timestamp

leaderboard_blueprint = Blueprint("leaderboard", __name__)

@leaderboard_blueprint.route("/submit_score", methods=["POST"])
@token_required
def submit_score(user_id):
    try:
        data = request.json
        new_score = data.get("score")

        if new_score is None:
            return jsonify({"error": "Score is required"}), 400

        # 🔹 Check if user already has a score
        response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).execute()

        if response.data:
            # 🔹 Update the existing score (add new score)
            current_score = response.data[0]["total_score"]
            updated_score = current_score + new_score  # Running total

            update_response = supabase_client.table("leaderboard").update({
                "total_score": updated_score,
                "timestamp": int(time())  # Update timestamp
            }).eq("user_id", user_id).execute()
        else:
            # 🔹 First time submitting → Insert new row
            update_response = supabase_client.table("leaderboard").insert({
                "user_id": user_id,
                "total_score": new_score,
                "timestamp": int(time())  # Store Unix timestamp
            }).execute()

        return jsonify({"message": "Score updated successfully!", "total_score": updated_score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



from datetime import datetime

@leaderboard_blueprint.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        response = supabase_client.table("leaderboard").select("user_id, total_score, timestamp").execute()

        if not response.data:
            return jsonify({"message": "No scores found"}), 404

        # 🔹 Sum scores per user
        user_scores = {}
        for entry in response.data:
            user_id = entry["user_id"]
            if user_id not in user_scores:
                user_scores[user_id] = {
                    "user_id": user_id,
                    "total_score": 0,
                    "latest_timestamp": entry["timestamp"]
                }
            user_scores[user_id]["total_score"] += entry["total_score"]
            user_scores[user_id]["latest_timestamp"] = max(user_scores[user_id]["latest_timestamp"], entry["timestamp"])

        # Convert Unix timestamps to human-readable format
        for user in user_scores.values():
            user["latest_timestamp"] = datetime.utcfromtimestamp(user["latest_timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Convert to sorted list
        leaderboard = sorted(user_scores.values(), key=lambda x: x["total_score"], reverse=True)

        # Assign rankings
        for index, entry in enumerate(leaderboard, start=1):
            entry["rank"] = index

        # Paginate results
        total_entries = len(leaderboard)
        total_pages = (total_entries + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page

        paginated_results = leaderboard[start:end]

        return jsonify({
            "leaderboard": paginated_results,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_entries": total_entries
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@leaderboard_blueprint.route("/reset_score", methods=["POST"])
@token_required
def reset_score(user_id):
    try:
        # 🔹 Update score to 0
        update_response = supabase_client.table("leaderboard").update({
            "total_score": 0,
            "timestamp": int(time())  # Update timestamp
        }).eq("user_id", user_id).execute()

        return jsonify({"message": "Score has been reset to 0!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@leaderboard_blueprint.route("/update_score", methods=["POST"])
@token_required
def update_score(user_id):
    try:
        data = request.json
        new_score = data.get("score")

        if new_score is None:
            return jsonify({"error": "Score is required"}), 400

        # 🔹 Overwrite the score instead of adding
        update_response = supabase_client.table("leaderboard").update({
            "total_score": new_score,
            "timestamp": int(time())  # Update timestamp
        }).eq("user_id", user_id).execute()

        return jsonify({"message": "Score updated successfully!", "new_score": new_score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@leaderboard_blueprint.route("/admin/reset_leaderboard", methods=["POST"])
@admin_required
def reset_leaderboard(admin_user_id):
    try:
        # Delete all leaderboard records safely
        supabase_client.table("leaderboard").delete().gt("total_score", -1).execute()

        return jsonify({"message": "Leaderboard has been reset!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

