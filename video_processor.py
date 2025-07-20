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
    print("1. Lancement de la transcription avec Whisper...")
    model = whisper.load_model("base")
    
    video = mp.VideoFileClip(video_path)
    
    # --- DÉBUT DE LA CORRECTION ---
    # On vérifie si la vidéo a une piste audio
    if video.audio is None:
        print("ERREUR: La vidéo ne contient pas de piste audio.")
        # On retourne une liste vide car on ne peut pas analyser une vidéo sans son
        return [] 
    # --- FIN DE LA CORRECTION ---

    audio_path = "temp_audio.wav"
    print("Extraction de la piste audio...")
    video.audio.write_audiofile(audio_path) # Maintenant, cette ligne est sécurisée
    
    print("Transcription de l'audio avec Whisper...")
    result = model.transcribe(audio_path, word_timestamps=True)
    os.remove(audio_path)
    # ... reste du code

    print("2. Identification des moments forts...")
    highlights = []
    current_segment_words = []
    segment_start_time = result['segments'][0]['words'][0]['start'] if result['segments'] else 0

    # Simplification : on cherche les segments denses en mots
    for segment in result['segments']:
        for word_info in segment['words']:
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
    if current_segment_words and (current_segment_words[-1]['end'] - segment_start_time >= min_clip_duration):
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
    clip_resized = original_clip.resize(height=1920 * w / 1080)
    
    # Créer un fond en zoomant et floutant le clip original
    background_clip = original_clip.resize(height=1920)
    background_clip = background_clip.crop(x_center=background_clip.w/2, width=1080)
    background_clip = background_clip.fx(mp.vfx.blur, radius=20)
    
    # Superposer le clip principal sur le fond
    final_clip = mp.CompositeVideoClip([
        background_clip,
        clip_resized.set_position("center")
    ], size=(1080, 1920))
    
    # Ajout des sous-titres (simplifié, une version avancée animerait mot par mot)
    # Pour cela, il faudrait relancer whisper sur le subclip pour des timestamps précis
    # Pour l'instant, on n'ajoute pas les sous-titres pour garder le code simple.

    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
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
    generated_clips = []

    for i, highlight in enumerate(highlights):
        output_filename = os.path.join("temp_clips", f"clip_{i+1}.mp4")
        clip_path = create_vertical_clip(video_path, highlight["start"], highlight["end"], output_filename)
        generated_clips.append({
            "path": clip_path,
            "transcription": highlight["transcription"]
        })
        
    return generated_clips
