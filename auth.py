import re
import streamlit as st
from supabase import create_client


# -------------------------------
# SUPABASE CONFIGURATION
# -------------------------------

def _settings():
    return (
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
        st.secrets["SUPABASE_SECRET_KEY"],
    )


def get_client(access_token=None, refresh_token=None):
    url, anon_key, _ = _settings()

    client = create_client(url, anon_key)

    if access_token and refresh_token:
        client.auth.set_session(
            access_token,
            refresh_token
        )

    return client


def get_admin_client():
    url, _, secret_key = _settings()

    return create_client(url, secret_key)


# -------------------------------
# USERNAME VALIDATION
# -------------------------------

def _normalise_username(username):
    return username.strip().lower()


def _internal_email(username):
    return (
        f"{_normalise_username(username)}"
        "@login.smart-expense-tracker.com"
    )


def validate_username(username):
    if not isinstance(username, str):
        return False

    username = username.strip()

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_.-]{3,24}",
            username
        )
    )


# -------------------------------
# USER REGISTRATION
# -------------------------------

def register_user(username, password):

    if not validate_username(username):
        return False, (
            "Username must contain 3–24 characters. "
            "Only letters, numbers, dots, underscores "
            "and hyphens are allowed."
        )

    if not isinstance(password, str) or len(password) < 8:
        return False, "Password must contain at least 8 characters."

    username = username.strip()

    try:
        client = get_client()

        response = client.auth.sign_up({
            "email": _internal_email(username),
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })

        if not response.user:
            return False, "Registration could not be completed."

        return True, "Registration successful. Please log in."

    except Exception:
        return False, (
            "Registration failed. Username may already exist "
            "or Supabase configuration needs checking."
        )


# -------------------------------
# USER LOGIN
# -------------------------------

def login_user(username, password):

    if not validate_username(username):
        return None

    if not isinstance(password, str) or not password:
        return None

    client = None

    try:
        client = get_client()

        response = client.auth.sign_in_with_password({
            "email": _internal_email(username),
            "password": password
        })

        if not response.user or not response.session:
            return None

        profile_result = (
            client.table("profiles")
            .select("id, username, role, status")
            .eq("id", str(response.user.id))
            .maybe_single()
            .execute()
        )

        profile = profile_result.data

        if not profile:
            client.auth.sign_out()
            return None

        if profile.get("status") != "active":
            client.auth.sign_out()
            return None

        return {
            "user_id": str(response.user.id),
            "username": profile["username"],
            "role": profile["role"],
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:

        if client:
            try:
                client.auth.sign_out()
            except Exception:
                pass

        return None


# -------------------------------
# USER ROLE
# -------------------------------

def get_user_role(user_id, client):

    try:
        result = (
            client.table("profiles")
            .select("role")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )

        return (
            result.data.get("role")
            if result.data else None
        )

    except Exception:
        return None


# -------------------------------
# ADMIN VERIFICATION
# -------------------------------

def is_admin(client):

    try:
        result = client.rpc("is_admin").execute()

        return bool(result.data)

    except Exception:
        return False


# -------------------------------
# ADMIN PASSWORD RESET
# -------------------------------

def admin_reset_password(
    client,
    target_user_id,
    new_password
):

    if not is_admin(client):
        return False, "Admin access required."

    if not isinstance(new_password, str) or len(new_password) < 8:
        return False, "Password must contain at least 8 characters."

    try:

        target = (
            client.table("profiles")
            .select("id, role")
            .eq("id", target_user_id)
            .maybe_single()
            .execute()
        )

        if not target.data:
            return False, "User account not found."

        if target.data.get("role") != "user":
            return False, (
                "Only ordinary user accounts can be reset here."
            )

        admin_client = get_admin_client()

        admin_client.auth.admin.update_user_by_id(
            target_user_id,
            {
                "password": new_password
            }
        )

        return True, "Password reset successfully."

    except Exception:
        return False, (
            "Password reset failed. Please try again."
        )