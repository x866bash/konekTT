# app.py
import os, sqlite3, secrets, time
from urllib.parse import urlencode
from flask import Flask, redirect, request, session, url_for, jsonify
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # ganti di produksi

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")  # ex: https://yourapp.com/auth/tiktok/callback
SCOPES = "user.info.basic"  # tambah scope sesuai approval kamu

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
USERINFO_URL = "https://open.tiktokapis.com/v2/user/info/"

DB = "users.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            open_id TEXT UNIQUE,
            display_name TEXT,
            avatar_url TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at INTEGER
        )""")
init_db()

def save_user(u):
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            INSERT INTO tiktok_users(open_id, display_name, avatar_url, access_token, refresh_token, token_expires_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(open_id) DO UPDATE SET
              display_name=excluded.display_name,
              avatar_url=excluded.avatar_url,
              access_token=excluded.access_token,
              refresh_token=excluded.refresh_token,
              token_expires_at=excluded.token_expires_at
        """, (u["open_id"], u["display_name"], u["avatar_url"], u["access_token"], u["refresh_token"], u["token_expires_at"]))

@app.route("/")
def index():
    return {
        "routes": {
            "/login/tiktok": "Mulai login dengan TikTok",
            "/me": "Lihat profil akun yang sedang di session",
            "/users": "Lihat semua akun yang pernah login (disimpan di DB)"
        }
    }

@app.route("/login/tiktok")
def login_tiktok():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    params = {
        "client_key": TIKTOK_CLIENT_KEY,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }
    return redirect(f"{AUTH_URL}?{urlencode(params)}")

@app.route("/auth/tiktok/callback")
def tiktok_callback():
    if request.args.get("state") != session.get("oauth_state"):
        return "Invalid state", 400
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    # Tukar code → token
    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    token_resp = requests.post(TOKEN_URL, data=data, timeout=20)
    if token_resp.status_code != 200:
        return f"Token error: {token_resp.text}", 400
    tok = token_resp.json().get("data", {})
    access_token = tok.get("access_token")
    refresh_token = tok.get("refresh_token")
    expires_in = tok.get("expires_in", 0)
    expires_at = int(time.time()) + int(expires_in)

    # Ambil user info
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "open_id,display_name,avatar_url"}
    ui_resp = requests.get(USERINFO_URL, headers=headers, params=params, timeout=20)
    if ui_resp.status_code != 200:
        return f"User info error: {ui_resp.text}", 400
    user_data = ui_resp.json().get("data", {}).get("user", {})
    user = {
        "open_id": user_data.get("open_id"),
        "display_name": user_data.get("display_name"),
        "avatar_url": user_data.get("avatar_url"),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expires_at": expires_at
    }
    save_user(user)
    # Simpan siapa yang "aktif" di session (opsional)
    session["open_id"] = user["open_id"]
    return redirect(url_for("me"))

@app.route("/me")
def me():
    open_id = session.get("open_id")
    if not open_id:
        return {"message": "Belum login. Pergi ke /login/tiktok"}, 401
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT open_id, display_name, avatar_url FROM tiktok_users WHERE open_id = ?", (open_id,)).fetchone()
        if not row:
            return {"message": "User tidak ditemukan"}, 404
        return {"open_id": row[0], "display_name": row[1], "avatar_url": row[2]}

@app.route("/users")
def users():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT open_id, display_name, avatar_url FROM tiktok_users ORDER BY id DESC").fetchall()
        return jsonify([{"open_id": r[0], "display_name": r[1], "avatar_url": r[2]} for r in rows])

if __name__ == "__main__":
    # Jalankan: FLASK_SECRET=... TIKTOK_CLIENT_KEY=... TIKTOK_CLIENT_SECRET=... TIKTOK_REDIRECT_URI=... python app.py
    app.run(debug=True, host="0.0.0.0", port=5000)
