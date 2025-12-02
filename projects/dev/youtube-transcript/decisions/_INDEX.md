# Décisions - YouTube Transcript

Décisions techniques et choix architecturaux du projet.

## 📋 Liste des décisions

### 2025-12-01
- [[2025-12-01-roadmap|Roadmap de développement]] - Plan complet phases 1-5

## 🎯 Décisions majeures

### Architecture
- **Python système** (3.9.6) vs venv → Simplicité, disponibilité globale
- **youtube-transcript-api** vs scraping → API stable, gratuite, maintenue
- **Flat structure** vs dossiers thématiques → Flexibilité des tags

### Formatage
- **Retours ligne auto** vs flux continu → Lisibilité supérieure
- **YAML frontmatter** vs JSON → Standard Obsidian, plus lisible

### Distribution
- **Symlink PATH** vs script standalone → Accessible partout, maj faciles
- **Repo privé** vs public → Développement privé pour l'instant

## 🔄 Décisions en attente

### Phase 2
- Choix API métadonnées : yt-dlp vs YouTube Data API v3
- Format historique : SQLite vs JSON files
- Tags auto : règles manuelles vs ML

### Phase 3
- LLM pour résumés : OpenAI vs Anthropic vs local
- Extraction concepts : NLP library vs LLM

### Phase 5
- Interface web : Flask vs FastAPI
- Déploiement : local only vs cloud option
