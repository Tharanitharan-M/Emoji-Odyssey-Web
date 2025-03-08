from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required
import uuid
import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required


game_blueprint = Blueprint("game", __name__)
multiplayer_blueprint = Blueprint("multiplayer", __name__)

# 🔹 Generate a unique room code
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 🔹 Create a game room
@multiplayer_blueprint.route("/create_room", methods=["POST"])
def create_room():
    try:
        data = request.json
        host_id = data.get("host_id")
        total_rounds = data.get("total_rounds", 5)  # Default to 5 rounds if not provided

        if not host_id:
            return jsonify({"error": "host_id is required"}), 400

        room_id = str(uuid.uuid4())
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))  # Generate a 6-letter room code

        # Insert into game_rooms table
        supabase_client.table("game_rooms").insert({
            "id": room_id,
            "room_code": room_code,
            "host_id": host_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # Insert the host as the first player in the room
        supabase_client.table("players_in_room").insert({
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": host_id,
            "joined_at": datetime.utcnow().isoformat()
        }).execute()

        # Automatically create a game state for the room
        supabase_client.table("game_state").insert({
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "current_turn": host_id,  # Host starts first
            "game_data": {"scores": {}},
            "is_active": True,
            "total_rounds": total_rounds,  # 🔹 Ensure total rounds are stored
            "current_round": 1
        }).execute()

        return jsonify({
            "room_id": room_id,
            "room_code": room_code,
            "total_rounds": total_rounds  # 🔹 Now included in response
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



@multiplayer_blueprint.route("/submit_emoji_answer", methods=["POST"])
@token_required
def submit_emoji_answer(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        puzzle_id = data.get("puzzle_id")
        player_answer = data.get("answer")

        if not room_id or not puzzle_id or not player_answer:
            return jsonify({"error": "room_id, puzzle_id, and answer are required"}), 400

        # 🔹 Fetch game state
        game_state_response = supabase_client.table("game_state").select("current_turn", "game_data", "current_round", "total_rounds").eq("room_id", room_id).execute()

        if not game_state_response.data:
            return jsonify({"error": "Game state not found"}), 404

        game_data = game_state_response.data[0]
        current_turn = game_data["current_turn"]
        current_round = game_data["current_round"]
        total_rounds = game_data["total_rounds"]

        # 🔹 Fetch the host ID of the room
        room_response = supabase_client.table("game_rooms").select("host_id").eq("id", room_id).execute()
        if not room_response.data:
            return jsonify({"error": "Room not found"}), 404

        host_id = room_response.data[0]["host_id"]

        # 🔹 Prevent the host from guessing
        if user_id == host_id:
            return jsonify({"error": "The host cannot guess. Only other players can answer."}), 403

        # 🔹 Ensure it's the correct player's turn
        if current_turn != user_id:
            return jsonify({"error": "Not your turn!"}), 403

        # 🔹 Fetch the correct answer
        response = supabase_client.table("emoji_puzzles").select("correct_answer").eq("id", puzzle_id).execute()
        if not response.data:
            return jsonify({"error": "Invalid puzzle ID"}), 404

        correct_answer = response.data[0]["correct_answer"]

        # 🔹 Get current scores
        current_scores = game_data["game_data"].get("scores", {})

        # 🔹 Check if answer is correct
        if player_answer.strip().lower() == correct_answer.strip().lower():
            current_scores[user_id] = current_scores.get(user_id, 0) + 10
            is_correct = True
        else:
            is_correct = False

        # 🔹 Fetch all players in the room
        players_response = supabase_client.table("players_in_room").select("user_id").eq("room_id", room_id).execute()
        if not players_response.data or len(players_response.data) < 2:
            return jsonify({"error": "No other players in the game"}), 404

        all_players = [p["user_id"] for p in players_response.data]

        # 🔹 Ensure turn switches between two players
        if len(all_players) == 2:
            next_player = all_players[0] if user_id == all_players[1] else all_players[1]
        else:
            current_index = all_players.index(user_id)
            next_player = all_players[(current_index + 1) % len(all_players)]

        # 🔹 Check if this was the last round
        if current_round >= total_rounds:
            # 🎯 Determine the winner (player with the highest score)
            winner = max(current_scores, key=current_scores.get) if current_scores else "No winner"

            # 🔹 Store final scores in leaderboard
            for player_id, score in current_scores.items():
                supabase_client.table("leaderboard").insert({
                    "user_id": player_id,
                    "total_score": score,
                    "genre": "multiplayer",  # You can change this if needed
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()

            return jsonify({
                "correct": is_correct,
                "message": "Game over! Winner declared!",
                "winner": winner,
                "final_scores": current_scores
            })

        # 🔹 Update game state with new turn, scores, and increase round count
        supabase_client.table("game_state").update({
            "game_data": { "scores": current_scores },
            "current_turn": next_player,
            "current_round": current_round + 1  # Move to next round
        }).eq("room_id", room_id).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!",
            "new_score": current_scores[user_id],
            "next_turn": next_player
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
