from flask import Flask, jsonify
from flask_cors import CORS

from .routes import auth_api


app = Flask(__name__)

# Allow requests from the local Streamlit frontend
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:8501",
                "http://127.0.0.1:8501"
            ]
        }
    }
)


# Register authentication routes
app.register_blueprint(auth_api)


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "success",
        "message": "Smart Expense Tracker API is running!"
    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "application": "Smart Expense Tracker",
        "backend": "Flask"
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )  