import os
import pickle
import time
from google.auth.transport.requests import Request
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "token.pickle"
VIDEO_ID = "sko6ULR8M1M"
THUMBNAIL_PATH = "miniatures/miniature_essaie.png"

# Authentification persistante (token)
def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds

def update_title_and_thumbnail():
    creds = get_credentials()
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=creds)
    # Récupérer le nombre de vues, la description, les tags et la catégorie
    request = youtube.videos().list(
        part="statistics,snippet",
        id=VIDEO_ID
    )
    response = request.execute()
    view_count = response["items"][0]["statistics"]["viewCount"]
    snippet = response["items"][0]["snippet"]
    current_description = snippet["description"]
    current_tags = snippet.get("tags", [])
    current_category = snippet.get("categoryId", "27")
    print(f"Nombre de vues: {view_count}")
    new_title = f"Cette video va faire {view_count} vues"
    # Mettre à jour le titre
    update_request = youtube.videos().update(
        part="snippet",
        body={
            "id": VIDEO_ID,
            "snippet": {
                "title": new_title,
                "description": current_description,
                "tags": current_tags,
                "categoryId": current_category
            }
        }
    )
    update_response = update_request.execute()
    print(f"Titre mis à jour: {new_title}")
    # Mettre à jour la miniature
    media = MediaFileUpload(THUMBNAIL_PATH)
    thumbnail_request = youtube.thumbnails().set(
        videoId=VIDEO_ID,
        media_body=media
    )
    thumbnail_response = thumbnail_request.execute()
    print(f"Miniature mise à jour avec {THUMBNAIL_PATH}")

if __name__ == "__main__":
    update_title_and_thumbnail()
