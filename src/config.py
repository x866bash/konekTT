import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FLASK_SECRET = os.getenv("FLASK_SECRET", "dev-secret")
    CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
    CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
    REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:5000/auth/tiktok/callback")
    SCOPES = os.getenv("SCOPES", "user.info.basic")
    PORT = int(os.getenv("PORT", "5000"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tiktok_users.db")

settings = Settings()
