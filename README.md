# Générateur de vidéo Sora2

Script Python pour générer des vidéos avec l'API Sora2-pro.

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
```

## Configuration

- **SORA_API_KEY**: Votre clé d'API Sora2
- **SORA_MODEL**: Modèle à utiliser (`sora-2` ou `sora-2-pro`)
- **SORA_DURATION**: Durée de la vidéo en secondes (`4`, `8`, ou `12`)
- **SORA_SIZE**: Résolution de la vidéo (ex: `1280x720`)

## Utilisation

1. Éditer le fichier `prompt.md` avec votre description de vidéo

2. Lancer la génération:
```bash
python generate_video.py
```

3. La vidéo sera téléchargée dans le dossier `output/`

## Structure du projet

```
.
├── .env                    # Configuration API (ne pas commiter)
├── prompt.md              # Votre prompt pour la vidéo
├── generate_video.py      # Script principal
├── requirements.txt       # Dépendances Python
└── output/               # Vidéos générées
```
