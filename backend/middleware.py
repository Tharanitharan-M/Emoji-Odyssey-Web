import jwt
import time
import uuid
from functools import wraps
from flask import request, jsonify

import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Securely get the JWT Secret from environment
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        try:
            # 🔹 Decode Token
            decoded_token = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
            
            # 🔹 Validate Expiration Time (`exp`)
            if "exp" in decoded_token and decoded_token["exp"] < time.time():
                return jsonify({"error": "Token has expired!"}), 401

            # 🔹 Validate User Role (`role`)
            if decoded_token.get("role") != "authenticated":
                return jsonify({"error": "Unauthorized user role!"}), 403

            # 🔹 Extract User ID (`sub`)
            user_id = decoded_token.get("sub")

            if not user_id:
                return jsonify({"error": "Invalid token structure!"}), 401

            # 🔹 Ensure user_id is a valid UUID
            user_id = str(uuid.UUID(user_id))

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e:
            print("❌ JWT Decode Error:", str(e))
            return jsonify({"error": "Invalid token!"}), 401
        except ValueError:
            return jsonify({"error": "Invalid UUID format!"}), 401

        return f(user_id, *args, **kwargs)

    return decorated