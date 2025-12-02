# Stack Technique

## 🐍 Python

**Version :** 3.9.6 (système macOS)
**Shebang :** `#!/Library/Developer/CommandLineTools/usr/bin/python3`

**Pourquoi Python système ?**
- Modules installés en mode utilisateur
- Évite conflits avec venv projets
- Disponible partout sur la machine

## 📦 Dépendances

### youtube-transcript-api 1.2.3

**Rôle :** Extraction transcriptions YouTube

```python
from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
result = api.fetch(video_id)  # FetchedTranscript
```

**Caractéristiques :**
- Pas d'API key nécessaire
- Gratuit et illimité
- Support sous-titres auto et manuels
- Retour : objets `FetchedTranscriptSnippet`

### defusedxml 0.7.1

**Rôle :** Dépendance de youtube-transcript-api
**Fonction :** Parsing XML sécurisé

## 🛠️ Outils système

**pbcopy (macOS)**
```bash
echo "text" | pbcopy
```
- Copie dans presse-papier macOS
- Natif, pas de dépendance

**git**
- Versioning du code
- Repo privé GitHub

## 📁 Filesystem

**Structure projet :**
```
youtube-transcript/
├── yt_transcript.py      # Script principal
├── requirements.txt      # Dépendances
├── README.md             # Documentation
└── .gitignore           # Git excludes
```

**Installation :**
```bash
pip install -r requirements.txt
chmod +x yt_transcript.py
ln -s [path]/yt_transcript.py ~/.local/bin/yt
```

## 🔄 Formats supportés

**Input :**
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `VIDEO_ID` (direct)

**Output :**
- Texte brut (stdout)
- Clipboard (pbcopy)
- Markdown avec YAML (Obsidian)

## ⚡ Performance

**Temps d'exécution typique :**
- Vidéo 10 min : ~2-3 secondes
- Vidéo 30 min : ~5-8 secondes

**Bottleneck :** API YouTube (réseau)

## 🔮 Évolutions futures possibles

**Phase 2 :**
- `yt-dlp` : Métadonnées YouTube (titre, durée, chaîne)
- `sqlite3` : Base locale pour historique

**Phase 3 :**
- LLM API : Résumés automatiques
- `transformers` : Extraction concepts NLP

**Phase 4 :**
- `flask/fastapi` : Interface web
- `playwright` : Preview intégrée
