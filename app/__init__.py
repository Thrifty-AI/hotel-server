from .socket import socketio
from flask import Flask
from flask_cors import CORS
from .routes import register_routes
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(
        app,
        # supports_credentials=True,
        # resources={r"/*": {"origins": json.loads(os.environ.get("CLIENT_URL", "[]"))}},
    )

    register_routes(app)

    app.config["CORS_HEADERS"] = "Content-Type"

    return app
