# TikTok Login Kit (OAuth 2.0) – Flask Example

Contoh aplikasi Flask untuk **Login dengan TikTok** (OAuth 2.0) yang mendukung banyak akun.
- Simpan token & profil ke **SQLite**
- **Refresh token** manual atau massal
- Struktur proyek rapi (`src/`), `.env` untuk konfigurasi
- UI sederhana (template Jinja)

## Fitur
- Login via TikTok (OAuth v2)
- Simpan user (`open_id`, `display_name`, `avatar_url`) + token (`access_token`, `refresh_token`, `expires_at`)
- Lihat user aktif (`/me`) & daftar semua user (`/users`)
- Refresh token per user atau semua user
- Tombol **Login with TikTok** di halaman utama

## Persiapan
1. Buat app di [TikTok for Developers](https://developers.tiktok.com/).
2. Aktifkan **Login Kit** dan catat **Client Key** & **Client Secret**.
3. Daftarkan **Redirect URI** yang sama persis dengan `.env` (contoh: `http://localhost:5000/auth/tiktok/callback`).

## Konfigurasi
Copy file `.env.example` menjadi `.env` lalu isi nilainya:
```bash
cp .env.example .env
# lalu edit .env
```

### Variabel `.env`
- `FLASK_SECRET` – secret key Flask
- `TIKTOK_CLIENT_KEY` – client key TikTok
- `TIKTOK_CLIENT_SECRET` – client secret TikTok
- `TIKTOK_REDIRECT_URI` – redirect URI yang terdaftar di TikTok
- `SCOPES` – default: `user.info.basic`
- `PORT` – port aplikasi (default 5000)
- `DATABASE_URL` – default sqlite file: `sqlite:///tiktok_users.db`

## Menjalankan secara lokal
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# konfigurasi env
cp .env.example .env
# isi nilai di .env, lalu:
python -m src.app
```

Buka `http://localhost:5000` lalu klik **Login with TikTok**.

## Endpoint Utama
- `GET /` – halaman depan + tombol login
- `GET /login/tiktok` – mulai OAuth
- `GET /auth/tiktok/callback` – callback, tukar code → token, ambil profil, simpan
- `GET /me` – user aktif dari session
- `GET /users` – daftar semua user dari database
- `POST /admin/refresh/<open_id>` – refresh token user tertentu
- `POST /admin/refresh_all` – refresh token semua user (yang punya refresh_token)

## Catatan
- Pastikan **Redirect URI** *exact match* dengan yang kamu daftarkan di TikTok.
- Token akan **kedaluwarsa**; gunakan endpoint refresh di atas atau jadwalkan cron/job.

## Deploy cepat
### Docker
```bash
docker build -t tiktok-login-kit .
docker run -p 5000:5000 --env-file .env tiktok-login-kit
```

### Render/Fly/Heroku (opsional)
Gunakan `Procfile`. Pastikan mengatur variabel env di dashboard layanan yang kamu pakai.

## Lisensi
MIT
