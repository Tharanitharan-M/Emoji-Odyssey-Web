from flask import Blueprint, request, jsonify
from config import supabase_client

auth_blueprint = Blueprint("auth", __name__)

# 🔹 Signup API
@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Sign up user in Supabase
        response = supabase_client.auth.sign_up({"email": email, "password": password})

        if response.user is None:
            return jsonify({"error": "Signup failed. User may already exist."}), 400

        return jsonify({"message": "User created successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Login API
@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Authenticate the user with Supabase
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})

        if response.user is None or response.session is None:
            return jsonify({"error": "Invalid email or password"}), 401

        # Return JWT Token
        return jsonify({"token": response.session.access_token})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
