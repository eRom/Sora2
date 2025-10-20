# Générateur de vidéo Sora2

Script Python pour générer des vidéos avec l'API Sora2-pro, avec support optionnel d'images de référence.

## Installation

1. Installer les dépendances:
```bash
pip install -r requirements.txt
```

2. Configurer votre clé API dans le fichier `.env`:
```bash
SORA_API_KEY=votre_clé_api_ici
SORA_MODEL=sora-2-pro
SORA_DURATION=8
SORA_SIZE=1280x720
SORA_REFERENCE_IMAGE=input_reference/votre_image.jpg
```

## Configuration

- **SORA_API_KEY**: Votre clé d'API Sora2
- **SORA_MODEL**: Modèle à utiliser (`sora-2` ou `sora-2-pro`)
- **SORA_DURATION**: Durée de la vidéo en secondes (`4`, `8`, ou `12`)
- **SORA_SIZE**: Résolution de la vidéo (ex: `1280x720`)
- **SORA_REFERENCE_IMAGE**: (Optionnel) Chemin vers une image de référence

## Utilisation

### Génération simple (sans image de référence)

1. Éditer le fichier `prompt.md` avec votre description de vidéo

2. Lancer la génération:
```bash
python generate.py
```

### Génération avec image de référence

1. Éditer le fichier `prompt.md` avec votre description de vidéo

2. Placer votre image de référence dans le dossier `input_reference/`
   - **Important**: L'image doit avoir les mêmes dimensions que SORA_SIZE
   - Exemple: si SORA_SIZE=1280x720, l'image doit être 1280x720 pixels

3. Lancer la génération avec l'image:
```bash
# Via argument en ligne de commande
python generate.py --reference-image input_reference/mon_image.jpg

# Ou via la variable d'environnement (.env)
python generate.py
```

4. La vidéo sera téléchargée dans le dossier `output/`

## Formats d'images supportés

- JPG/JPEG
- PNG
- GIF
- BMP
- WebP

## Structure du projet

```
.
├── .env                    # Configuration API (ne pas commiter)
├── prompt.md              # Votre prompt pour la vidéo
├── generate.py             # Script principal
├── requirements.txt        # Dépendances Python
├── input_reference/        # Images de référence (à créer)
├── output/                # Vidéos générées
└── metadata/              # Métadonnées des générations
```

## Arguments en ligne de commande

- `--reference-image` / `-r`: Spécifier une image de référence (remplace la variable d'environnement)

## Exemples d'utilisation

```bash
# Génération sans image de référence
python generate.py

# Génération avec image de référence spécifique
python generate.py --reference-image input_reference/ma_photo.png

# Afficher l'aide
python generate.py --help
```
