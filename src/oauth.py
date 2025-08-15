import time
import requests
from typing import Optional, Dict, Any
from .config import settings

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
USERINFO_URL = "https://open.tiktokapis.com/v2/user/info/"

def build_auth_url(state: str) -> str:
    from urllib.parse import urlencode
    params = {
        "client_key": settings.CLIENT_KEY,
        "response_type": "code",
        "scope": settings.SCOPES,
        "redirect_uri": settings.REDIRECT_URI,
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> Dict[str, Any]:
    data = {
        "client_key": settings.CLIENT_KEY,
        "client_secret": settings.CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.REDIRECT_URI,
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=20)
    resp.raise_for_status()
    return resp.json().get("data", {})

def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    data = {
        "client_key": settings.CLIENT_KEY,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=20)
    if resp.status_code != 200:
        return None
    return resp.json().get("data", {})

def fetch_user_info(access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "open_id,display_name,avatar_url"}
    resp = requests.get(USERINFO_URL, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("user", {})
