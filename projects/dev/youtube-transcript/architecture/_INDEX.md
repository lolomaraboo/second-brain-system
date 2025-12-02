# Architecture - YouTube Transcript

Vue d'ensemble de l'architecture technique du projet.

## 📁 Structure

- [[stack-technique|Stack Technique]] - Python, APIs, dépendances
- [[obsidian-integration|Intégration Obsidian]] - Format YAML, organisation

## 🏗️ Architecture globale

```
User → yt command → Python Script → YouTube API → Transcript
                         ↓
                    Processing (formatting, metadata)
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        Clipboard (pbcopy)    Obsidian Vault
                              (YAML + Markdown)
```

## 🔑 Composants clés

**1. CLI Entry Point**
- Symlink : `~/.local/bin/yt`
- Script : `yt_transcript.py`
- Python : 3.9.6 système

**2. Extraction**
- Library : `youtube-transcript-api` 1.2.3
- Méthode : `YouTubeTranscriptApi().fetch(video_id)`
- Format : `FetchedTranscript` itérable

**3. Output**
- Clipboard : `pbcopy` (macOS)
- Obsidian : `content/videos/[titre]-[id].md`
- Format : YAML frontmatter + texte

## 📊 Flux de données

1. **Input** : URL YouTube ou video_id
2. **Parsing** : Extraction video_id via regex
3. **API Call** : `youtube-transcript-api`
4. **Formatting** : Ajout retours ligne, ponctuation préservée
5. **Output** : Clipboard et/ou fichier Obsidian

## 🔐 Sécurité

- Pas de secrets (API publique YouTube)
- Sandbox : Aucun (local, pas de risque)
- Permissions : Lecture/écriture filesystem locale
