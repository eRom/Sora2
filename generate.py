#!/usr/bin/env python3
"""
Script pour générer une vidéo avec l'API Sora2
"""

import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path
import time
import json
import hashlib
import base64
import argparse

# Charger les variables d'environnement
load_dotenv()

# Configuration
API_KEY = os.getenv("SORA_API_KEY")
MODEL = os.getenv("SORA_MODEL", "sora-2-pro")
DURATION = os.getenv("SORA_DURATION", "8")
SIZE = os.getenv("SORA_SIZE", "1280x720")
REFERENCE_IMAGE = os.getenv("SORA_REFERENCE_IMAGE")

# Variable globale pour suivre l'image de référence utilisée
current_reference_image_path = None

# URL de l'API Sora2
API_BASE_URL = "https://api.openai.com/v1/videos"

# Configuration retry
MAX_RETRIES = 3
INITIAL_BACKOFF = 5  # secondes

def save_metadata(video_id, prompt, status, error=None, reference_image_path=None):
    """Sauvegarde les métadonnées de la vidéo pour récupération ultérieure"""
    metadata_dir = Path("metadata")
    metadata_dir.mkdir(exist_ok=True)

    metadata = {
        "video_id": video_id,
        "prompt": prompt,
        "model": MODEL,
        "duration": DURATION,
        "size": SIZE,
        "status": status,
        "timestamp": int(time.time()),
        "error": error
    }

    # Ajouter les informations sur l'image de référence si fournie
    global current_reference_image_path
    if current_reference_image_path:
        metadata["reference_image"] = current_reference_image_path

    metadata_file = metadata_dir / f"{video_id}.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return metadata_file

def read_prompt():
    """Lit le prompt depuis le fichier prompt.md"""
    prompt_file = Path("prompt.md")
    if not prompt_file.exists():
        print("Erreur: Le fichier prompt.md n'existe pas")
        sys.exit(1)

    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        # Retirer les titres markdown et lignes vides
        lines = [line for line in content.split("\n") if line.strip() and not line.startswith("#")]
        return "\n".join(lines)

def read_reference_image(image_path):
    """Lit une image de référence et la convertit en base64"""
    if not image_path:
        return None

    # Vérifier si c'est une URL
    if image_path.startswith(('http://', 'https://')):
        print("❌ Erreur: Les URLs ne sont pas supportées pour les images de référence")
        print("   Veuillez placer votre image dans le répertoire 'input_reference/'")
        return None

    # Fichier local - vérifier qu'il est dans input_reference/
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"❌ Erreur: Le fichier image '{image_path}' n'existe pas")
        return None

    # Vérifier que le fichier est dans le répertoire input_reference/
    try:
        image_file_abs = image_file.resolve()
        input_ref_dir = Path("input_reference").resolve()
        if not str(image_file_abs).startswith(str(input_ref_dir)):
            print(f"❌ Erreur: L'image doit être placée dans le répertoire 'input_reference/'")
            print(f"   Chemin actuel: {image_file}")
            print(f"   Répertoire requis: input_reference/")
            return None
    except Exception:
        print(f"❌ Erreur: Impossible de vérifier le chemin de l'image")
        return None

    # Vérifier l'extension
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    if image_file.suffix.lower() not in valid_extensions:
        print(f"❌ Erreur: Format d'image non supporté. Formats supportés: {', '.join(valid_extensions)}")
        return None

    try:
        from PIL import Image
        # Vérifier les dimensions de l'image
        with Image.open(image_file) as img:
            width, height = img.size
            expected_size = SIZE  # Format "1280x720"
            expected_width, expected_height = map(int, expected_size.split('x'))

            print(f"📏 Dimensions de l'image: {width}x{height}")
            print(f"📏 Dimensions requises: {expected_width}x{expected_height}")

            if width != expected_width or height != expected_height:
                print(f"❌ Erreur: Les dimensions de l'image ne correspondent pas à SORA_SIZE={SIZE}")
                print(f"   Image actuelle: {width}x{height}")
                print(f"   Attendu: {expected_width}x{expected_height}")
                print(f"   Veuillez redimensionner l'image ou modifier SORA_SIZE dans le .env")
                return None
            else:
                print(f"✅ Dimensions de l'image correctes")
    except ImportError:
        print("⚠️  Attention: PIL/Pillow n'est pas installé. Impossible de vérifier les dimensions de l'image.")
        print("   Installez avec: pip install Pillow")
    except Exception as e:
        print(f"⚠️  Attention: Impossible de vérifier les dimensions de l'image: {e}")

    try:
        with open(image_file, "rb") as f:
            image_data = f.read()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier image: {e}")
        return None

    # Encoder en base64
    try:
        base64_image = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ Image de référence chargée ({len(image_data):,} bytes)")
        return base64_image
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage de l'image: {e}")
        return None

def check_moderation_error(error_response):
    """Détecte si l'erreur est liée à la modération"""
    if not error_response:
        return False

    error_text = str(error_response).lower()
    moderation_keywords = [
        "moderation",
        "content policy",
        "violates",
        "inappropriate",
        "blocked",
        "prohibited"
    ]

    return any(keyword in error_text for keyword in moderation_keywords)

def generate_video(prompt, reference_image_base64=None):
    """Génère une vidéo en utilisant l'API Sora2"""
    if not API_KEY or API_KEY == "your_api_key_here":
        print("Erreur: Veuillez configurer votre clé API dans le fichier .env")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    print(f"Génération de la vidéo avec les paramètres:")
    print(f"  - Model: {MODEL}")
    print(f"  - Duration: {DURATION}s")
    print(f"  - Size: {SIZE}")
    if reference_image_base64:
        print(f"  - Image de référence: ✅")
    else:
        print(f"  - Image de référence: ❌")
    print(f"  - Prompt: {prompt[:100]}...")
    
    # Demander confirmation avant l'appel API
    print("\n" + "="*50)
    print("⚠️  ATTENTION: Cet appel va générer des coûts sur votre compte OpenAI")
    print("="*50)
    
    confirmation = input("\nVoulez-vous continuer avec la génération de vidéo ? (oui/non): ").lower().strip()
    
    if confirmation not in ['oui', 'o', 'yes', 'y']:
        print("❌ Génération annulée par l'utilisateur")
        return None
    
    print("\nEnvoi de la requête à l'API...")

    # Préparer les données pour multipart/form-data
    data = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": DURATION,
        "size": SIZE
    }
    
    files = {}
    
    # Ajouter l'image de référence si fournie
    if reference_image_base64:
        # Convertir base64 en bytes pour l'upload
        import base64
        image_data = base64.b64decode(reference_image_base64)
        files["input_reference"] = ("reference_image.jpg", image_data, "image/jpeg")

    try:
        response = requests.post(API_BASE_URL, headers=headers, data=data, files=files)

        # Vérifier les erreurs de modération AVANT de facturer
        if response.status_code == 400:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)

            if check_moderation_error(error_msg):
                print("\n❌ ERREUR DE MODÉRATION:")
                print(f"   {error_msg}")
                print("\n💡 Suggestions:")
                print("   - Reformulez votre prompt pour éviter le contenu sensible")
                print("   - Évitez les descriptions violentes, sexuelles ou inappropriées")
                print("   - Utilisez un langage plus neutre et descriptif")
                print("\n⚠️  IMPORTANT: Vous n'avez PAS été débité car la requête a été rejetée avant la génération")
                return False
            else:
                print(f"\n❌ Erreur de requête: {error_msg}")
                return False

        response.raise_for_status()
        result = response.json()
        print(f"Réponse de l'API: {result}")

        # L'API retourne un ID de vidéo
        if "id" in result:
            video_id = result["id"]
            print(f"\n✓ Tâche de génération créée: {video_id}")
            print("⏳ La génération peut prendre quelques minutes...")

            # Sauvegarder les métadonnées
            save_metadata(video_id, prompt, "queued")

            return wait_for_completion(video_id, headers, prompt)

        print("Format de réponse inattendu:", result)
        return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erreur lors de la requête API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", e.response.text)
                print(f"   Détails: {error_msg}")

                if check_moderation_error(error_msg):
                    print("\n⚠️  Erreur de modération détectée - Vous n'avez pas été débité")
            except:
                print(f"   Détails: {e.response.text}")
        return False

def wait_for_completion(video_id, headers, prompt):
    """Attend la complétion d'une tâche de génération asynchrone"""
    status_url = f"{API_BASE_URL}/{video_id}"
    content_url = f"{API_BASE_URL}/{video_id}/content"

    timeout_counter = 0
    max_timeout = 600  # 10 minutes (600 secondes / 10 secondes par check)

    while timeout_counter < max_timeout:
        try:
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()
            result = response.json()

            status = result.get("status")
            progress = result.get("progress", 0)
            print(f"📊 Status: {status} - Progression: {progress}%")

            # Mettre à jour les métadonnées
            save_metadata(video_id, prompt, status)

            if status == "completed":
                print(f"\n✅ Vidéo générée avec succès!")
                # Télécharger la vidéo avec retry
                return download_video_with_retry(content_url, headers, video_id, prompt)

            elif status in ["failed", "error"]:
                error_info = result.get("error", {})
                error_msg = error_info.get("message", "Erreur inconnue")
                error_code = error_info.get("code", "")

                print(f"\n❌ Erreur lors de la génération:")
                print(f"   Message: {error_msg}")
                if error_code:
                    print(f"   Code: {error_code}")

                # Sauvegarder l'erreur dans les métadonnées
                save_metadata(video_id, prompt, "failed", error=error_msg)

                if check_moderation_error(error_msg):
                    print("\n⚠️  ATTENTION: Vous avez été débité mais la vidéo a été rejetée par la modération")
                    print("   Contactez le support OpenAI pour un remboursement avec cet ID: " + video_id)

                return False

            time.sleep(10)
            timeout_counter += 1

        except requests.exceptions.RequestException as e:
            print(f"\n⚠️  Erreur lors de la vérification du status: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"   Détails: {e.response.text}")

            # Sauvegarder l'état d'erreur
            save_metadata(video_id, prompt, "error", error=str(e))
            print(f"\n💾 Métadonnées sauvegardées pour récupération: metadata/{video_id}.json")
            return False

    print(f"\n⏰ Timeout: La génération prend trop de temps (>{max_timeout * 10}s)")
    print(f"   Video ID: {video_id}")
    print(f"   Vous pouvez vérifier manuellement le statut plus tard")
    save_metadata(video_id, prompt, "timeout")
    return False

def download_video_with_retry(content_url, headers, video_id, prompt, max_retries=MAX_RETRIES):
    """Télécharge la vidéo avec retry en cas d'erreur réseau"""
    for attempt in range(max_retries):
        try:
            print(f"\n📥 Tentative de téléchargement {attempt + 1}/{max_retries}...")

            if download_video_from_api(content_url, headers, video_id):
                save_metadata(video_id, prompt, "downloaded")
                return True

        except Exception as e:
            wait_time = INITIAL_BACKOFF * (2 ** attempt)
            if attempt < max_retries - 1:
                print(f"\n⚠️  Erreur: {e}")
                print(f"   Nouvelle tentative dans {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"\n❌ Échec après {max_retries} tentatives")
                print(f"   Video ID: {video_id}")
                print(f"   URL: {content_url}")
                print(f"\n💡 Vous pouvez télécharger manuellement avec:")
                print(f"   curl -H 'Authorization: Bearer YOUR_API_KEY' '{content_url}' > output/{video_id}.mp4")
                save_metadata(video_id, prompt, "download_failed", error=str(e))
                return False

    return False

def download_video_from_api(content_url, headers, video_id):
    """Télécharge la vidéo générée depuis l'API"""
    print("📥 Téléchargement de la vidéo...")

    response = requests.get(content_url, headers=headers, stream=True, timeout=300)
    response.raise_for_status()

    # Créer le dossier de sortie si nécessaire
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Nom du fichier avec timestamp
    timestamp = int(time.time())
    output_file = output_dir / f"video_{video_id}_{timestamp}.mp4"
    temp_file = output_dir / f"video_{video_id}_{timestamp}.mp4.tmp"

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    hasher = hashlib.sha256()

    # Télécharger dans un fichier temporaire
    with open(temp_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                hasher.update(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\r📥 Téléchargement: {progress:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)

    print()  # Nouvelle ligne après la barre de progression

    # Vérifier que le téléchargement est complet
    if total_size > 0 and downloaded != total_size:
        temp_file.unlink()
        raise Exception(f"Téléchargement incomplet: {downloaded}/{total_size} bytes")

    # Vérifier que le fichier n'est pas vide
    if downloaded == 0:
        temp_file.unlink()
        raise Exception("Le fichier téléchargé est vide")

    # Renommer le fichier temporaire
    temp_file.rename(output_file)

    file_hash = hasher.hexdigest()
    print(f"\n✅ Vidéo sauvegardée: {output_file}")
    print(f"   Taille: {downloaded:,} bytes")
    print(f"   SHA256: {file_hash[:16]}...")

    # Sauvegarder le hash dans les métadonnées
    metadata_file = Path("metadata") / f"{video_id}.json"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        metadata["file_path"] = str(output_file)
        metadata["file_size"] = downloaded
        metadata["sha256"] = file_hash
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    return True

def main():
    parser = argparse.ArgumentParser(description="Générateur de vidéo Sora2 avec support d'image de référence optionnelle")
    parser.add_argument("--reference-image", "-r",
                       help="Chemin ou URL de l'image de référence à utiliser")

    args = parser.parse_args()

    print("═══════════════════════════════════════════")
    print("   🎬 Générateur de vidéo Sora2")
    print("═══════════════════════════════════════════\n")

    # Déterminer l'image de référence à utiliser
    global current_reference_image_path
    reference_image_path = args.reference_image or REFERENCE_IMAGE

    if reference_image_path:
        print(f"🖼️  Image de référence: {reference_image_path}")
        current_reference_image_path = reference_image_path
        reference_image_base64 = read_reference_image(reference_image_path)
        if reference_image_base64 is None:
            print("❌ Impossible de charger l'image de référence, abandon...")
            sys.exit(1)
    else:
        print("ℹ️  Aucune image de référence spécifiée")
        reference_image_base64 = None

    # Lire le prompt
    prompt = read_prompt()

    # Générer la vidéo
    success = generate_video(prompt, reference_image_base64)

    if success:
        print("\n" + "═" * 43)
        print("✅ Génération terminée avec succès!")
        print("═" * 43)
    else:
        print("\n" + "═" * 43)
        print("❌ La génération a échoué")
        print("═" * 43)
        sys.exit(1)

if __name__ == "__main__":
    main()
