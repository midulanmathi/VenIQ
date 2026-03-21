from flask import Flask
from flask_cors import CORS
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.mood import mood_bp
    from app.routes.music import music_bp

    app.register_blueprint(mood_bp, url_prefix="/api/mood")
    app.register_blueprint(music_bp, url_prefix="/api/music")

    return app
