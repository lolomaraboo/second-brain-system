---
description: Sauvegarde le contexte de la session (Mem0 + Obsidian + Resume)
---

Fais un résumé de cette session et sauvegarde.

**Usage:**
- `/end` - Détection automatique du projet (git root ou pwd)
- `/end [project-id]` - Force le projet spécifié

---

**IMPORTANT** : Avant de commencer, exécute OBLIGATOIREMENT :
```bash
source ~/.claude/shell-config/end-lock-helpers.sh && end_with_lock
```
Ceci acquiert un lock pour éviter les conflits si 2 sessions font /end simultanément.

---

1. **Mem0** : Utilise mem0_save pour sauvegarder le contexte de travail :
   - Ce qui a été accompli
   - Les décisions techniques prises
   - Les problèmes rencontrés et leurs solutions
   - Les prochaines étapes suggérées

2. **Documentation Review (CODE-DOC-MAP)** : Vérifie la synchronisation code-doc :
   - Lit `SecondBrain/wiki/CODE-DOC-MAP.md` (si existe)
   - Identifie les fichiers code modifiés pendant la session
   - Pour chaque fichier dans CODE-DOC-MAP, vérifie si doc correspondante à jour
   - Affiche résumé : "📝 Documentation Review:"
     ```
     Fichiers code modifiés:
     - ~/scripts/mem0_mcp_server.py

     Documentation correspondante (CODE-DOC-MAP):
     - SecondBrain/wiki/tools/mem0-auto-sync-architecture.md

     Ces fichiers docs sont-ils à jour? [o/n]
     ```
   - Si 'n' : rappeler de mettre à jour avant prochain commit
   - Si 'o' : continuer sauvegarde

3. **Obsidian** : Propose de mettre à jour les notes si :
   - Une décision architecturale importante a été prise
   - Un nouveau pattern/outil a été découvert
   - Un debug non-trivial a été résolu
   - Une nouvelle config/secret a été ajouté
   - **Note** : Si documentation déjà reviewée à l'étape 2, ne pas re-demander

4. **Resume File** : Génère automatiquement un résumé ultra-rapide :

   **Détection du projet (robuste) :**
   - Si argument fourni : utilise `$ARGUMENTS` comme project_id
   - Sinon : essaye `git rev-parse --show-toplevel` puis `basename`
   - Fallback : `basename "$PWD"`
   - **Confirmation** : Affiche "💾 Saving context for project '[project_id]' - Proceed? (y/n)"
   - Si 'n' : demander le nom du projet

   **Génération du resume :**
   - Crée `~/.claude/resumes/[project-id]/` si nécessaire
   - Génère `~/.claude/resumes/[project-id]/resume.md` (20-30 lignes)
   - **Écrit `~/.claude/last-project.txt`** avec le project_id (1 ligne)

   Contenu du resume.md :
   - État actuel du projet
   - Résumé de la dernière session (3-5 lignes)
   - Décisions techniques clés
   - Fichiers importants modifiés (top 5)
   - Prochaines étapes (TODOs)
   - Références vers session complète, Obsidian _INDEX, stats Mem0

5. **Cleanup final** : À la toute fin, exécute OBLIGATOIREMENT :
   ```bash
   # Supprime la session du tracking Obsidian
   python3 ~/scripts/obsidian_session_manager.py unregister

   # Relâche le lock /end
   source ~/.claude/shell-config/end-lock-helpers.sh && end_lock_release
   ```

**Note** : Ces commandes doivent être exécutées même si erreur pendant la sauvegarde.
