# Protection Multi-Sessions Claude Code

Documentation du système de protection pour travailler avec plusieurs sessions Claude en parallèle.

## Résumé

Ce système protège contre les conflits lors de l'utilisation de :
- **Git worktrees** : Plusieurs branches du même repo
- **Terminaux multiples** : 2+ sessions Claude en parallèle
- **Projets différents** : Safe par défaut
- **Même projet** : Détection et warnings

## Architecture

### Composants

1. **Session Tracking** : `~/.claude/obsidian_sessions.json`
   - Enregistre les sessions actives (PID, project_id, timestamp)
   - File locking pour éviter race conditions
   - Auto-cleanup des sessions mortes

2. **Lock /end** : `~/.claude/end.lock`
   - Empêche 2 sessions de sauvegarder simultanément
   - Timeout de 30 secondes
   - Cleanup automatique des locks orphelins

3. **Scripts** :
   - `~/scripts/obsidian_session_manager.py` : Gestion sessions
   - `~/.claude/shell-config/obsidian-session-helpers.sh` : Helpers Bash
   - `~/.claude/shell-config/end-lock-helpers.sh` : Lock /end

## Workflow

### Au démarrage de session (`/start`)

```bash
# 1. Enregistrer la session
~/scripts/obsidian_session_manager.py register [project_id] [cwd]

# 2. Vérifier les autres sessions
source ~/.claude/shell-config/obsidian-session-helpers.sh
obsidian_session_check [project_id]
```

**Résultats possibles :**
- ✅ Aucune autre session → OK
- ℹ️ Autres sessions sur projets différents → Info
- ⚠️ Autre session sur même projet → **WARNING**

### À la fin de session (`/end`)

```bash
# 1. Acquérir le lock (OBLIGATOIRE)
source ~/.claude/shell-config/end-lock-helpers.sh
end_with_lock

# 2. Sauvegarder (Mem0 + Obsidian + Resume)
# ... votre logique de sauvegarde ...

# 3. Cleanup (OBLIGATOIRE)
python3 ~/scripts/obsidian_session_manager.py unregister
end_lock_release
```

## Scénarios d'utilisation

### ✅ Scénario 1 : Projets différents (SAFE)

```bash
# Terminal 1
cd ~/windsurf-project/recording-studio-manager
# → project_id = "recording-studio-manager"

# Terminal 2
cd ~/windsurf-project/ClaudeCodeChampion
# → project_id = "claude-code-champion-v4"
```

**Résultat :** Aucun conflit, totalement safe.

### ⚠️ Scénario 2 : Même projet, worktrees différents

```bash
# Terminal 1
cd ~/windsurf-project
git worktree add ../windsurf-feat-a feature-a

# Terminal 2
cd ../windsurf-feat-a
```

**Risques :**
- Modification simultanée de fichiers Obsidian → conflit Git
- 2 sessions font `/end` en même temps → lock protège

**Protection :**
- Lock `/end` : ✅ Protégé (une session attend l'autre)
- Session tracking : ⚠️ Warning au `/start`
- Recommandation : Coordonner les `/end` manuellement

### 🚫 Scénario 3 : Même projet, même worktree (DÉCONSEILLÉ)

```bash
# Terminal 1
cd ~/windsurf-project

# Terminal 2
cd ~/windsurf-project
```

**Risques :**
- Git index partagé → corruption possible
- Même fichiers Obsidian → conflits
- Confusion sur l'état du projet

**Protection :**
- Lock `/end` : ✅ Protégé
- Session tracking : ⚠️ Warning fort
- Recommandation : **Ne pas faire**

## Détails techniques

### Session Tracking

**Fichier :** `~/.claude/obsidian_sessions.json`

```json
{
  "sessions": [
    {
      "pid": 12345,
      "project_id": "recording-studio-manager",
      "cwd": "/path/to/project",
      "started": "2025-12-01T14:30:00",
      "last_active": "2025-12-01T14:35:00"
    }
  ]
}
```

**Fonctionnement :**
- PID = PID du shell parent (détecté via `$PPID`)
- Cleanup automatique des PIDs morts
- File locking avec `fcntl` (timeout 5s)

### Lock /end

**Fichier :** `~/.claude/end.lock`

```
<PID du process qui détient le lock>
```

**Fonctionnement :**
1. Vérifier si lock existe
2. Si oui, attendre (max 30s)
3. Si timeout, avertir l'utilisateur
4. Créer lock avec PID
5. Exécuter sauvegarde
6. Supprimer lock

**Cleanup automatique :**
- Détecte les locks orphelins (PID mort)
- Supprime automatiquement

### File Locking

**Pourquoi ?**
- Évite race conditions lors d'accès concurrent
- Protège l'intégrité des fichiers JSON
- Safe pour 2+ instances Claude

**Comment ?**
```python
import fcntl

fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Non-blocking
# ... opération critique ...
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
```

## Commandes utiles

```bash
# Lister les sessions actives
python3 ~/scripts/obsidian_session_manager.py list

# Vérifier les conflits
python3 ~/scripts/obsidian_session_manager.py check [project_id]

# Enregistrer une session manuellement
python3 ~/scripts/obsidian_session_manager.py register [project] [cwd]

# Supprimer une session
python3 ~/scripts/obsidian_session_manager.py unregister [pid]

# Forcer suppression du lock /end (si bloqué)
rm ~/.claude/end.lock

# Vérifier l'état des locks
ls -la ~/.claude/*.lock
```

## Troubleshooting

### Lock /end bloqué ?

```bash
# Vérifier qui détient le lock
cat ~/.claude/end.lock

# Vérifier si le process existe
ps -p $(cat ~/.claude/end.lock)

# Si le process est mort, supprimer le lock
rm ~/.claude/end.lock
```

### Session orpheline ?

```bash
# Lister les sessions
python3 ~/scripts/obsidian_session_manager.py list

# Cleanup manuel
python3 ~/scripts/obsidian_session_manager.py unregister [pid]
```

### Conflit Git dans SecondBrain ?

```bash
cd ~/path/to/SecondBrain/

# Voir les conflits
git status

# Résoudre manuellement
# 1. Éditer les fichiers en conflit
# 2. git add .
# 3. git commit
```

## Limitations connues

1. **Détection PID** : `$PPID` est en lecture seule
   - Impossible de simuler des PIDs différents en tests
   - Fonctionne correctement avec de vraies sessions Claude

2. **Worktrees** : Protection partielle
   - Lock `/end` protège la sauvegarde
   - Mais modifications Obsidian pendant session non bloquées
   - Recommandation : Coordonner manuellement

3. **Git index** : Pas de protection
   - Si 2 sessions modifient le même worktree
   - Risque de corruption de l'index Git
   - Recommandation : Utiliser des worktrees séparés

## Recommandations

### ✅ FAIRE

- Travailler sur des **projets différents** en parallèle
- Utiliser **git worktrees** pour features séparées
- **Coordonner les `/end`** si même projet
- **Vérifier les warnings** au `/start`

### 🚫 NE PAS FAIRE

- 2 sessions sur le **même worktree**
- Ignorer les **warnings** de session
- Forcer suppression du lock `/end` **sans vérifier**
- Modifier **SecondBrain/** en parallèle

## Tests

Scripts de test disponibles :
- `/tmp/test-multi-sessions.sh` : Tests basiques
- `/tmp/test-concurrent-sessions.sh` : Tests parallèles

```bash
# Exécuter les tests
/tmp/test-multi-sessions.sh
/tmp/test-concurrent-sessions.sh
```

## Changelog

- **2025-12-01** : Implémentation initiale
  - Session tracking avec file locking
  - Lock /end avec timeout 30s
  - Intégration `/start` et `/end`
  - Documentation complète
