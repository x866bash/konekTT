from flask import Flask
from .config import settings
from .routes import bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.FLASK_SECRET
    app.register_blueprint(bp)
    return app

def main():
    app = create_app()
    app.run(host="0.0.0.0", port=settings.PORT, debug=True)

if __name__ == "__main__":
    main()
