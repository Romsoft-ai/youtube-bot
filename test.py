import os

import time

import pickle

import datetime

from PIL import Image, ImageDraw, ImageFont

from googleapiclient.discovery import build

from googleapiclient.http import MediaFileUpload



# IDs des vidéos sources et destination

SOURCE_VIDEO_ID = "cLMjNDPRgAA"

DEST_VIDEO_ID = "cLMjNDPRgAA"

# Coordonnées et info du texte sur la miniature

X_COORD = 730

Y_COORD = 250

TAILLE_POLICE = 120

ATTENTE_MINUTES = 8  # Titre mis à jour toutes les..



dernier_texte_miniature = ""



def get_authenticated_service():

    maintenant = datetime.datetime.now()

    heure = maintenant.hour

    # Rotation 12h/12h

    if 8 <= heure < 20:

        token_file = "token_2.pickle"

        label = "PROJET n°2 (JOUR)"

    else:

        token_file = "token.pickle"

        label = "PROJET n°1 (NUIT)"



    if not os.path.exists(token_file):

        raise Exception(f"{token_file} manquant !")

    with open(token_file, "rb") as token:

        creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:

        from google.auth.transport.requests import Request

        creds.refresh(Request())

    return build("youtube", "v3", credentials=creds)



def get_thumbnail_logic(views):

    """Gère les miniatures : message fixe sous 1000 vues, puis paliers de 100 vues"""

    if views < 90:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 100 vues"

    

    elif views < 190:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 200 vues"

    

    elif views < 290:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 300 vues"

    

    elif views < 390:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 400 vues"

    

    elif views < 490:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 500 vues"

    

    elif views < 590:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 600 vues"

    

    elif views < 690:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 700 vues"

    

    elif views < 790:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 800 vues"

    

    elif views < 890:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 900 vues"

    

    elif views < 1000:

        # Texte fixe pour économiser le quota et le rate limit sous 1000 vues

        return "Cette vidéo va faire\nmoins de 1 000 vues"

    

    elif views < 10000:

        # Entre 1k et 10k : On garde la virgule

        valeur_k = (views // 100) / 10.0

        str_k = str(valeur_k).replace('.', ',')

        return f"Cette vidéo va faire\n{str_k}k vues"

    

    elif views < 1000000:

        # Entre 10k et 999k : Pas de virgule

        valeur_k = views // 1000

        return f"Cette vidéo va faire\n{valeur_k}k vues"

    

    else:

        # Arrondi à l'inférieur pour les millions

        valeur_m = (views // 100000) / 10.0

        str_m = str(valeur_m).replace('.', ',')

        return f"Cette vidéo va faire\n{str_m}M de vues"



def create_thumbnail(texte):

    try:

        img = Image.open("background.jpg")

    except:

        img = Image.new('RGB', (1280, 720), color=(220, 220, 220))

    

    draw = ImageDraw.Draw(img)

    try:

        font = ImageFont.truetype("arialbd.ttf", TAILLE_POLICE)

    except:

        font = ImageFont.load_default()



    draw.text((X_COORD, Y_COORD), texte, font=font, fill="black", align="center", spacing=20)

    img.save("current_thumbnail.jpg")

    return "current_thumbnail.jpg"



def update_loop():

    global dernier_texte_miniature

    

    while True:

        try:

            youtube = get_authenticated_service()

            print(f"\n--- CYCLE ({datetime.datetime.now().strftime('%H:%M:%S')}) ---")

            

            # 1. Lecture

            source_data = youtube.videos().list(part="statistics", id=SOURCE_VIDEO_ID).execute()

            views = int(source_data["items"][0]["statistics"]["viewCount"])

            

            # 2. TITRE

            vues_formatees = f"{views:,}".replace(",", " ")

            nouveau_titre = f"Elle va faire {vues_formatees} vues pour être précis"

            

            dest_data = youtube.videos().list(part="snippet", id=DEST_VIDEO_ID).execute()

            category_id = dest_data["items"][0]["snippet"]["categoryId"]



            youtube.videos().update(

                part="snippet",

                body={"id": DEST_VIDEO_ID, "snippet": {"title": nouveau_titre, "categoryId": category_id}}

            ).execute()

            print(f"TITRE : {nouveau_titre}")



            # 3. MINIATURE PAR PALIER

            texte_miniature = get_thumbnail_logic(views)

            

            if texte_miniature != dernier_texte_miniature:

                print(f"Nouveau palier : {texte_miniature}")

                thumb_path = create_thumbnail(texte_miniature)

                youtube.thumbnails().set(

                    videoId=DEST_VIDEO_ID,

                    media_body=MediaFileUpload(thumb_path)

                ).execute()

                dernier_texte_miniature = texte_miniature

                print("MINIATURE actualisée.")

            else:

                print("Le palier n'a pas changé. Miniature conservée.")



        except Exception as e:

            print(f"Erreur : {e}")

            time.sleep(60)

            continue



        time.sleep(ATTENTE_MINUTES * 60)



if name == "__main__":

    update_loop()