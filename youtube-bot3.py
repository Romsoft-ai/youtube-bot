import os
import pickle
import time
import datetime
from google.auth.transport.requests import Request
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
VIDEO_ID = "w-T_qMMFiLg"  
THUMBNAIL_PATH = "miniatures/miniature_essaie.png"

# Authentification persistante (token)
def get_credentials():
    # Choix du projet selon l'heure
    now = datetime.datetime.now()
    hour = now.hour
    if 5 <= hour < 14:
        client_secrets_file = "client_secret_1.json"
        token_file = "token_1.pickle"
    else:
        client_secrets_file = "client_secret_2.json"
        token_file = "token_2.pickle"
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_console()
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)
    return creds

def to_bold_unicode(text):
    # Lettres et chiffres gras Unicode (math bold)
    bold_map = {
        **{chr(i): chr(0x1D400 + i - ord('A')) for i in range(ord('A'), ord('Z')+1)},
        **{chr(i): chr(0x1D41A + i - ord('a')) for i in range(ord('a'), ord('z')+1)},
        **{chr(i): chr(0x1D7CE + i - ord('0')) for i in range(ord('0'), ord('9')+1)}
    }
    return ''.join(bold_map.get(c, c) for c in text)

def generate_dynamic_thumbnail(view_count):
    """
    Génère une miniature dynamique à partir de background.png pour les vues >= 10 000
    Texte : Cette vidéo va faire\nXXk vues
    Palier de 100 vues, format 10k, 10.5k, 11k, etc.
    """
    background_path = "miniatures/background.png"
    img = Image.open(background_path).convert("RGBA")
    font_path = "OpenSans-Bold.ttf"  # Mets le chemin correct si besoin
    font_size = 60
    font = ImageFont.truetype(font_path, font_size)

    # Calcul du palier de 100
    palier = (view_count // 100) * 100
    # Format k (ex: 10k, 10.5k, 11k...)
    if palier % 1000 == 0:
        vues_str = f"{palier // 1000}k"
    else:
        vues_str = f"{palier / 1000:.1f}k"
    texte = f"Cette vidéo va faire\n{vues_str} vues"

    # Position du texte (à ajuster si besoin)
    x = 150
    y = 550
    img_draw = ImageDraw.Draw(img)
    img_draw.multiline_text((x, y), texte, font=font, fill="black", align="center", spacing=10)

    output_path = f"miniatures/background{palier}.png"
    img.save(output_path)
    return output_path

def get_thumbnail_path(view_count):
    view_count = int(view_count)
    if view_count < 1000:
        palier = (view_count // 100 + 1) * 100
        return f"miniatures/{palier}.png"
    else:
        # Générer la miniature dynamique et retourner son chemin
        return generate_dynamic_thumbnail(view_count)

def get_thumbnail_palier(view_count):
    view_count = int(view_count)
    if view_count < 1000:
        palier = (view_count // 100 + 1) * 100
    else:
        palier = (view_count // 100) * 100
    return palier

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
    view_count = int(response["items"][0]["statistics"]["viewCount"])
    snippet = response["items"][0]["snippet"]
    current_description = snippet["description"]
    current_tags = snippet.get("tags", [])
    current_category = snippet.get("categoryId", "27")
    print(f"Nombre de vues: {view_count}")
    base_title = f"Elle va faire {view_count} vues pour être précis"
    new_title = to_bold_unicode(base_title)
    # Choisir la miniature selon le palier
    thumbnail_path = get_thumbnail_path(view_count)
    # Gestion du fichier vues.txt
    vues_file = "vues.txt"
    palier_actuel = get_thumbnail_palier(view_count)
    palier_prec = 700
    if os.path.exists(vues_file):
        with open(vues_file, "r") as f:
            try:
                palier_prec = int(f.read().strip())
            except Exception:
                palier_prec = None
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
    # Mettre à jour la miniature uniquement si le palier a changé
    if palier_prec != palier_actuel:
        try:
            media = MediaFileUpload(thumbnail_path)
            thumbnail_request = youtube.thumbnails().set(
                videoId=VIDEO_ID,
                media_body=media
            )
            thumbnail_response = thumbnail_request.execute()
            print(f"Miniature mise à jour avec {thumbnail_path}")
            # Écrire le nouveau palier dans vues.txt
            with open(vues_file, "w") as f:
                f.write(str(palier_actuel))
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la miniature : {e}")
    else:
        print("Miniature inchangée (palier identique).")

if __name__ == "__main__":
    update_title_and_thumbnail()
