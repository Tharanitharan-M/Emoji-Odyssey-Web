from flask import Blueprint, request, jsonify
from middleware import token_required
from config import supabase_client
import uuid
import random
from datetime import datetime

multiplayer_blueprint = Blueprint("multiplayer", __name__)

# 🔹 Create a Multiplayer Room
@multiplayer_blueprint.route("/create_room", methods=["POST"])
def create_room():
    try:
        data = request.json
        host_id = data.get("host_id")

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

        # Automatically create a game state for the room, setting host as first turn
        supabase_client.table("game_state").insert({
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "current_turn": host_id,  # Ensure the host starts first
            "game_data": {"scores": {}},
            "is_active": True,
            "total_rounds": 5,
            "current_round": 1
        }).execute()

        return jsonify({"room_id": room_id, "room_code": room_code})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Join a Multiplayer Room
@multiplayer_blueprint.route("/join_room", methods=["POST"])
def join_room():
    try:
        data = request.json
        room_code = data.get("room_code")
        user_id = data.get("user_id")

        if not room_code or not user_id:
            return jsonify({"error": "room_code and user_id are required"}), 400

        # 🔹 Find the room using the room_code
        room_response = supabase_client.table("game_rooms").select("id").eq("room_code", room_code).execute()

        if not room_response.data:
            return jsonify({"error": "Invalid room code"}), 404

        room_id = room_response.data[0]["id"]

        # 🔹 Check if the player is already in the room
        existing_player_response = supabase_client.table("players_in_room").select("user_id").eq("room_id", room_id).eq("user_id", user_id).execute()

        if existing_player_response.data:
            return jsonify({"message": "Player already in room", "room_id": room_id})

        # 🔹 Add player to the room
        supabase_client.table("players_in_room").insert({
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": user_id,
            "joined_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({"room_id": room_id, "message": "Player joined the room successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Submit an Emoji in Multiplayer Mode (Host Only)
@multiplayer_blueprint.route("/set_emoji", methods=["POST"])
@token_required
def set_emoji(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        emoji_clue = data.get("emoji_clue")
        correct_answer = data.get("correct_answer")

        if not room_id or not emoji_clue or not correct_answer:
            return jsonify({"error": "room_id, emoji_clue, and correct_answer are required"}), 400

        # 🔹 Fetch the host ID
        room_response = supabase_client.table("game_rooms").select("host_id").eq("id", room_id).execute()
        if not room_response.data:
            return jsonify({"error": "Room not found"}), 404

        host_id = room_response.data[0]["host_id"]

        # 🔹 Get all players in the room
        players_response = supabase_client.table("players_in_room").select("user_id").eq("room_id", room_id).execute()
        if not players_response.data or len(players_response.data) < 2:
            return jsonify({"error": "No other players in the room"}), 404

        all_players = [p["user_id"] for p in players_response.data]

        # 🔹 Select the first player who is NOT the host
        first_player = next(player for player in all_players if player != host_id)

        # 🔹 Update the game state to set the first turn
        supabase_client.table("game_state").update({
            "current_turn": first_player  # 🎯 First player starts, NOT the host
        }).eq("room_id", room_id).execute()

        return jsonify({"message": "Emoji puzzle set successfully!", "next_turn": first_player})

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
        game_state_response = supabase_client.table("game_state").select("current_turn", "game_data").eq("room_id", room_id).execute()

        if not game_state_response.data:
            return jsonify({"error": "Game state not found"}), 404

        game_data = game_state_response.data[0]
        current_turn = game_data["current_turn"]

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

        # 🔹 Update game state with new turn and scores
        supabase_client.table("game_state").update({
            "game_data": { "scores": current_scores },
            "current_turn": next_player
        }).eq("room_id", room_id).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!",
            "new_score": current_scores[user_id],
            "next_turn": next_player
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
