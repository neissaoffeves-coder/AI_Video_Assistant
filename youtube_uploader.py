# youtube_uploader.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Ce fichier est généré par la Google Cloud Console quand vous créez des identifiants OAuth2
# LIGNE À CHANGER
CLIENT_SECRETS_FILE = "client_secrets.json"

def get_authenticated_service():
    """Authentifie l'utilisateur et retourne un objet service pour l'API YouTube."""
    # LIGNE À CHANGER
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def upload_to_youtube(video_path, title, description, tags):
    """
    Poste une vidéo sur YouTube.
    """
    youtube = get_authenticated_service()
    
    # Le titre ou la description DOIT contenir #Shorts pour être reconnu comme tel
    full_description = f"{description}\n\n{tags}"
    if "#shorts" not in title.lower() and "#shorts" not in full_description.lower():
        title += " #Shorts"

    body = {
        "snippet": {
            "title": title,
            "description": full_description,
            "tags": tags.replace("#", "").split(),
            "categoryId": "22" # Voir la doc de l'API pour les catégories
        },
        "status": {
            "privacyStatus": "private" # "private", "unlisted" ou "public"
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = request.execute()
    print(f"Vidéo postée ! ID de la vidéo : {response['id']}")
    return response['id']
