# Décision : /start intelligent avec mode rapide par défaut

**Date** : 2025-12-01
**Statut** : Implémenté
**Décideurs** : Claude + User
**Note** : Initialement prévu comme `/resume` séparé, mais conflit avec commande native Claude Code

## Contexte

Besoin de reprendre rapidement le travail après épuisement du contexte Claude (proche de la limite de tokens).

### Problème

Quand le contexte devient plein :
- `/start` traditionnel est lent (2-5s) car charge tout depuis Mem0 API + Obsidian
- Perte de temps à chaque reprise
- Workflow `/clear` puis `/start` inefficace pour quick check-in

### Use Case Principal

```bash
# Contexte devient plein (proche limite tokens)
/end     # Sauvegarde tout + génère resume.md
/clear   # Vide le contexte
/start   # Recharge rapidement via resume.md (<100ms)
# → On reprend exactement où on en était !
```

## Décision

Modifier `/start` pour avoir deux modes intelligents :
- **Mode rapide (par défaut)** : Lit resume.md si disponible (<100ms)
- **Mode complet (--full)** : Force Mem0 + Obsidian même si resume existe (2-5s)

**Rationale** : Pas de nouvelle commande à apprendre, `/start` devient intelligent.

## Solution Implémentée

### Architecture

```
~/.claude/
├── commands/
│   ├── start.md        ← MODIFIÉ (deux modes)
│   └── end.md          ← MODIFIÉ (génère resume.md)
├── last-project.txt    ← NOUVEAU (1 ligne: project-id)
└── resumes/            ← NOUVEAU DOSSIER
    └── [project-id]/
        └── resume.md   (20-30 lignes)
```

### Commande /start modifiée

**Usage:**
```bash
/start              # Mode rapide (resume.md si existe, sinon Mem0+Obsidian)
/start --full       # Mode complet (force Mem0+Obsidian)
/start [projet]     # Charge projet spécifié (mode rapide)
/start [projet] --full  # Charge projet spécifié (mode complet)
```

**Logique :**

1. **Détection du projet :**
   - Si argument fourni (pas --full) : utiliser comme project_id
   - Sinon : lire `~/.claude/last-project.txt`
   - Fallback : `basename` du répertoire courant

2. **Choix du mode :**
   - Si `--full` présent : **Mode complet**
   - Sinon : **Mode rapide** (par défaut)

3. **Mode rapide :**
   - Si `resume.md` existe et <7 jours : afficher resume
   - Si `resume.md` n'existe pas : passer automatiquement en mode complet
   - Si `resume.md` ≥7 jours : warning + suggérer `/start --full`

4. **Mode complet :**
   - Charge Mem0 + Obsidian (comportement original)

### Commande /end modifiée

**Nouvelle étape 3** : Génération automatique du resume

**Détection robuste du projet** :
1. **Argument explicite** : `/end [project-id]` (priorité)
2. **Git root** : `git rev-parse --show-toplevel` → robuste aux `cd`
3. **Fallback** : `basename "$PWD"`
4. **Confirmation** : Toujours demander confirmation à l'utilisateur

**Génération** :
- Crée `~/.claude/resumes/[project-id]/resume.md` (20-30 lignes)
- Écrit `~/.claude/last-project.txt` avec le project-id

### Format resume.md

```markdown
# Resume: [Project Name]
**Last Updated:** 2025-12-01 16:45:00
**Directory:** /full/path/to/project

## Current State
- [État du projet]

## Last Session Summary
[3-5 lignes]

## Key Decisions & Changes
- [Décision 1]: Rationale

## Important Files Modified
- `path/to/file.ts` - [What changed]

## Next Steps
- [ ] TODO item 1

---
**Full Session:** `~/.claude/sessions/session-[timestamp].md`
**Obsidian:** `~/SecondBrain/projects/[project]/_INDEX.md`
**Mem0:** [X] entries saved
```

## Problème Résolu : Détection robuste du projet

### Problème identifié

Si on fait `cd` pendant la session, `basename "$PWD"` dans `/end` ne reflète pas nécessairement le projet réel.

**Exemple** :
```bash
# Début de session
pwd → /path/to/recording-studio-manager

# Pendant la session
cd ../ClaudeCodeChampion/

# Fin de session
/end  # ❌ basename "$PWD" = ClaudeCodeChampion (incorrect!)
```

### Solution

Stratégie de détection en cascade :

1. **Argument explicite prioritaire** : `/end [project-id]`
2. **Git root automatique** : `git rev-parse --show-toplevel`
3. **Fallback sur pwd** : `basename "$PWD"`
4. **Confirmation utilisateur** : Toujours demander

### Test en live

Lors de cette session :
- `pwd` = `windsurf-project`
- Travail réel = `second-brain`
- User a utilisé `/end second-brain` pour forcer le bon projet
- ✅ Démontre l'utilité de la détection robuste + confirmation

## Pivot : /resume → /start intelligent

### Problème découvert

Claude Code a déjà une commande native `/resume` → conflit.

### Solution

Au lieu de créer `/resume` séparé :
- Modifier `/start` pour qu'il soit intelligent
- Mode rapide par défaut (resume.md)
- Mode complet avec `--full`

### Avantages

- ✅ Pas de conflit avec commandes natives
- ✅ Pas de nouvelle commande à apprendre
- ✅ `/start` devient plus puissant
- ✅ Backward compatible (si pas de resume → comportement normal)

## Conséquences

### Positives

- ✅ **Speed** : Mode rapide 20-50x plus rapide que mode complet
- ✅ **Auto-detection** : Pas besoin de spécifier le projet
- ✅ **DX** : Une seule commande avec modes intelligents
- ✅ **Offline** : Mode rapide pas de dépendance API
- ✅ **Robustesse** : Git root résout le problème du `cd`
- ✅ **Compatibilité** : Pas de conflit avec Claude Code natif

### Négatives

- ⚠️ Résumé limité (20-30 lignes) vs contexte complet
- ⚠️ Nécessite discipline : exécuter `/end` en fin de session

### Neutres

- Mode rapide complète mode complet, ne le remplace pas
- Resume atomique (pas d'historique, remplace le précédent)

## Fichiers Modifiés

1. `~/.claude/commands/start.md` (modifié - deux modes)
2. `~/.claude/commands/end.md` (modifié - génération resume)
3. `~/SecondBrain/wiki/tools/second-brain.md` (documentation)

## Workflows

### Context Exhaustion Recovery ⭐
```bash
/end → /clear → /start (mode rapide auto)
```

### Quick Check-In
```bash
/start (mode rapide) → [travail] → /end
```

### Deep Dive
```bash
/start --full → [session longue] → /end
```

### Context Switch
```bash
/start [projet-a] → [travail] → /end → /start [projet-b]
```

## Métriques de Succès

- ✅ `/start` mode rapide s'exécute en <100ms
- ✅ Détection automatique du dernier projet fonctionne
- ✅ Resume capture assez de contexte pour reprendre
- ✅ Pas de conflit avec commandes natives
- ✅ Backward compatible

## Références

- Plan : `~/.claude/plans/enchanted-popping-teapot.md`
- Pattern : [[context-exhaustion-recovery]]
- Session : 2025-12-01
