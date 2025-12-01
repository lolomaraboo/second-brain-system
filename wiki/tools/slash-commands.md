# Slash Commands Second Brain

**Statut:** ✅ PRODUCTION

## Vue d'ensemble

Les slash commands sont des commandes personnalisées pour Claude Code qui simplifient l'interaction avec le Second Brain (Mem0 + Obsidian).

## Architecture

```
User tape: /start
     │
     ▼
┌─────────────────────────────────────┐
│ Claude Code lit:                    │
│ ~/.claude/commands/start.md        │
│ (frontmatter YAML + instructions)   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Claude exécute les instructions     │
│ - Détecte projet                    │
│ - Lit resume.md OU                  │
│ - Appelle mem0_recall + lit Obsidian│
└─────────────────────────────────────┘
```

## Slash Commands disponibles

### /start - Charger contexte

**Fichier:** `~/.claude/commands/start.md`

**Description:** Charge le contexte Second Brain du projet avec deux modes intelligents.

**Usage:**
```
/start                  # Mode rapide (resume.md si disponible)
/start --full           # Mode complet (Mem0 + Obsidian)
/start [projet]         # Charge projet spécifié (mode rapide)
/start [projet] --full  # Charge projet spécifié (mode complet)
```

**Détection projet:**
1. Si argument fourni → utiliser comme project_id
2. Sinon → lire `~/.claude/last-project.txt` (écrit par /end)
3. Fallback → `basename` du répertoire courant

**Mode Rapide (défaut):**
- Lit `~/.claude/resumes/[project]/resume.md`
- Vérifie âge du resume (< 7 jours recommandé)
- Affichage < 100ms
- Rappel: "💡 Pour le contexte complet : /start --full"

**Mode Complet (--full):**
- Appelle `mem0_recall` pour charger mémoires
- Lit `SecondBrain/projects/[projet]/_INDEX.md` et fichiers liés
- Présente résumé structuré
- Durée: 2-5s

**Avantages:**
- Performance: 20-50x plus rapide en mode rapide
- Intelligent: détection automatique du meilleur mode
- Backward compatible: si pas de resume → mode complet auto

### /end - Sauvegarder session

**Fichier:** `~/.claude/commands/end.md`

**Description:** Sauvegarde le contexte de la session complète (Mem0 + Obsidian + Resume).

**Usage:**
```
/end              # Détection auto du projet
/end [projet]     # Force le projet spécifié
```

**Détection projet (robuste):**
1. Si argument fourni → utiliser
2. Essaye `git rev-parse --show-toplevel | xargs basename`
3. Fallback → `basename "$PWD"`
4. **Confirmation:** "💾 Saving context for project '[project]' - Proceed? (y/n)"

**Actions:**

1. **Mem0 Save:**
   - Ce qui a été accompli
   - Décisions techniques prises
   - Problèmes et solutions
   - Prochaines étapes

2. **Obsidian (avec confirmation):**
   Propose mise à jour si:
   - Décision architecturale importante
   - Nouveau pattern/outil découvert
   - Debug non-trivial résolu
   - Nouvelle config/secret ajouté

3. **Resume File (automatique):**
   - Crée `~/.claude/resumes/[project]/resume.md`
   - Écrit `~/.claude/last-project.txt` (pour /start)
   - Contenu (20-30 lignes):
     - État actuel
     - Résumé session (3-5 lignes)
     - Décisions clés
     - Top 5 fichiers modifiés
     - Prochaines étapes (TODOs)
     - Références (Obsidian, Mem0)

### /wiki - Ajouter note Obsidian

**Fichier:** `~/.claude/commands/wiki.md`

**Description:** Ajoute une note au wiki Obsidian.

**Usage:**
```
/wiki [texte de la note]
```

**Catégories auto-détectées:**
- `projects/[projet]/` - Note spécifique au projet
- `wiki/patterns/` - Pattern réutilisable
- `wiki/tools/` - Documentation outil
- `wiki/secrets/` - Doc secret (JAMAIS la valeur!)
- `wiki/troubleshooting/` - Solution problème
- `ideas/` - Idée/brainstorming

**Actions:**
1. Crée fichier markdown atomique (max 50-100 lignes)
2. Met à jour `_INDEX.md` du dossier
3. Demande confirmation avant écriture

## Fichiers slash commands

**Location:** `~/.claude/commands/`

**Synchronisé:** ✅ Oui (via APP_HOME)

**Structure fichier:**
```markdown
---
description: Description courte du command
---

Instructions pour Claude...

Peut utiliser:
- $ARGUMENTS : Arguments passés au command
- Outils MCP : mem0_save, mem0_recall, etc.
- Outils Claude : Read, Write, Edit, Bash, etc.
```

## Créer un slash command custom

### Étape 1: Créer le fichier

```bash
# Créer dans ~/.claude/commands/
nano ~/.claude/commands/my-command.md
```

### Étape 2: Ajouter le frontmatter YAML

```markdown
---
description: Description de mon command
---
```

### Étape 3: Écrire les instructions

```markdown
Fais ceci avec les arguments:
$ARGUMENTS

Utilise les outils:
- mem0_search pour trouver...
- Read pour lire...
```

### Étape 4: Tester

```
/my-command arg1 arg2
```

## Exemples de custom commands

### /debug - Session de debug

```markdown
---
description: Lance une session de debug assistée
---

1. Demande à l'utilisateur de décrire le bug
2. Utilise mem0_search pour chercher bugs similaires
3. Analyse le code avec Read
4. Propose des hypothèses
5. Guide l'utilisateur dans le debug
6. Sauvegarde la solution avec mem0_save
```

### /deploy - Déploiement

```markdown
---
description: Checklist de déploiement
---

1. Vérifie que tous les tests passent (pytest)
2. Vérifie git status (aucun uncommitted)
3. Crée un tag de version
4. Push vers GitHub
5. Déclenche CI/CD
6. Vérifie déploiement
7. Sauvegarde dans Mem0
```

### /review - Code review

```markdown
---
description: Review du code modifié
---

1. Utilise git diff pour voir changements
2. Analyse:
   - Qualité code
   - Sécurité (OWASP top 10)
   - Performance
   - Tests
3. Propose améliorations
4. Sauvegarde review dans Obsidian
```

## Workflow Context Exhaustion Recovery

Quand le contexte devient trop long (beaucoup d'échanges, fichiers lus):

```bash
# 1. Sauvegarder tout
/end

# 2. Vider le contexte
/clear

# 3. Recharger (mode rapide)
/start
```

**Temps total:** ~5-10 secondes
**Résultat:** Contexte frais avec résumé complet

## Variables disponibles

Dans les slash commands, Claude a accès à:

- `$ARGUMENTS` - Arguments passés au command
- `$PWD` - Répertoire courant
- Outils MCP (mem0_*, mcp__*)
- Outils Claude (Read, Write, Edit, Bash, etc.)

## Troubleshooting

### Command non reconnu

**Symptôme:** `/my-command` → "Unknown command"

**Diagnostic:**
```bash
ls -la ~/.claude/commands/my-command.md
```

**Solution:**
- Vérifier que le fichier existe
- Vérifier permissions (doit être lisible)
- Redémarrer session Claude Code

### Command ne s'exécute pas

**Symptôme:** Command reconnu mais ne fait rien

**Diagnostic:**
```bash
cat ~/.claude/commands/my-command.md
```

**Solution:**
- Vérifier frontmatter YAML valide
- Vérifier instructions claires pour Claude
- Tester avec des instructions plus simples

### Arguments non passés

**Symptôme:** `$ARGUMENTS` est vide

**Solution:**
- Utiliser: `/command arg1 arg2` (avec espace)
- Dans le .md, accéder via `$ARGUMENTS`

## Best Practices

✅ **DO:**
- Frontmatter YAML obligatoire
- Description claire et concise
- Instructions step-by-step
- Utiliser mem0_save pour mémoriser
- Demander confirmation avant actions destructives

❌ **DON'T:**
- Pas d'instructions ambiguës
- Pas d'actions destructives sans confirmation
- Pas de logique trop complexe (créer agent à la place)

## Références

- [[second-brain]] - Système mémoire persistante
- [[claude-code-sync]] - Synchronisation multi-machines
- Location: `~/.claude/commands/`
- Documentation officielle: https://docs.anthropic.com/claude-code
