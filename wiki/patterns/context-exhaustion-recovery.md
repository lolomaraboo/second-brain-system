# Pattern : Context Exhaustion Recovery

**Type** : Workflow Pattern
**Domaine** : Claude Code - Second Brain
**Use Case** : Reprendre rapidement après épuisement du contexte

## Problème

Quand le contexte Claude devient plein (proche de la limite de tokens) :
- Impossible d'ajouter plus d'informations
- Charger tout le contexte est lent (2-5s)
- Perte de temps et momentum
- Frustration de devoir tout recharger

## Solution

Workflow en 3 étapes avec `/start` intelligent :

```bash
/end     # Sauvegarde tout + génère resume.md + last-project.txt
/clear   # Vide le contexte Claude
/start   # Recharge automatiquement en mode rapide (<100ms)
```

## Architecture

```
Session workflow :

START                    WORK                    END
  |                        |                       |
  v                        |                       v
/start (mode rapide)       |                    /end
  |                        |                       ├─ mem0_save
  ├─ Lit resume.md         |                       ├─ Obsidian proposal
  └─ <100ms                |                       ├─ Génère resume.md
                           |                       └─ Écrit last-project.txt
                           v
                    Décisions, fichiers,
                    TODOs trackés
```

## Implémentation

### Fichiers

```
~/.claude/
├── commands/
│   ├── start.md        # Deux modes (rapide/complet)
│   └── end.md          # Génère resume
├── last-project.txt    # 1 ligne: project-id
└── resumes/
    └── [project-id]/
        └── resume.md   # 20-30 lignes
```

### Commandes

**`/start`** : Mode intelligent
- **Par défaut** : Lit resume.md si disponible (<100ms)
- **Avec --full** : Force Mem0 + Obsidian (2-5s)
- Détection auto du dernier projet via `last-project.txt`

**`/end`** : Sauvegarde + génération
- Mem0 : Sauvegarde contexte de travail
- Obsidian : Propose documentation si nécessaire
- Resume : Génère `resume.md` + écrit `last-project.txt`

**`/clear`** : Vide le contexte
- Libère les tokens
- Contexte vierge

## Cas d'Usage

### 1. Context Exhaustion (principal)

```bash
# Contexte plein (95% des tokens utilisés)
/end     # Sauvegarde tout
/clear   # Reset
/start   # Recharge en mode rapide (<100ms)
# → Continue le travail avec contexte frais
```

### 2. Quick Check-In

```bash
# Début de journée
/start  # Mode rapide auto (20-30 lignes)
# Travail rapide...
/end     # Sauvegarde
```

### 3. Context Switch

```bash
# Projet A → Projet B
/start recording-studio-manager  # Mode rapide
# Travail...
/end

# Switch
/start claude-code-champion  # Mode rapide
# Travail...
/end
```

### 4. Deep Dive

```bash
# Session longue avec besoin contexte complet
/start --full   # Force Mem0 + Obsidian
# Travail intense...
/end     # Sauvegarde + génère resume

# Lendemain - Quick check
/start  # Mode rapide suffit
```

## Comparaison des modes

| Aspect | /start (rapide) | /start --full |
|--------|-----------------|---------------|
| **Speed** | <100ms | 2-5s |
| **Source** | resume.md local | Mem0 API + Obsidian |
| **Completeness** | 20-30 lignes | Complet |
| **Détection** | Auto via last-project.txt | Auto via last-project.txt |
| **When** | Quick check-in, 80% des cas | Deep dive, 20% des cas |

## Bénéfices

1. **Performance** : 20-50x plus rapide en mode rapide
2. **Fluidité** : Pas de friction pour reprendre
3. **Autonomie** : Mode rapide offline-friendly
4. **Simplicité** : Une seule commande avec modes intelligents
5. **Robustesse** : Détection git root (résiste aux `cd`)
6. **Compatibilité** : Pas de conflit avec commandes natives Claude Code

## Anti-Patterns

❌ **Ne pas utiliser /start (rapide) pour :**
- Première session sur un projet (pas de resume encore → passe auto en mode complet)
- Resume obsolète (≥7 jours → warning affiché)

✅ **Utiliser /start --full quand :**
- Besoin de tout le contexte historique Mem0
- Deep dive avec décisions importantes
- Resume affiché comme obsolète

## Exemples Réels

### Session 2025-12-01 : Pivot /resume → /start

**Contexte** :
- Initialement créé `/resume` comme commande séparée
- Découvert conflit avec commande native Claude Code

**Solution** :
- Pivot vers `/start` intelligent avec deux modes
- Mode rapide par défaut, `--full` pour complet
- Pas de nouvelle commande à apprendre

**Lesson** : Toujours vérifier les commandes natives avant d'en créer

### Session 2025-12-01 : Test détection projet

**Contexte** :
- `pwd` = `windsurf-project`
- Travail réel = `second-brain`

**Solution** :
```bash
/end second-brain  # Force le bon projet
# Confirmation : "💾 Saving context for project 'second-brain' - Proceed?"
# → Sauvegarde correcte malgré pwd différent
```

**Lesson** : Détection git root + confirmation évite les erreurs

## Format resume.md

**Sections (20-30 lignes)** :
- Current State
- Last Session Summary (3-5 lignes)
- Key Decisions & Changes
- Important Files Modified (top 5)
- Next Steps (TODOs)
- Références (session complète, Obsidian, Mem0)

**Atomicité** :
- Remplace le précédent (pas d'historique)
- Focus sur la session la plus récente

## Métriques

**Performance** :
- `/start` (rapide) : <100ms
- `/start --full` : 2-5s
- Gain : 20-50x

**Usage recommandé** :
- Quick check-in : `/start` (80% des cas)
- Deep dive : `/start --full` (20% des cas)

## Voir Aussi

- [[second-brain]] - Guide d'utilisation
- Decision : [[2025-12-01-start-intelligent]]
- Commandes : `~/.claude/commands/start.md`, `~/.claude/commands/end.md`
