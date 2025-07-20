# video_processor.py
import os
import whisper
import moviepy.editor as mp
from moviepy.video.fx.all import crop, resize
import cv2
import shutil

# Crée un dossier pour stocker les clips temporaires
if not os.path.exists("temp_clips"):
    os.makedirs("temp_clips")

def find_highlights(video_path, min_clip_duration=15, max_clip_duration=60):
    """
    Analyse la transcription pour trouver des segments denses en paroles.
    C'est une simplification. Une version avancée analyserait aussi l'audio et la vidéo.
    """
    print("1. Lancement de l'analyse vidéo...")
    
    try:
        model = whisper.load_model("base") # "base" est rapide, "medium" est plus précis
        video = mp.VideoFileClip(video_path)
    except Exception as e:
        print(f"Erreur lors du chargement de la vidéo ou du modèle Whisper : {e}")
        return []

    # --- DÉBUT DE LA CORRECTION ---
    # On vérifie si la vidéo a une piste audio AVANT de continuer.
    if video.audio is None:
        print("ERREUR CRITIQUE: La vidéo fournie ne contient pas de piste audio.")
        print("Le traitement ne peut pas continuer car il est basé sur l'analyse audio.")
        # On arrête immédiatement la fonction et on retourne une liste vide.
        return [] 
    # --- FIN DE LA CORRECTION ---

    # Si on arrive ici, c'est que la vidéo a bien une piste audio.
    audio_path = "temp_audio.wav"
    print("Extraction de la piste audio...")
    video.audio.write_audiofile(audio_path) # Cette ligne est maintenant sécurisée.
    
    print("Transcription de l'audio avec Whisper (cela peut prendre du temps)...")
    result = model.transcribe(audio_path, word_timestamps=True)
    os.remove(audio_path) # Nettoyage du fichier audio temporaire

    print("2. Identification des moments forts...")
    highlights = []
    
    if not result or not result['segments']:
        print("Aucun segment de parole détecté dans la vidéo.")
        return []

    current_segment_words = []
    # S'assurer que le premier segment a bien des mots pour éviter une erreur
    if result['segments'] and result['segments'][0]['words']:
        segment_start_time = result['segments'][0]['words'][0]['start']
    else:
        print("La transcription n'a pas pu identifier de mots avec des timestamps.")
        return []

    # Simplification : on cherche les segments denses en mots
    for segment in result['segments']:
        for word_info in segment['words']:
            # S'assurer que le mot a bien un timestamp de fin
            if 'end' not in word_info:
                continue
                
            current_segment_words.append(word_info)
            duration = word_info['end'] - segment_start_time
            
            # Si le segment atteint la durée max, on le sauvegarde et on recommence
            if duration >= max_clip_duration:
                if duration >= min_clip_duration:
                    highlights.append({
                        "start": segment_start_time,
                        "end": word_info['end'],
                        "transcription": " ".join(w['word'] for w in current_segment_words)
                    })
                # Réinitialiser pour le prochain clip
                current_segment_words = []
                # Le prochain mot devient le début du segment suivant
                if 'start' in word_info: # S'assurer que le mot suivant existe
                   segment_start_time = word_info['start']

    # Ajouter le dernier segment s'il est assez long
    if current_segment_words and 'end' in current_segment_words[-1] and (current_segment_words[-1]['end'] - segment_start_time >= min_clip_duration):
         highlights.append({
            "start": segment_start_time,
            "end": current_segment_words[-1]['end'],
            "transcription": " ".join(w['word'] for w in current_segment_words)
        })

    print(f"Trouvé {len(highlights)} moments forts potentiels.")
    return highlights[:5] # On limite à 5 pour l'exemple

def create_vertical_clip(video_path, start_time, end_time, output_filename):
    """
    Découpe la vidéo et la convertit au format vertical 9:16 avec un fond flouté.
    """
    print(f"3. Génération du clip vertical pour {output_filename}...")
    original_clip = mp.VideoFileClip(video_path).subclip(start_time, end_time)
    
    # Création du fond flouté
    (w, h) = original_clip.size
    target_ratio = 1080 / 1920
    
    # Recadrer la vidéo originale pour la placer au centre
    # Note: cette logique peut être améliorée pour suivre les visages
    clip_resized = original_clip.resize(width=1080)
    
    # Créer un fond en zoomant et floutant le clip original
    background_clip = original_clip.resize(height=1920)
    background_clip = background_clip.crop(x_center=background_clip.w/2, width=1080)
    background_clip = background_clip.fx(mp.vfx.blur, radius=20)
    
    # Superposer le clip principal sur le fond
    final_clip = mp.CompositeVideoClip([
        background_clip,
        clip_resized.set_position("center")
    ], size=(1080, 1920)).set_audio(original_clip.audio) # Ne pas oublier de rattacher l'audio !
    
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, threads=4)
    return output_filename

def process_video(video_path):
    """
    Fonction principale qui orchestre la détection et la création de clips.
    """
    # Nettoyer les anciens clips avant de commencer
    if os.path.exists("temp_clips"):
        shutil.rmtree("temp_clips")
    os.makedirs("temp_clips")

    highlights = find_highlights(video_path)
    
    # Si aucun moment fort n'est trouvé, on arrête
    if not highlights:
        print("Aucun moment fort trouvé, fin du processus.")
        return []

    generated_clips = []
    for i, highlight in enumerate(highlights):
        output_filename = os.path.join("temp_clips", f"clip_{i+1}.mp4")
        clip_path = create_vertical_clip(video_path, highlight["start"], highlight["end"], output_filename)
        generated_clips.append({
            "path": clip_path,
            "transcription": highlight["transcription"]
        })
        
    return generated_clips
