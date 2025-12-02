# YouTube Transcript

Outil pour extraire les transcriptions de vidéos YouTube.

## Installation

```bash
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/youtube-transcript
pip install -r requirements.txt
```

Le script est accessible via la commande `yt` (symlink dans `~/.local/bin`).

## Utilisation rapide

```bash
# Copier dans le presse-papier
yt VIDEO_ID --copy

# Sauvegarder dans Obsidian
yt VIDEO_ID --save --title "Titre" --tags dev,python

# Copier ET sauvegarder
yt VIDEO_ID --copy --save --title "Titre" --tags ai,tutorial
```

## Workflow recommandé

1. **Trouver une vidéo intéressante**
2. **Extraire et sauvegarder**
   ```bash
   yt https://youtube.com/watch?v=... --save --title "..." --tags ...
   ```
3. **Demander à Claude d'analyser**
   - "Analyse la vidéo sur [sujet]"
   - "Résume les points clés de la dernière vidéo"
   - "Extrait les concepts importants"

## Formats supportés

- URL complète : `https://youtube.com/watch?v=VIDEO_ID`
- URL courte : `https://youtu.be/VIDEO_ID`
- ID seul : `VIDEO_ID`

## Langues

Par défaut : français puis anglais.

Pour changer :
```bash
yt VIDEO_ID --languages en,es,fr
```

## Stockage

Les transcriptions sont dans : `SecondBrain/content/videos/`

Format :
```yaml
---
title: "Titre"
video_id: VIDEO_ID
date: 2025-12-01
url: https://youtube.com/...
tags: [dev, python]
---

[Transcription]
```

## Dépannage

**Module non installé :**
```bash
pip install youtube-transcript-api
```

**Transcriptions désactivées :**
- La vidéo n'a pas de sous-titres
- Essayer une autre vidéo

**Script non dans PATH :**
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

## Liens

- Projet : `~/Documents/APP_HOME/CascadeProjects/windsurf-project/youtube-transcript/`
- README : [README.md](../../youtube-transcript/README.md)
