from flask import Blueprint, jsonify, request
from config import supabase_client

singleplayer_blueprint = Blueprint('singleplayer', __name__)

@singleplayer_blueprint.route("/get_genres", methods=["GET"])
def get_genres():
    try:
        # Fetch all unique genres from the emoji_puzzles table
        response = supabase_client.table("emoji_puzzles").select("genre").execute()
        genres = list(set(entry["genre"] for entry in response.data))

        if not genres:
            return jsonify({"error": "No genres found"}), 404

        return jsonify({"genres": genres})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@singleplayer_blueprint.route("/get_score/<user_id>/<genre>", methods=["GET"])
def get_score(user_id, genre):
    try:
        # Fetch the user's score for the specific genre from the leaderboard
        response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).eq("genre", genre).execute()
        score = response.data[0]["total_score"] if response.data else 0

        return jsonify({"score": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@singleplayer_blueprint.route("/get_levels/<user_id>/<genre>", methods=["GET"])
def get_levels(user_id, genre):
    try:
        # Fetch the player's progress
        progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", genre).execute()
        completed_levels = int(progress_response.data[0]["completed_levels"]) if progress_response.data else 0

        # Fetch levels along with correct answers
        levels_response = supabase_client.table("emoji_puzzles").select("level_number", "emoji_clue", "correct_answer").eq("genre", genre).order("level_number").execute()

        levels = []
        for entry in levels_response.data:
            level_number = int(entry["level_number"])
            is_unlocked = level_number <= completed_levels + 1
            levels.append({
                "level_number": level_number,
                "emoji_clue": entry["emoji_clue"],
                "correct_answer": entry["correct_answer"],  # ✅ Include correct answer
                "is_unlocked": is_unlocked
            })

        return jsonify({
            "levels": levels,
            "completed_levels": completed_levels
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@singleplayer_blueprint.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.json
        user_id = data.get("user_id")
        level_number = data.get("level_number")
        player_answer = data.get("answer")

        if not user_id or level_number is None or not player_answer:
            return jsonify({"error": "user_id, level_number, and answer are required"}), 400

        # Fetch the correct answer and genre for the level
        response = supabase_client.table("emoji_puzzles").select("correct_answer", "genre").eq("level_number", level_number).execute()
        if not response.data:
            return jsonify({"error": "Invalid level number"}), 404

        correct_answer = response.data[0]["correct_answer"]
        genre = response.data[0]["genre"]

        # Check if the answer is correct
        is_correct = player_answer.strip().lower() == correct_answer.strip().lower()
        score_increment = 10 if is_correct else 0

        # Fetch player's current progress for the genre
        progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", genre).execute()
        completed_levels = progress_response.data[0]["completed_levels"] if progress_response.data else 0

        # Fetch player's current score
        leaderboard_response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).eq("genre", genre).execute()
        current_score = leaderboard_response.data[0]["total_score"] if leaderboard_response.data else 0
        updated_score = current_score + score_increment if is_correct and completed_levels < level_number else current_score

        # If progress doesn't exist, insert a new progress record
        if not progress_response.data and is_correct:
            supabase_client.table("player_progress").insert({
                "user_id": user_id,
                "genre": genre,
                "completed_levels": 1
            }).execute()
        elif is_correct and completed_levels < level_number:
            # Update existing progress for the genre
            supabase_client.table("player_progress").update({
                "completed_levels": completed_levels + 1
            }).eq("user_id", user_id).eq("genre", genre).execute()

        # If leaderboard entry doesn't exist, insert it
        if not leaderboard_response.data and is_correct:
            supabase_client.table("leaderboard").insert({
                "user_id": user_id,
                "genre": genre,
                "total_score": score_increment
            }).execute()
        elif is_correct and completed_levels < level_number:
            # Update leaderboard score
            supabase_client.table("leaderboard").update({
                "total_score": updated_score
            }).eq("user_id", user_id).eq("genre", genre).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!" if is_correct else "Wrong answer!",
            "new_score": updated_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
