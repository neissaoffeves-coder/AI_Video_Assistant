# youtube_uploader.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Ce fichier est généré par la Google Cloud Console quand vous créez des identifiants OAuth2
import streamlit as st
from google.oauth2.credentials import Credentials
# ... autres imports

def get_authenticated_service():
    """Authentifie l'utilisateur en utilisant les secrets de Streamlit."""
    # On récupère les secrets stockés dans Streamlit
    client_config = {
        "installed": {
            "client_id": st.secrets["installed"]["client_id"],
            "project_id": st.secrets["installed"]["project_id"],
            "auth_uri": st.secrets["installed"]["auth_uri"],
            "token_uri": st.secrets["installed"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["installed"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["installed"]["client_secret"],
            "redirect_uris": st.secrets["installed"]["redirect_uris"]
        }
    }
    # Note: L'authentification 'run_local_server' ne fonctionne pas sur le cloud.
    # Pour une vraie app déployée, il faudrait un flux web plus complexe.
    # Pour l'instant, cette partie posera problème au déploiement.
    # Une solution plus simple pour commencer serait de désactiver la fonctionnalité de publication YouTube.

    # ***SOLUTION SIMPLIFIÉE POUR UN PREMIER DÉPLOIEMENT***
    # Pour l'instant, commentons cette partie pour que l'app puisse se déployer
    st.warning("La publication sur YouTube est désactivée dans la version en ligne.")
    return None

def upload_to_youtube(video_path, title, description, tags):
    youtube = get_authenticated_service()
    if youtube is None:
        return None # On arrête la fonction si le service n'est pas dispo

    # ... le reste du code

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
