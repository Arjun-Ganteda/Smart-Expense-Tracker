import os
import tomllib
from pathlib import Path

SECRETS_PATH = (
    Path(__file__).resolve().parents[1]
    / ".streamlit"
    / "secrets.toml"
)

secrets = {}

if SECRETS_PATH.exists():
    with open(SECRETS_PATH, "rb") as file:
        secrets = tomllib.load(file)

SUPABASE_URL = (
    os.getenv("SUPABASE_URL")
    or secrets.get("SUPABASE_URL")
)

SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or secrets.get("SUPABASE_KEY")
)

SUPABASE_SECRET_KEY = (
    os.getenv("SUPABASE_SECRET_KEY")
    or secrets.get("SUPABASE_SECRET_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing Supabase URL or publishable key."
 )