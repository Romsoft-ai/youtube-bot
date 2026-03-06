import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pickle
import time
from google.auth.transport.requests import Request

# Chemin vers le fichier client secret
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "token.pickle"

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

def update_title_loop():
    creds = get_credentials()
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=creds)
    # Récupérer le nombre de vues, la description ET les tags actuels
    request = youtube.videos().list(
        part="statistics,snippet",
        id="sko6ULR8M1M"
    )
    response = request.execute()
    view_count = response["items"][0]["statistics"]["viewCount"]
    snippet = response["items"][0]["snippet"]
    current_description = snippet["description"]
    current_tags = snippet.get("tags", [])
    current_category = snippet.get("categoryId", "27")
    print(f"Nombre de vues: {view_count}")
    new_title = f"Cette video va faire {view_count} vues"
    update_request = youtube.videos().update(
        part="snippet",
        body={
            "id": "sko6ULR8M1M",
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

if __name__ == "__main__":
    update_title_loop()
