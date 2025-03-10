from flask import Blueprint, request, jsonify
from middleware import token_required
from config import supabase_client
import uuid
import random
from datetime import datetime

multiplayer_blueprint = Blueprint("multiplayer", __name__)

# 🔹 Create a Multiplayer Room
# 🔹 Create a Multiplayer Room
@multiplayer_blueprint.route("/create_room", methods=["POST"])
def create_room():
    try:
        data = request.json
        host_id = data.get("host_id")
        username = data.get("username")
        total_rounds = data.get("total_rounds", 5)

        if not host_id or not username:
            return jsonify({"error": "host_id and username are required"}), 400

        # Generate room ID & Code
        room_id = str(uuid.uuid4())
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))

        # Insert new room
        supabase_client.table("game_rooms").insert({
            "id": room_id,
            "room_code": room_code,
            "host_id": host_id,
            "total_rounds": total_rounds,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # Host joins the room first with username
        supabase_client.table("players_in_room").insert({
            "room_id": room_id,
            "user_id": host_id,
            "username": username,
            "joined_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({
            "room_id": room_id,
            "room_code": room_code,
            "total_rounds": total_rounds
        })

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

        # Find the room
        room_response = supabase_client.table("game_rooms").select("id", "host_id").eq("room_code", room_code).execute()
        if not room_response.data:
            return jsonify({"error": "Invalid room code"}), 404

        room_id = room_response.data[0]["id"]
        host_id = room_response.data[0]["host_id"]

        # Add player to the room
        supabase_client.table("players_in_room").insert({
            "room_id": room_id,
            "user_id": user_id,
            "joined_at": datetime.utcnow().isoformat()
        }).execute()

        # Fetch all players in the room
        players_response = supabase_client.table("players_in_room").select("user_id").eq("room_id", room_id).execute()
        players = [p["user_id"] for p in players_response.data if p["user_id"] != host_id]  # Exclude host

        if len(players) == 1:
            first_player = players[0]
            # Set first turn in game_state
            supabase_client.table("game_state").insert({
                "room_id": room_id,
                "current_turn": first_player,
                "total_rounds": 5,
                "current_round": 1,
                "is_active": True
            }).execute()

        return jsonify({
            "room_id": room_id,
            "message": "Player joined the room successfully!"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Submit an Emoji in Multiplayer Mode (Host Only)
@multiplayer_blueprint.route("/set_emoji", methods=["POST"])
def set_emoji():
    try:
        data = request.json
        room_id = data.get("room_id")
        host_id = data.get("host_id")
        emoji_clue = data.get("emoji_clue")
        correct_answer = data.get("correct_answer")

        if not room_id or not host_id or not emoji_clue or not correct_answer:
            return jsonify({"error": "room_id, host_id, emoji_clue, and correct_answer are required"}), 400

        # Ensure the room exists
        room_response = supabase_client.table("game_rooms").select("id").eq("id", room_id).execute()
        if not room_response.data:
            return jsonify({"error": "Invalid room ID"}), 404

        # Store the puzzle in `game_state`
        puzzle_response = supabase_client.table("game_state").update({
            "game_data": {
                "emoji_clue": emoji_clue,
                "correct_answer": correct_answer
            },
            "updated_at": datetime.utcnow().isoformat()
        }).eq("room_id", room_id).execute()

        return jsonify({
            "message": "Multiplayer emoji puzzle set successfully!"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@multiplayer_blueprint.route("/submit_emoji_answer", methods=["POST"])
def submit_emoji_answer():
    try:
        data = request.json
        room_id = data.get("room_id")
        user_id = data.get("user_id")
        player_answer = data.get("answer")

        if not room_id or not user_id or not player_answer:
            return jsonify({"error": "room_id, user_id, and answer are required"}), 400

        # Fetch game state for this room
        game_state_response = supabase_client.table("game_state").select("current_turn", "game_data", "total_rounds", "current_round", "is_active").eq("room_id", room_id).execute()

        if not game_state_response.data:
            return jsonify({"error": "Game state not found"}), 404

        game_state = game_state_response.data[0]
        current_turn = game_state["current_turn"]
        game_data = game_state["game_data"]
        total_rounds = game_state["total_rounds"]
        current_round = game_state["current_round"]
        is_active = game_state["is_active"]

        # If the game is already finished, prevent further actions
        if not is_active:
            return jsonify({"error": "The game has already ended!"}), 403

        # Get the correct puzzle data
        if "emoji_clue" not in game_data or "correct_answer" not in game_data:
            return jsonify({"error": "No active puzzle found in this room"}), 400

        correct_answer = game_data["correct_answer"]

        # Fetch all players in the room
        players_response = supabase_client.table("players_in_room").select("user_id").eq("room_id", room_id).execute()
        players = [p["user_id"] for p in players_response.data]

        if len(players) < 2:
            return jsonify({"error": "No other players in the game"}), 403  # Ensure at least 2 players exist

        # Check if the answer is correct
        is_correct = player_answer.strip().lower() == correct_answer.strip().lower()
        score_increment = 10 if is_correct else 0

        # Fetch the current leaderboard score
        leaderboard_response = supabase_client.table("leaderboard").select("total_score").eq("user_id", user_id).execute()
        current_score = leaderboard_response.data[0]["total_score"] if leaderboard_response.data else 0
        updated_score = current_score + score_increment

        if is_correct:
            # Update the player's score
            supabase_client.table("leaderboard").update({"total_score": updated_score}).eq("user_id", user_id).execute()

            # Check if the game should end
            if current_round >= total_rounds:
                # End the game
                supabase_client.table("game_state").update({
                    "is_active": False
                }).eq("room_id", room_id).execute()

                return jsonify({
                    "correct": True,
                    "message": "Game over! Final scores are updated.",
                    "new_score": updated_score
                })

            # Get the next player in turn order
            current_index = players.index(user_id)
            next_player = players[(current_index + 1) % len(players)]  # Rotate turn

            # Update game state with the next turn and increase round count
            supabase_client.table("game_state").update({
                "current_turn": next_player,
                "current_round": current_round + 1
            }).eq("room_id", room_id).execute()

        return jsonify({
            "correct": is_correct,
            "message": "Answer submitted successfully!" if is_correct else "Wrong answer!",
            "new_score": updated_score if is_correct else current_score,
            "next_turn": next_player if is_correct else current_turn
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@multiplayer_blueprint.route("/get_players/<room_id>", methods=["GET"])
def get_players(room_id):
    try:
        # Fetch players with usernames from players_in_room table
        players_response = supabase_client.table("players_in_room").select("username").eq("room_id", room_id).execute()

        if not players_response.data:
            return jsonify({"players": []})

        # Extract usernames from the response
        players = [p["username"] for p in players_response.data]

        return jsonify({"players": players})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


