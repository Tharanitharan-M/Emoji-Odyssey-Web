from flask import Blueprint, request, jsonify
from config import supabase_client
from middleware import token_required
import uuid
from datetime import datetime

chat_blueprint = Blueprint("chat", __name__)

@chat_blueprint.route("/send_message", methods=["POST"])
@token_required
def send_message(user_id):
    try:
        data = request.json
        room_id = data.get("room_id")
        message = data.get("message")

        if not room_id or not message:
            return jsonify({"error": "room_id and message are required"}), 400

        # 🔹 Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        # 🔹 Check if the room exists
        room_check = supabase_client.table("game_rooms").select("id").eq("id", room_id).execute()

        if not room_check.data:
            return jsonify({"error": "Room does not exist. Please create or join a valid room."}), 400

        # Insert message into chat table with correct timestamp format
        response = supabase_client.table("chat_messages").insert({
            "room_id": room_id,
            "sender_id": user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()

        return jsonify({"message": "Message sent successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 🔹 Get all chat messages in a room
@chat_blueprint.route("/get_messages/<room_id>", methods=["GET"])
@token_required
def get_messages(user_id, room_id):
    try:
        # 🔹 Validate room_id as UUID
        try:
            room_id = str(uuid.UUID(room_id))
        except ValueError:
            return jsonify({"error": "Invalid room_id format. Must be a valid UUID."}), 400

        response = supabase_client.table("chat_messages")\
            .select("sender_id, message, timestamp")\
            .eq("room_id", room_id)\
            .order("timestamp", desc=False)\
            .execute()

        return jsonify({"messages": response.data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

