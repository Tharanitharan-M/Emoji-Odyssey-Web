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
        player_name = data.get("player_name")
        
        if not room_code or not user_id or not player_name:
            return jsonify({"error": "room_code, user_id, and player_name are required"}), 400

        # ✅ Validate Room Code
        room_response = supabase_client.table("game_rooms").select("id", "host_id").eq("room_code", room_code).execute()
        if not room_response.data:
            return jsonify({"error": "Invalid room code"}), 404

        room_id = room_response.data[0]["id"]

        # ✅ Check if Player Already Exists
        existing_player = supabase_client.table("players_in_room").select("id").eq("room_id", room_id).eq("user_id", user_id).execute()
        if existing_player.data:
            return jsonify({"message": "Player already in the room!"}), 200

        # ✅ Insert Player into the Room
        supabase_client.table("players_in_room").insert({
            "room_id": room_id,
            "user_id": user_id,
            "username": player_name,
            "joined_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({
            "room_id": room_id,
            "message": "Player joined the room successfully!"
        })

    except Exception as e:
        print("Error in join_room:", str(e))
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


@multiplayer_blueprint.route("/start_game", methods=["POST"])
def start_game():
    try:
        data = request.json
        room_id = data.get("room_id")

        # Fetch a random question from the database
        question_response = supabase_client.table("game_questions").select("*").order("random()").limit(1).execute()

        if not question_response.data:
            return jsonify({"error": "No questions available."}), 404

        question = question_response.data[0]

        # Set game state
        supabase_client.table("game_state").insert({
            "room_id": room_id,
            "question_id": question["id"],
            "current_round": 1,
            "is_active": True,
            "answered_users": [],
        }).execute()

        return jsonify({
            "question": question["question"],
            "room_id": room_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@multiplayer_blueprint.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.json
        room_id = data.get("room_id")
        user_id = data.get("user_id")
        answer = data.get("answer")

        # Fetch the current question
        game_state_response = supabase_client.table("game_state").select("*").eq("room_id", room_id).execute()

        if not game_state_response.data:
            return jsonify({"error": "Game state not found."}), 404

        game_state = game_state_response.data[0]
        answered_users = game_state.get("answered_users", [])

        # Check if the answer is correct
        question_response = supabase_client.table("emoji_puzzles").select("correct_answer").eq("id", game_state["question_id"]).execute()
        correct_answer = question_response.data[0]['correct_answer']

        if answer.lower().strip() == correct_answer.lower().strip():
            if user_id in answered_users:
                return jsonify({"message": "Already answered correctly."})

            # Calculate points based on order
            points = max(10 - len(answered_users) * 2, 2)

            # Update player's score
            supabase_client.table("players_in_room").update({
                "score": supabase_client.rpc('increment_score', {"amount": points})
            }).eq("user_id", user_id).execute()

            # Update the answered users
            answered_users.append(user_id)
            supabase_client.table("game_state").update({
                "answered_users": answered_users
            }).eq("room_id", room_id).execute()

            return jsonify({"correct": True, "points": points})

        return jsonify({"correct": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@multiplayer_blueprint.route("/get_scores/<room_id>", methods=["GET"])
def get_scores(room_id):
    try:
        response = supabase_client.table("players_in_room").select("username, score").eq("room_id", room_id).order("score", desc=True).execute()
        return jsonify({"players": response.data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@multiplayer_blueprint.route("/end_game/<room_id>", methods=["POST"])
def end_game(room_id):
    try:
        # Delete game state and player data
        supabase_client.table("game_state").delete().eq("room_id", room_id).execute()
        supabase_client.table("players_in_room").delete().eq("room_id", room_id).execute()

        return jsonify({"message": "Game ended and data cleaned."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
import random

@multiplayer_blueprint.route("/get_random_question", methods=["POST"])
def get_random_question():
    try:
        # ✅ Step 1: Get the total number of questions
        count_response = supabase_client.table("emoji_puzzles").select("id", count="exact").execute()
        total_count = count_response.count

        if total_count == 0:
            return jsonify({"error": "No questions available."}), 404

        # ✅ Step 2: Generate a random offset and fetch one question
        random_offset = random.randint(0, total_count - 1)

        # ✅ Fetch one question using range
        question_response = supabase_client.table("emoji_puzzles").select("*").range(random_offset, random_offset).execute()

        if not question_response.data:
            return jsonify({"error": "Failed to fetch question."}), 404

        question = question_response.data[0]

        return jsonify({
            "emoji_clue": question["emoji_clue"],
            "correct_answer": question["correct_answer"]
        })

    except Exception as e:
        print("Error in get_random_question:", str(e))
        return jsonify({"error": str(e)}), 500
