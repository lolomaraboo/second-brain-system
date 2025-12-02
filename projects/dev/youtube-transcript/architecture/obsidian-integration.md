# Intégration Obsidian

## 📁 Organisation

**Choix :** Flat structure + tags YAML

```
SecondBrain/content/videos/
├── _INDEX.md
├── Top-Trending-GitHub-Projects-y7Ka-aATAzI.md
├── Python-Tutorial-abc123.md
└── ...
```

**Pourquoi flat ?**
- ✅ Flexibilité : 1 vidéo = plusieurs tags
- ✅ Recherche Obsidian puissante
- ✅ Pas de réorganisation si thématiques changent
- ✅ Évite doublons (même vidéo, plusieurs thèmes)

## 📝 Format fichier

### YAML Frontmatter

```yaml
---
title: "Titre de la vidéo"
video_id: VIDEO_ID
date: 2025-12-01
url: https://youtube.com/watch?v=VIDEO_ID
tags: [ai, dev, python, tutorial]
---
```

**Champs obligatoires :**
- `title` : Titre descriptif
- `video_id` : ID YouTube (unique)
- `date` : Date d'extraction
- `url` : Lien source

**Champs optionnels :**
- `tags` : Liste tags pour recherche
- `channel` : Nom chaîne (future)
- `duration` : Durée vidéo (future)

### Corps du fichier

Transcription brute avec :
- Retours ligne (~40-50 chars)
- Ponctuation préservée
- Marqueurs locuteur `>>`

```markdown
Hey creators, welcome to top trending
and open- source GitHub projects. This
week, part two, where you'll discover
powerful new tools on GitHub...
```

## 🔍 Recherche Obsidian

**Par tags :**
```
tag:#ai
tag:#python
```

**Par titre :**
Recherche globale Obsidian

**Par contenu :**
Full-text search dans transcriptions

**Liens internes :**
```markdown
[[Top-Trending-GitHub-Projects-y7Ka-aATAzI]]
```

## 📊 Métadonnées enrichies (future)

### Phase 2 : Métadonnées auto

```yaml
---
title: "Titre automatique"
channel: "Nom de la chaîne"
duration: "15:32"
published: "2025-11-28"
views: 125000
thumbnail: "https://..."
---
```

### Phase 3 : Intelligence

```yaml
---
summary: "Résumé en 3 lignes"
concepts: [LLM, AI Agents, Open Source]
mentioned_projects:
  - LLM Council
  - Code Mode
  - ADK Go
key_points:
  - "Multiple LLMs debate for consensus"
  - "Code-first AI agents in Go"
---
```

## 🎯 Tags suggérés

**Thématiques principales :**
- `dev` - Développement
- `ai` - Intelligence Artificielle
- `python`, `go`, `typescript` - Langages
- `tutorial` - Tutoriels
- `business` - Business/Marketing
- `music` - Musique/Audio
- `tech` - Technologie générale
- `conference` - Conférences

**Tags automatiques (future) :**
Basés sur :
- Titre vidéo
- Description
- Chaîne YouTube
- Analyse contenu transcription

## 🔗 Intégration Second Brain

**Liens croisés :**
```markdown
# Dans projects/dev/project-X/_INDEX.md
Ressources vidéo : [[../../content/videos/_INDEX|Videos]]

# Dans une vidéo
Projet lié : [[../../projects/dev/youtube-transcript/_INDEX]]
```

**Wiki outils :**
```markdown
# Dans wiki/tools/youtube-transcript.md
Transcriptions stockées : [[../../content/videos/_INDEX]]
```

## 🛠️ Workflow complet

1. **Extraction**
   ```bash
   yt URL --save --title "..." --tags dev,python
   ```

2. **Fichier créé**
   `content/videos/[titre]-[id].md`

3. **Recherche Obsidian**
   Tags, titre, contenu

4. **Analyse avec Claude**
   "Analyse la vidéo sur [sujet]"

5. **Liens croisés**
   Relier aux projets pertinents
