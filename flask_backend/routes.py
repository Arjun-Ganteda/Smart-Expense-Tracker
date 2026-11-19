import re
from flask import Blueprint, request, jsonify
from supabase import create_client

from .config import SUPABASE_URL, SUPABASE_KEY


auth_api = Blueprint(
    "auth_api",
    __name__,
    url_prefix="/api/auth"
)


def get_supabase_client():
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


def validate_username(username):

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_.-]{3,24}",
            username
        )
    )


def internal_email(username):

    return (
        username.strip().lower()
        + "@login.smart-expense-tracker.com"
    )


# --------------------------------
# USER REGISTRATION API
# --------------------------------

@auth_api.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    if not isinstance(username, str):
        return jsonify({
            "status": "error",
            "message": "Invalid username."
        }), 400

    username = username.strip()

    if not validate_username(username):
        return jsonify({
            "status": "error",
            "message": "Username must contain 3-24 valid characters."
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters."
        }), 400

    try:

        client = get_supabase_client()

        response = client.auth.sign_up({
            "email": internal_email(username),
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })

        if not response.user:
            return jsonify({
                "status": "error",
                "message": "Registration could not be completed."
            }), 400

        return jsonify({
            "status": "success",
            "message": "Registration successful. Please log in."
        }), 201

    except Exception:

        return jsonify({
            "status": "error",
            "message": "Registration failed. Please check your details."
        }), 400


# --------------------------------
# USER LOGIN API
# --------------------------------

@auth_api.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    if not isinstance(username, str) or not validate_username(username):
        return jsonify({
            "status": "error",
            "message": "Invalid username or password."
        }), 401

    if not isinstance(password, str) or not password:
        return jsonify({
            "status": "error",
            "message": "Invalid username or password."
        }), 401

    client = None

    try:

        client = get_supabase_client()

        response = client.auth.sign_in_with_password({
            "email": internal_email(username),
            "password": password
        })

        if not response.user or not response.session:
            return jsonify({
                "status": "error",
                "message": "Invalid username or password."
            }), 401

        profile_result = (
            client.table("profiles")
            .select("id, username, role, status")
            .eq("id", str(response.user.id))
            .maybe_single()
            .execute()
        )

        profile = profile_result.data

        if not profile or profile.get("status") != "active":

            try:
                client.auth.sign_out()
            except Exception:
                pass

            return jsonify({
                "status": "error",
                "message": "Account is inactive or unavailable."
            }), 403

        return jsonify({
            "status": "success",
            "message": "Login successful.",
            "user": {
                "user_id": str(response.user.id),
                "username": profile["username"],
                "role": profile["role"]
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        }), 200

    except Exception:

        if client:
            try:
                client.auth.sign_out()
            except Exception:
                pass

        return jsonify({
            "status": "error",
            "message": "Invalid username or password."
        }), 401