from flask import Blueprint, request, jsonify
from config import supabase_client
import uuid
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
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))  # Generate 6-letter code

        # Insert into game_rooms table
        supabase_client.table("game_rooms").insert({
            "id": room_id,
            "room_code": room_code,
            "host_id": host_id,
            "created_at": datetime.utcnow().isoformat()
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

        # Find the room
        room_response = supabase_client.table("game_rooms").select("id").eq("room_code", room_code).execute()
        if not room_response.data:
            return jsonify({"error": "Invalid room code"}), 404

        room_id = room_response.data[0]["id"]

        return jsonify({"room_id": room_id})

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

        # Insert emoji question
        supabase_client.table("emoji_puzzles").insert({
            "id": str(uuid.uuid4()),
            "emoji_clue": emoji_clue,
            "correct_answer": correct_answer,
            "genre": "multiplayer"
        }).execute()

        return jsonify({"message": "Emoji puzzle set successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
