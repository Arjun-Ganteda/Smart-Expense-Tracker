import tomllib
from pathlib import Path


# Locate the main project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Locate Streamlit secrets file
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"


def load_settings():

    if not SECRETS_FILE.exists():
        raise FileNotFoundError(
            "Supabase secrets.toml file not found."
        )

    with open(SECRETS_FILE, "rb") as file:
        secrets = tomllib.load(file)

    required_keys = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SECRET_KEY"
    ]

    for key in required_keys:
        if not secrets.get(key):
            raise ValueError(
                f"Missing configuration: {key}"
            )

    return secrets


settings = load_settings()

SUPABASE_URL = settings["SUPABASE_URL"]
SUPABASE_KEY = settings["SUPABASE_KEY"]
SUPABASE_SECRET_KEY = settings["SUPABASE_SECRET_KEY"]