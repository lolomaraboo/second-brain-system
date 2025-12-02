# CLAUDE.md - Renforcement de la Règle de Consultation

**Date:** 2025-12-02
**Statut:** ✅ IMPLÉMENTÉ
**Impact:** Critique (comportement fondamental de Claude)

## Problème Identifié

Claude n'appliquait pas systématiquement la règle de priorité de consultation:
- Parfois utilisait `bash`, `ls`, `find` avant de consulter Mem0/Obsidian
- Explorait le filesystem AVANT de chercher dans la mémoire
- Violait la règle: "Mémoire/Obsidian AVANT filesystem"

**Exemple de violation:**
```bash
# Mauvais : exploration filesystem directe
ls -la ~/.claude/hooks/
ls -la ~/scripts/

# Correct : consulter d'abord la mémoire
mem0_search("hooks configuration")
# PUIS si nécessaire: ls -la ~/.claude/hooks/
```

## Solutions Implémentées

### 1. Checklist Critique (début de CLAUDE.md)

Ajout d'une section **⚠️ CHECKLIST CRITIQUE** en tout début du fichier:

```markdown
## ⚠️ CHECKLIST CRITIQUE - À APPLIQUER SYSTÉMATIQUEMENT ⚠️

**Avant d'utiliser TOUT outil (Read, Bash, Write, etc.), vérifie:**

1. ✅ **Chercher d'abord dans Second Brain:**
   - `mem0_search` pour trouver informations existantes
   - Lire Obsidian `_INDEX.md` pertinents
   - **SEULEMENT APRÈS:** utiliser filesystem (Bash, Read, etc.)

2. ✅ **Sauvegarder automatiquement:**
   - Après chaque commit important → `mem0_save`
   - Après décision technique → `mem0_save`
   - Après création config/script → `mem0_save`

3. ✅ **Toujours consulter la mémoire avant:**
   - Créer nouveau fichier (Write) → chercher patterns existants
   - Modifier fichier critique (Edit) → chercher bugs/décisions connus
   - Faire git commit → chercher conventions projet
   - Installer package → chercher conflits connus

**RÈGLE D'OR: Mémoire/Obsidian AVANT filesystem/bash**
```

**Raison du placement en début:** Claude lit CLAUDE.md de haut en bas. Mettre la règle critique en premier maximise les chances qu'elle soit appliquée.

### 2. Warnings Renforcés (section "Consultation automatique")

Ajout d'un warning visible dans la section existante:

```markdown
⚠️ **RÈGLE CRITIQUE:** TOUJOURS consulter Mem0/Obsidian AVANT d'utiliser Bash/Read/Write pour explorer le système

**Si tu utilises Bash/Read pour chercher sans avoir consulté Mem0/Obsidian d'abord = VIOLATION DE LA RÈGLE**
```

**Ordre de priorité obligatoire:**
1. `mem0_search` → Chercher dans la mémoire
2. `Read` Obsidian _INDEX.md → Consulter documentation
3. **SEULEMENT APRÈS:** Bash/Read filesystem

## Idée Future: Pre-Tool Validation Hook

Voir [[../ideas/pre-tool-validation-hook|Pre-Tool Validation Hook]]

**Statut:** Idée documentée, implémentation en attente

Système de hook qui détecterait automatiquement:
- Utilisation de Bash/Read avant mem0_search
- Afficherait warning automatique
- Permettrait audit des violations

**Décision:** Attendre 2-3 semaines pour évaluer l'efficacité des améliorations CLAUDE.md avant d'implémenter le hook.

## Impact Attendu

**Avant:**
- Exploration filesystem directe fréquente
- Contexte Second Brain sous-utilisé
- Redécouverte d'informations existantes

**Après:**
- Consultation systématique de la mémoire d'abord
- Meilleure utilisation du contexte accumulé
- Réduction de l'exploration filesystem redondante
- Respect de la hiérarchie: Mémoire → Docs → Filesystem

## Métriques de Succès

À surveiller sur 2-3 semaines:
- [ ] Nombre de violations (utilisation Bash avant mem0_search)
- [ ] Temps de recherche d'information (devrait diminuer)
- [ ] Utilisation de mem0_search (devrait augmenter)
- [ ] Feedback utilisateur sur respect de la règle

Si violations persistent → implémenter le hook pre-tool

## Fichiers Modifiés

- `~/.claude/CLAUDE.md` (user global)
- `~/Documents/APP_HOME/.claude/CLAUDE.md` (project)

**Note:** Les deux fichiers sont identiques et synchronisés via APP_HOME.

## Références

- [[../tools/second-brain|Second Brain Documentation]]
- [[../ideas/pre-tool-validation-hook|Pre-Tool Validation Hook]]
- Session: [[../../projects/dev/second-brain/sessions/2025-12-02-continuation|Session 2025-12-02]]
- Feedback utilisateur: "pourquoi utiliser bash en priorite plutot que les memoires et obsidian?"

---

**Tags:** #improvement #claude-md #second-brain #consultation-priority
**Priorité:** Critique
