# Sync Claude Config

## Architecture

- **Source de vérité** : `~/.claude/` (config locale active)
- **Backup versionné** : `SecondBrain/claude-config/` (Git)

## Script de synchronisation

```bash
# Backup quotidien (sync vers Git)
./scripts/sync-claude-config.sh to-backup

# Voir les différences
./scripts/sync-claude-config.sh diff

# Restaurer depuis le backup (⚠️ écrase ~/.claude/)
./scripts/sync-claude-config.sh from-backup
```

## Flux de travail

### 1. Modifications locales (quotidien)

```bash
# Vous modifiez ~/.claude/commands/my-command.md
vim ~/.claude/commands/my-command.md

# Sync vers SecondBrain/
./scripts/sync-claude-config.sh to-backup

# Commit dans SecondBrain/
cd SecondBrain/
git add claude-config/
git commit -m "feat: update my-command"
git push
```

### 2. Hook Git automatique

Installez le hook pour sync automatique avant chaque commit :

```bash
cd SecondBrain/
ln -sf ../../hooks/pre-commit-claude-sync .git/hooks/pre-commit
```

Maintenant chaque `git commit` dans SecondBrain/ synchronisera automatiquement depuis `~/.claude/`.

### 3. Restauration (nouvelle machine)

```bash
# Cloner le repo
git clone <url> SecondBrain/
cd SecondBrain/

# Restaurer la config
./scripts/sync-claude-config.sh from-backup

# ~/.claude/ est maintenant configuré !
```

## Ce qui est synchronisé

✅ **Versionné** :
- `commands/` - Slash commands
- `hooks/` - Git hooks
- `shell-config/` - Helpers bash
- `resumes/` - Templates de resume
- `CLAUDE.md` - Instructions
- `agents/` - Config agents
- `config/` - Config générale
- `settings.json` - Settings

🚫 **Ignoré** (cache/secrets) :
- `projects/` (359M cache)
- `file-history/` (70M)
- `debug/` (50M logs)
- `.env` (secrets)
- `logs/`, `*.log`
- `history.jsonl`

## Avantages

1. **Backup automatique** : Chaque commit = backup de la config
2. **Multi-machines** : Cloner SecondBrain = config synchronisée
3. **Historique** : Git track tous les changements de config
4. **Sécurité** : `.env` et secrets jamais versionnés
5. **Performance** : Cache local (projects/, file-history/) pas copié

## Dépannage

**Conflit de sync** :
```bash
# Voir les différences
./scripts/sync-claude-config.sh diff

# Forcer le push
./scripts/sync-claude-config.sh to-backup

# Ou forcer le pull
./scripts/sync-claude-config.sh from-backup
```

**Hook Git ne fonctionne pas** :
```bash
# Vérifier le symlink
ls -la .git/hooks/pre-commit

# Réinstaller
ln -sf ../../hooks/pre-commit-claude-sync .git/hooks/pre-commit
chmod +x hooks/pre-commit-claude-sync
```
