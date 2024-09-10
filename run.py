from app import create_app, socketio
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    # with app.app_context():
    socketio.run(app, debug=True, port=8080)
