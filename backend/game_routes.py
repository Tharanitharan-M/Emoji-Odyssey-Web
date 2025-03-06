from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required
import uuid
import random
import string
from datetime import datetime, timedelta

game_blueprint = Blueprint("game", __name__)

# 🔹 Generate a unique room code
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 🔹 Create a game room
@game_blueprint.route("/create_room", methods=["POST"])
@token_required
def create_room(user_id):
    try:
        room_code = generate_room_code()

        # Create a new game room
        response = supabase_client.table("game_rooms").insert({
            "room_code": room_code,
            "host_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        room_id = response.data[0]["id"]

        # 🔹 Set up the initial game state with the first turn
        supabase_client.table("game_state").insert({
            "room_id": room_id,
            "current_turn": user_id,  # 🔹 First turn is the host
            "game_data": { "scores": {} },
            "current_round": 1,
            "is_active": True,
            "total_rounds": 5,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({
            "room_id": room_id,
            "room_code": room_code,
            "message": "Game room created successfully! First turn set to host."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@game_blueprint.route("/join_room", methods=["POST"])
@token_required
def join_room(user_id):
    try:
        data = request.json
        room_code = data.get("room_code")

        if not room_code:
            return jsonify({"error": "room_code is required"}), 400

        # Find the room by code
        room_check = supabase_client.table("game_rooms").select("id").eq("room_code", room_code).execute()

        if not room_check.data:
            return jsonify({"error": "Invalid room code. Room does not exist."}), 400

        room_id = room_check.data[0]["id"]

        return jsonify({"room_id": room_id, "message": "Joined room successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@game_blueprint.route("/update_game_state", methods=["POST"])
@token_required
def update_game_state(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        game_data = data.get("game_data")
        next_turn = data.get("next_turn")

        if not room_id or not game_data or not next_turn:
            return jsonify({"error": "room_id, game_data, and next_turn are required"}), 400

        # 🔹 Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        # 🔹 Check if the room exists in game_rooms
        room_check = supabase_client.table("game_rooms").select("id").eq("id", room_id).execute()

        if not room_check.data:
            return jsonify({"error": "Room does not exist. Please create a game room first."}), 400

        # Insert or update game state
        response = supabase_client.table("game_state").upsert({
            "room_id": room_id,
            "current_turn": next_turn,
            "game_data": game_data,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({"message": "Game state updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@game_blueprint.route("/get_game_state/<room_id>", methods=["GET"])
@token_required
def get_game_state(user_id, room_id):
    try:
        # Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        response = supabase_client.table("game_state").select("*").eq("room_id", room_id).execute()

        if not response.data:
            return jsonify({"error": "No game state found for this room."}), 404

        return jsonify(response.data[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@game_blueprint.route("/take_turn", methods=["POST"])
@token_required
def take_turn(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        guess = data.get("guess")
        next_turn = data.get("next_turn")

        if not room_id or not guess or not next_turn:
            return jsonify({"error": "room_id, guess, and next_turn are required"}), 400

        # Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        # Fetch game state
        game_state = supabase_client.table("game_state").select("*").eq("room_id", room_id).execute()

        if not game_state.data:
            return jsonify({"error": "Game state not found."}), 404

        game_data = game_state.data[0]
        print("🔹 DEBUG: Current Turn:", game_data["current_turn"])
        print("🔹 DEBUG: User ID:", user_id)

        if not game_data["is_active"]:
            return jsonify({"error": "Game has already ended."}), 400

        if game_data["current_turn"] != user_id:
            return jsonify({"error": "Not your turn!", "expected_turn": game_data["current_turn"], "your_id": user_id}), 403

        # Update game data (validate answer, update score, switch turns)
        new_game_data = game_data["game_data"]
        player_scores = new_game_data.get("scores", {})

        if guess == "correct":
            player_scores[user_id] = player_scores.get(user_id, 0) + 10

        # Check if the game should end
        next_round = game_data["current_round"] + 1
        is_game_active = next_round <= game_data["total_rounds"]

        # Update game state
        response = supabase_client.table("game_state").update({
            "current_turn": next_turn,
            "game_data": { "scores": player_scores },
            "current_round": next_round,
            "is_active": is_game_active,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("room_id", room_id).execute()

        return jsonify({
            "message": "Turn taken successfully!",
            "next_turn": next_turn,
            "scores": player_scores,
            "game_over": not is_game_active
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@game_blueprint.route("/get_turn_info/<room_id>", methods=["GET"])
@token_required
def get_turn_info(user_id, room_id):
    try:
        # Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        response = supabase_client.table("game_state").select("current_turn", "current_round", "total_rounds", "is_active").eq("room_id", room_id).execute()

        if not response.data:
            return jsonify({"error": "Game state not found."}), 404

        return jsonify(response.data[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import random

from datetime import datetime, timedelta

@game_blueprint.route("/get_emoji_puzzle/<room_id>/<genre>", methods=["GET"])
@token_required
def get_emoji_puzzle(user_id, room_id, genre):
    try:
        # Validate room_id
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format"}), 400

        # Fetch a random emoji puzzle from the selected genre
        response = supabase_client.table("emoji_puzzles").select("*").eq("genre", genre).execute()

        if not response.data:
            return jsonify({"error": "No emoji puzzles found for this genre"}), 404

        random_puzzle = random.choice(response.data)

        # Set a 30-second timer for the turn
        turn_end_time = datetime.utcnow() + timedelta(seconds=30)

        # Update game_state with turn_end_time
        supabase_client.table("game_state").update({
            "turn_end_time": turn_end_time.isoformat()
        }).eq("room_id", room_id).execute()

        return jsonify({
            "puzzle_id": random_puzzle["id"],
            "emoji_clue": random_puzzle["emoji_clue"],
            "turn_end_time": turn_end_time.isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@game_blueprint.route("/submit_emoji_answer", methods=["POST"])
@token_required
def submit_emoji_answer(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        puzzle_id = data.get("puzzle_id")
        player_answer = data.get("answer")

        if not room_id or not puzzle_id or not player_answer:
            return jsonify({"error": "room_id, puzzle_id, and answer are required"}), 400

        # Validate room_id
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format"}), 400

        # Fetch game state
        game_state_response = supabase_client.table("game_state").select("*").eq("room_id", room_id).execute()

        if not game_state_response.data:
            return jsonify({"error": "Game state not found"}), 404

        game_data = game_state_response.data[0]
        turn_end_time = game_data["turn_end_time"]

        # Check if the turn timer has expired
        if turn_end_time and datetime.utcnow().isoformat() > turn_end_time:
            return jsonify({"error": "Time is up! Your turn has been skipped."}), 400

        # Fetch the correct answer from the emoji_puzzles table
        response = supabase_client.table("emoji_puzzles").select("correct_answer", "genre").eq("id", puzzle_id).execute()

        if not response.data:
            return jsonify({"error": "Invalid puzzle ID"}), 404

        correct_answer = response.data[0]["correct_answer"]
        genre = response.data[0]["genre"]

        # Get current scores
        current_scores = game_data["game_data"].get("scores", {})

        # Check if answer is correct
        if player_answer.strip().lower() == correct_answer.strip().lower():
            current_scores[genre][user_id] = current_scores[genre].get(user_id, 0) + 10
            is_correct = True
        else:
            is_correct = False

        # Update game state with new score
        supabase_client.table("game_state").update({
            "game_data": { "scores": current_scores },
            "updated_at": datetime.utcnow().isoformat()
        }).eq("room_id", room_id).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!",
            "new_score": current_scores[genre][user_id]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@game_blueprint.route("/get_genres", methods=["GET"])
def get_genres():
    try:
        # Fetch unique genres from the emoji_puzzles table
        response = supabase_client.table("emoji_puzzles").select("genre").execute()

        if not response.data:
            return jsonify({"error": "No genres found"}), 404

        # Extract unique genres
        genres = list(set([entry["genre"] for entry in response.data]))

        return jsonify({"genres": genres})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
