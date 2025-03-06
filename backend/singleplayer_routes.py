from flask import Blueprint, request, jsonify
from config import supabase_client
import random
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

# 🔹 Get Predefined Levels for a Selected Genre
@singleplayer_blueprint.route("/get_levels/<genre>", methods=["GET"])
def get_levels(genre):
    try:
        response = supabase_client.table("emoji_puzzles").select("id", "emoji_clue").eq("genre", genre).execute()
        if not response.data:
            return jsonify({"error": "No levels found for this genre"}), 404

        levels = [{"level_id": entry["id"], "emoji_clue": entry["emoji_clue"]} for entry in response.data]
        return jsonify({"levels": levels})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Submit Answer for Single Player Mode
@singleplayer_blueprint.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.json
        user_id = data.get("user_id")
        level_id = data.get("level_id")
        player_answer = data.get("answer")

        if not user_id or not level_id or not player_answer:
            return jsonify({"error": "user_id, level_id, and answer are required"}), 400

        # Fetch correct answer from database
        response = supabase_client.table("emoji_puzzles").select("correct_answer", "genre").eq("id", level_id).execute()
        if not response.data:
            return jsonify({"error": "Invalid level ID"}), 404

        correct_answer = response.data[0]["correct_answer"]
        genre = response.data[0]["genre"]

        # Check if the answer is correct
        if player_answer.strip().lower() == correct_answer.strip().lower():
            is_correct = True
            score_increment = 10  # Single-player mode fixed score per level
        else:
            is_correct = False
            score_increment = 0

        # Update the leaderboard for the single player
        leaderboard_response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).eq("genre", genre).execute()

        if leaderboard_response.data:
            current_score = leaderboard_response.data[0]["total_score"]
            updated_score = current_score + score_increment
            supabase_client.table("leaderboard").update({"total_score": updated_score}).eq("user_id", user_id).eq("genre", genre).execute()
        else:
            supabase_client.table("leaderboard").insert({"user_id": user_id, "total_score": score_increment, "genre": genre}).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!",
            "new_score": updated_score if is_correct else current_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@singleplayer_blueprint.route("/get_levels/<user_id>/<genre>", methods=["GET"])
def fetch_levels(user_id, genre):
    try:
        # Get the player's progress
        progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", genre).execute()
        
        completed_levels = progress_response.data[0]["completed_levels"] if progress_response.data else 0

        # Fetch only levels up to the player's progress
        response = supabase_client.table("emoji_puzzles").select("id", "emoji_clue").eq("genre", genre).limit(completed_levels + 1).execute()

        if not response.data:
            return jsonify({"error": "No levels found for this genre"}), 404

        levels = [{"level_id": entry["id"], "emoji_clue": entry["emoji_clue"]} for entry in response.data]
        return jsonify({"levels": levels, "completed_levels": completed_levels})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@singleplayer_blueprint.route("/submit_answer", methods=["POST"])
def submit_singleplayer_answer():
    try:
        data = request.json
        user_id = data.get("user_id")
        level_id = data.get("level_id")
        player_answer = data.get("answer")

        if not user_id or not level_id or not player_answer:
            return jsonify({"error": "user_id, level_id, and answer are required"}), 400

        # Fetch correct answer from database
        response = supabase_client.table("emoji_puzzles").select("correct_answer", "genre").eq("id", level_id).execute()
        if not response.data:
            return jsonify({"error": "Invalid level ID"}), 404

        correct_answer = response.data[0]["correct_answer"]
        genre = response.data[0]["genre"]

        # Check if the answer is correct
        if player_answer.strip().lower() == correct_answer.strip().lower():
            is_correct = True
            score_increment = 10  # Single-player mode fixed score per level
        else:
            is_correct = False
            score_increment = 0

        # Update the leaderboard
        leaderboard_response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).eq("genre", genre).execute()

        if leaderboard_response.data:
            current_score = leaderboard_response.data[0]["total_score"]
            updated_score = current_score + score_increment
            supabase_client.table("leaderboard").update({"total_score": updated_score}).eq("user_id", user_id).eq("genre", genre).execute()
        else:
            supabase_client.table("leaderboard").insert({"user_id": user_id, "total_score": score_increment, "genre": genre}).execute()

        # If correct, update progress (unlock next level)
        if is_correct:
            progress_response = supabase_client.table("player_progress").select("completed_levels").eq("user_id", user_id).eq("genre", genre).execute()
            if progress_response.data:
                current_progress = progress_response.data[0]["completed_levels"]
                supabase_client.table("player_progress").update({"completed_levels": current_progress + 1}).eq("user_id", user_id).eq("genre", genre).execute()
            else:
                supabase_client.table("player_progress").insert({"user_id": user_id, "genre": genre, "completed_levels": 1}).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!",
            "new_score": updated_score if is_correct else current_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
