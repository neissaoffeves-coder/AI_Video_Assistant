# content_generator.py
from transformers import pipeline

# Initialiser le pipeline une seule fois
# Pour le français, 'T5-base' fine-tuné sur des titres/résumés serait idéal.
# 'MBarek/bloom-arabic-french-english' est un exemple polyvalent.
# On utilise un modèle de résumé pour l'exemple.
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_creative_content(transcription):
    """
    Génère un titre, une description et des hashtags à partir d'une transcription.
    """
    print("4. Génération du contenu créatif (titre, description)...")
    
    # Simplification : on ne garde que les 512 premiers tokens pour le modèle
    short_transcription = " ".join(transcription.split()[:300])

    # Génération d'un résumé qui servira de description
    summary_result = summarizer(f"summarize: {short_transcription}", max_length=40, min_length=15, do_sample=False)
    description = summary_result[0]['summary_text']
    
    # Génération d'un titre accrocheur (on utilise le même modèle avec un prompt différent)
    # C'est une astuce. Un modèle fine-tuné pour les titres serait meilleur.
    title_prompt = f"Génère un titre de vidéo court et percutant pour ce texte: {description}"
    # Pour cet exemple, on va créer un titre simple pour éviter la complexité du prompt
    # Extraire les mots clés de la description
    keywords = [word for word in description.split() if len(word) > 4]
    if len(keywords) > 2:
        title = f"Incroyable ! {keywords[0].capitalize()} {keywords[1]}... 😱"
    else:
        title = "Regardez ce moment fou !"

    # Génération de hashtags
    hashtags = "#shorts #fyp #viral"
    if keywords:
        hashtags += f" #{keywords[0].lower()}"

    return {
        "title": title,
        "description": f"{description}\n\n#AppelÀLAction #AbonneToi",
        "hashtags": hashtags
    }