# main.py
import streamlit as st
import os
from video_processor import process_video
from content_generator import generate_creative_content
from youtube_uploader import upload_to_youtube

st.set_page_config(layout="wide")
st.title("🤖 Assistant de Création de Contenu Vidéo")

# --- Section Upload ---
st.header("1. Importez votre vidéo longue")
uploaded_file = st.file_uploader("Choisissez un fichier vidéo (MP4, MOV...)", type=["mp4", "mov", "avi"])

if 'clips' not in st.session_state:
    st.session_state.clips = []

if uploaded_file is not None:
    # Sauvegarder le fichier temporairement
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Lancer l'analyse et la génération des clips"):
        with st.spinner("Analyse en cours... Cela peut prendre plusieurs minutes selon la durée de la vidéo."):
            # 1. Traitement de la vidéo pour extraire les clips
            generated_clips_info = process_video("temp_video.mp4")
            
            # 2. Générer le contenu pour chaque clip
            final_clips = []
            for clip in generated_clips_info:
                content = generate_creative_content(clip["transcription"])
                final_clips.append({**clip, **content})
            
            st.session_state.clips = final_clips
            st.success(f"{len(st.session_state.clips)} clips ont été générés avec succès !")

# --- Section Affichage des Clips ---
if st.session_state.clips:
    st.header("2. Vos extraits sont prêts !")
    
    for i, clip_data in enumerate(st.session_state.clips):
        st.subheader(f"Extrait n°{i+1}")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Afficher la vidéo
            video_file = open(clip_data['path'], 'rb')
            video_bytes = video_file.read()
            st.video(video_bytes)
            
            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le clip",
                data=video_bytes,
                file_name=f"clip_{i+1}.mp4",
                mime="video/mp4"
            )

        with col2:
            # Champs éditables pour le contenu
            clip_data['title'] = st.text_input("Titre", value=clip_data['title'], key=f"title_{i}")
            clip_data['description'] = st.text_area("Description", value=clip_data['description'], height=150, key=f"desc_{i}")
            clip_data['hashtags'] = st.text_input("Hashtags", value=clip_data['hashtags'], key=f"tags_{i}")

            # Bouton de publication
            if st.button(f"🚀 Poster l'extrait n°{i+1} sur YouTube", key=f"upload_{i}"):
                try:
                    with st.spinner("Publication sur YouTube en cours..."):
                        upload_to_youtube(
                            video_path=clip_data['path'],
                            title=clip_data['title'],
                            description=clip_data['description'],
                            tags=clip_data['hashtags']
                        )
                    st.success(f"L'extrait n°{i+1} a été posté sur YouTube avec succès !")
                except Exception as e:
                    st.error(f"Une erreur est survenue lors de la publication : {e}")
                    st.warning("Assurez-vous d'avoir configuré votre fichier `client_secrets.json` et d'avoir autorisé l'application.")

        st.divider()