import secrets, time
from flask import Blueprint, redirect, request, session, url_for, jsonify, render_template, flash
from .oauth import build_auth_url, exchange_code_for_token, fetch_user_info, refresh_access_token
from .db import get_session, TikTokUser

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/login/tiktok")
def login_tiktok():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    return redirect(build_auth_url(state))

@bp.get("/auth/tiktok/callback")
def tiktok_callback():
    if request.args.get("state") != session.get("oauth_state"):
        return "Invalid state", 400
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    tok = exchange_code_for_token(code)
    access_token = tok.get("access_token")
    refresh_token = tok.get("refresh_token")
    expires_in = int(tok.get("expires_in", 0))
    expires_at = int(time.time()) + expires_in

    user_info = fetch_user_info(access_token)
    open_id = user_info.get("open_id")
    display_name = user_info.get("display_name", "")
    avatar_url = user_info.get("avatar_url", "")

    with get_session() as s:
        user = s.query(TikTokUser).filter_by(open_id=open_id).one_or_none()
        if not user:
            user = TikTokUser(open_id=open_id)
        user.display_name = display_name
        user.avatar_url = avatar_url
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expires_at = expires_at
        s.add(user)
        s.commit()

    session["open_id"] = open_id
    flash("Login berhasil", "success")
    return redirect(url_for("main.me"))

@bp.get("/me")
def me():
    open_id = session.get("open_id")
    if not open_id:
        return {"message": "Belum login. Pergi ke /login/tiktok"}, 401
    with get_session() as s:
        user = s.query(TikTokUser).filter_by(open_id=open_id).one_or_none()
        if not user:
            return {"message": "User tidak ditemukan"}, 404
        return {
            "open_id": user.open_id,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url
        }

@bp.get("/users")
def users():
    with get_session() as s:
        rows = s.query(TikTokUser).order_by(TikTokUser.id.desc()).all()
        return jsonify([{
            "open_id": r.open_id,
            "display_name": r.display_name,
            "avatar_url": r.avatar_url,
            "token_expires_at": r.token_expires_at
        } for r in rows])

@bp.post("/admin/refresh/<open_id>")
def refresh_one(open_id: str):
    with get_session() as s:
        user = s.query(TikTokUser).filter_by(open_id=open_id).one_or_none()
        if not user or not user.refresh_token:
            return {"message": "User atau refresh_token tidak ditemukan"}, 404
        data = refresh_access_token(user.refresh_token)
        if not data:
            return {"message": "Gagal refresh token"}, 400
        user.access_token = data.get("access_token", user.access_token)
        user.refresh_token = data.get("refresh_token", user.refresh_token)
        user.token_expires_at = int(time.time()) + int(data.get("expires_in", 0))
        s.add(user)
        s.commit()
        return {"message": "OK", "open_id": open_id, "expires_at": user.token_expires_at}

@bp.post("/admin/refresh_all")
def refresh_all():
    updated = 0
    with get_session() as s:
        users = s.query(TikTokUser).all()
        now = int(time.time())
        for u in users:
            if not u.refresh_token:
                continue
            data = refresh_access_token(u.refresh_token)
            if not data:
                continue
            u.access_token = data.get("access_token", u.access_token)
            u.refresh_token = data.get("refresh_token", u.refresh_token)
            u.token_expires_at = now + int(data.get("expires_in", 0))
            s.add(u)
            updated += 1
        s.commit()
    return {"message": "OK", "updated": updated}
