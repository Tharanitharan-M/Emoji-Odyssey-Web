from flask import Blueprint, request, jsonify
from config import supabase_client
from datetime import datetime

singleplayer_blueprint = Blueprint("singleplayer", __name__)

# 🔹 Get Available Genres for Single Player
@singleplayer_blueprint.route("/get_genres", methods=["GET"])
def get_genres():
    try:
        response = supabase_client.table("emoji_puzzles").select("genre").execute()
        if not response.data:
            return jsonify({"error": "No genres found"}), 404
        genres = list(set([entry["genre"] for entry in response.data]))
        return jsonify({"genres": genres})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Get Levels for a Selected Genre (Up to Player's Progress)
@singleplayer_blueprint.route("/get_levels/<user_id>/<genre>", methods=["GET"])
def get_levels(user_id, genre):
    try:
        # Get the player's progress
        progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", genre).execute()
        completed_levels = int(progress_response.data[0]["completed_levels"]) if progress_response.data else 0

        # Fetch only the next level for the player's progress
        response = supabase_client.table("emoji_puzzles").select("level_number", "emoji_clue").eq("genre", genre).eq("level_number", completed_levels + 1).execute()
        if not response.data:
            return jsonify({"error": "No next level found. You completed all levels!"}), 404

        levels = [{"level_number": int(entry["level_number"]), "emoji_clue": entry["emoji_clue"]} for entry in response.data]

        return jsonify({"levels": levels, "completed_levels": completed_levels})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Submit Answer for Singleplayer Mode
@singleplayer_blueprint.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.json
        user_id = data.get("user_id")
        level_number = data.get("level_number")  # ✅ Updated to `level_number`
        player_answer = data.get("answer")

        if not user_id or level_number is None or not player_answer:
            return jsonify({"error": "user_id, level_number, and answer are required"}), 400

        # Check if player has already completed this level
        progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", "movies").execute()
        completed_levels = progress_response.data[0]["completed_levels"] if progress_response.data else 0

        if completed_levels >= level_number:  # ✅ Ensure points are given only once
            return jsonify({
                "correct": False,
                "message": "You have already completed this level. No extra points awarded!",
                "new_score": completed_levels * 10  # Score remains the same
            })

        # Fetch correct answer
        response = supabase_client.table("emoji_puzzles").select("correct_answer", "genre").eq("level_number", level_number).execute()
        if not response.data:
            return jsonify({"error": "Invalid level number"}), 404

        correct_answer = response.data[0]["correct_answer"]
        genre = response.data[0]["genre"]

        # Check if the answer is correct
        is_correct = player_answer.strip().lower() == correct_answer.strip().lower()
        score_increment = 10 if is_correct else 0

        # Update leaderboard score only if not completed before
        leaderboard_response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).eq("genre", genre).execute()
        current_score = leaderboard_response.data[0]["total_score"] if leaderboard_response.data else 0
        updated_score = current_score + score_increment

        if is_correct:
            # Update player progress (unlock next level)
            supabase_client.table("player_progress").update({"completed_levels": completed_levels + 1}).eq("user_id", user_id).eq("genre", genre).execute()

            # Update leaderboard score
            supabase_client.table("leaderboard").update({"total_score": updated_score}).eq("user_id", user_id).eq("genre", genre).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!" if is_correct else "Wrong answer!",
            "new_score": updated_score if is_correct else current_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
