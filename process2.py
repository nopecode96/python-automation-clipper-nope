import os
import sys
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINAL_DIR = os.path.join(BASE_DIR, "final")
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secrets.json")
TOKEN_PICKLE_FILE = os.path.join(BASE_DIR, "token.pickle")

# Scope izin untuk mengunggah video dan thumbnail ke YouTube
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_authenticated_service():
    """Mengurus autentikasi OAuth 2.0 (hanya perlu login browser sekali saja)"""
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"❌ Error: File {CLIENT_SECRETS_FILE} tidak ditemukan!")
                print("💡 Harap download 'client_secrets.json' dari Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Simpan sesi login agar tidak perlu login ulang di eksekusi berikutnya
        with open(TOKEN_PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def set_video_thumbnail(youtube, video_id, thumbnail_path):
    """
    Mengunggah fail thumbnail kustom ke video YouTube yang sudah dibuat.
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        print(f"ℹ️ Thumbnail tidak ditemukan atau tidak tersedia: {thumbnail_path}")
        return False

    print(f"\n[THUMBNAIL] 🖼️ Mengunggah custom thumbnail ke YouTube...")
    try:
        media_thumb = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media_thumb
        ).execute()
        print(f"✅ Thumbnail berhasil dipasang pada video {video_id}!")
        return True
    except Exception as e:
        print(f"⚠️ Gagal memasang custom thumbnail (mungkin memerlukan verifikasi nomor HP pada channel YouTube): {e}")
        return False

def upload_to_youtube(video_path, title, description, tags=None, privacy_status="private", thumbnail_path=None):
    """
    Mengunggah video ke YouTube dan memasang custom thumbnail jika tersedia.
    Status default: 'private' (atau 'public' / 'unlisted')
    """
    print(f"\n[UPLOAD] 🚀 Menghubungkan ke YouTube API...")
    youtube = get_authenticated_service()
    if not youtube:
        return False

    if not os.path.exists(video_path):
        print(f"❌ File video tidak ditemukan: {video_path}")
        return False

    # Pastikan ada tag #Shorts di judul/deskripsi agar terbaca sebagai Shorts
    if "#shorts" not in title.lower():
        title = f"{title} #Shorts"

    body = {
        "snippet": {
            "title": title[:100],  # Maksimal 100 karakter
            "description": description,
            "tags": tags or ["Shorts", "AI", "Technology", "NopeCode"],
            "categoryId": "28"      # Kategori 28 = Science & Technology
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"📤 Sedang mengunggah: {os.path.basename(video_path)}")
    print(f"📌 Judul: {title}")
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"\n🎉 UPLOAD BERHASIL!")
    print(f"🔗 Link Video: https://www.youtube.com/shorts/{video_id}")
    print(f"🔒 Status: {privacy_status.upper()}")

    # Pasang custom thumbnail jika tersedia
    if thumbnail_path:
        set_video_thumbnail(youtube, video_id, thumbnail_path)

    return video_id

def run_process2(privacy="private"):
    metadata_json = os.path.join(FINAL_DIR, "latest_video.json")
    if not os.path.exists(metadata_json):
        print("❌ Metadata video terbaru (latest_video.json) tidak ditemukan di folder final/.")
        print("💡 Pastikan process1.py sudah selesai dijalankan.")
        return False

    with open(metadata_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    video_id = upload_to_youtube(
        video_path=data["video_path"],
        title=data["title"],
        description=data["description"],
        tags=data.get("tags", []),
        privacy_status=privacy,
        thumbnail_path=data.get("thumbnail_path")
    )
    return bool(video_id)

if __name__ == "__main__":
    # Default private agar aman dicek dulu di YouTube Studio Anda
    run_process2(privacy="private")