# YouTube Transcript

Outil d'extraction de transcriptions YouTube avec formatage, copie presse-papier et intégration Obsidian.

## 🎯 Statut : Opérationnel ✅

**Version :** 1.0.0
**Repo :** [lolomaraboo/youtube-transcript](https://github.com/lolomaraboo/youtube-transcript) (privé)
**Dernière mise à jour :** 2025-12-01

## 🚀 Quick Start

```bash
# Copier transcription
yt VIDEO_ID --copy

# Sauvegarder dans Obsidian
yt URL --save --title "Titre" --tags ai,dev

# Les deux
yt URL --copy --save --title "..." --tags ...
```

## 📚 Documentation

### Architecture
- [[architecture/_INDEX|Architecture Overview]]
- [[architecture/stack-technique|Stack Technique]]
- [[architecture/obsidian-integration|Intégration Obsidian]]

### Décisions
- [[decisions/_INDEX|Décisions techniques]]
- [[decisions/2025-12-01-roadmap|Roadmap développement]]

## 🔗 Liens rapides

**Local :**
- Projet : `~/Documents/APP_HOME/CascadeProjects/windsurf-project/youtube-transcript/`
- Script : `~/.local/bin/yt`
- Transcriptions : [[../../../content/videos/_INDEX|content/videos/]]

**Documentation :**
- [[../../wiki/tools/youtube-transcript|Wiki - YouTube Transcript]]
- README : `youtube-transcript/README.md`

## 📊 Métriques

- **Transcriptions sauvegardées :** 1
- **Dernière utilisation :** 2025-12-01
- **Mem0 project_id :** `yt-transcript`

## 🎯 Prochaines étapes

Voir [[decisions/2025-12-01-roadmap|Roadmap]] pour le plan de développement complet.

**Phase 2 prioritaire :**
- Métadonnées YouTube automatiques
- Tags intelligents
- Historique local
