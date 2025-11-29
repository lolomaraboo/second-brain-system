# Multi-instances Claude Code

Guide pour exécuter plusieurs instances de Claude Code en parallèle.

## TL;DR

✅ **Safe** : Projets différents
⚠️ **Risqué** : Même projet, fichiers différents
❌ **Dangereux** : Même projet, mêmes fichiers

## Analyse par composant

### 1. ✅ Queue Mem0 - Aucun risque

Depuis 2025-11-29, file locking (`fcntl`) empêche les race conditions.

```
Instance A               Lock              Instance B
────────────            ──────            ────────────
mem0_save("Fix bug")    🔒 A              mem0_save("Feature")
✓ Écrit                                   ⏳ Attend 5s max...
                        🔓
                        🔒 B              ✓ Écrit
```

**Résultat** : Les 2 mémoires sont sauvegardées ✅

### 2. ⚠️ Mémoire VPS Mem0 - Confusion possible

Les 2 instances écrivent dans le **même project_id** :

```python
# Instance A (projet-x)
mem0_save("projet-x", "Je travaille sur le login")

# Instance B (projet-x)
mem0_save("projet-x", "Je travaille sur le dashboard")
```

**Au prochain `/start`** : Contextes mélangés
- "Le login est terminé"
- "Le login est en cours"
- Confusion mais pas de corruption

### 3. ⚠️ Git - Conflits classiques

```bash
# Instance A
edit src/utils.ts (ligne 10-20)
git commit -m "Add helper"

# Instance B
edit src/utils.ts (ligne 15-25)  # Overlap !
git commit -m "Fix bug"
git push  # ❌ CONFLIT
```

**Solution** : Branches Git différentes

### 4. ⚠️ Obsidian - Conflits de fichiers

```
Instance A : Edit wiki/architecture.md
Instance B : Edit wiki/architecture.md (même fichier)
```

Obsidian détecte et crée 2 versions avec suffixe timestamp.

### 5. ⚠️ Fichiers partagés - Mélange

Tous dans `~/.claude/` :
- `history.jsonl` : Historique mélangé
- `todos/` : Todos des 2 sessions
- `debug/` : Logs mélangés

## Scénarios

### ✅ SAFE : Projets différents

```bash
# Terminal 1
cd ~/projet-A
claude

# Terminal 2
cd ~/projet-B
claude
```

**Avantages :**
- Mem0 : project_id différents ✅
- Git : Repos différents ✅
- Pas de conflit ✅

### ⚠️ RISQUÉ : Même projet, fichiers différents

```bash
# Terminal 1 : Branche feature-login
cd ~/projet-x
git checkout -b feature-login
claude  # Travaille sur src/auth/

# Terminal 2 : Branche feature-dashboard
cd ~/projet-x
git checkout -b feature-dashboard
claude  # Travaille sur src/dashboard/
```

**Risques :**
- Mem0 : Contextes mélangés (confusion)
- Git : OK si fichiers différents
- Historique : Mélangé

**Mitigation :**
```bash
# Fin de session
/end  # Sauvegarde contexte

# Nouvelle session : contextes mélangés
/start  # Charge TOUT
```

### ❌ DANGEREUX : Même projet, mêmes fichiers

```bash
# Terminal 1
edit src/utils.ts

# Terminal 2
edit src/utils.ts  # Même fichier !
```

**Résultats garantis :**
- Git : CONFLIT
- Obsidian : Conflit si même .md
- Frustration : Maximale

## Recommandations

### Pour projets différents
```bash
terminal1: cd ~/projet-A && claude  ✅
terminal2: cd ~/projet-B && claude  ✅
```

### Pour même projet
```bash
# Option 1 : 1 seule instance (recommandé)
claude

# Option 2 : Branches différentes (acceptable)
terminal1: git checkout -b feat-a && claude
terminal2: git checkout -b feat-b && claude

# Option 3 : Même branche (déconseillé)
❌ Ne pas faire
```

### Bonnes pratiques

1. **Avant de lancer 2e instance**
   - Vérifier projet_id différent OU
   - Créer nouvelle branche Git

2. **En cas de doute**
   - Utiliser 1 seule instance
   - Sauver avec `/end` avant changement

3. **Après session partagée**
   - Vérifier contexte Mem0
   - Résoudre conflits Git si nécessaire

## Dépannage

### "Queue locked (timeout)"
```bash
# Attendre que l'autre instance finisse
# Ou forcer sync manuelle
python3 ~/scripts/mem0_queue_worker.py
```

### Contexte Mem0 mélangé
```bash
# Pas de solution automatique
# Utiliser mem0_search pour retrouver contexte pertinent
```

### Conflit Git
```bash
# Résolution classique
git status
git diff
# Éditer fichiers conflictuels
git add .
git commit
```

## Voir aussi

- [[file-locking-fcntl]] - Mécanisme de protection queue
- Projet : [[windsurf-project/decisions/2025-11-29-file-locking]]
