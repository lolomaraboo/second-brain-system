# Code-Documentation Mapping

**Statut:** ✅ PRODUCTION
**Dernière mise à jour:** 2025-12-01

## Vue d'ensemble

Table de référence unique: fichier code → documentation Obsidian

**Usage:**
- Référence pour savoir où documenter chaque fichier code
- Utilisé par hook `pre-commit` pour validation automatique
- Utilisé par `weekly-doc-audit.sh` pour détecter gaps
- Utilisé par command `/end` pour review documentation

## Mapping actuel

| Code File | Doc File | Section | Status |
|-----------|----------|---------|--------|
| ~/scripts/mem0_mcp_server.py | mem0-auto-sync-architecture.md | MCP Server | ✅ |
| ~/scripts/mem0_queue_worker.py | mem0-auto-sync-architecture.md | Worker | ✅ |
| ~/scripts/weekly-doc-audit.sh | doc-automation.md | Weekly Audit | ✅ |
| ~/scripts/extract-obsidian-docs.py | doc-automation.md | Extract Docs | ✅ |
| ~/.claude/commands/start.md | slash-commands.md | /start | ✅ |
| ~/.claude/commands/end.md | slash-commands.md | /end | ✅ |
| ~/.claude/commands/wiki.md | slash-commands.md | /wiki | ✅ |
| ~/.claude/hooks/pre-session-start.sh | hooks.md | pre-session-start | ✅ |
| ~/.claude/hooks/pre-session-close.sh | hooks.md | pre-session-close | ✅ |
| ~/.claude/hooks/pre-compact.sh | hooks.md | pre-compact | ✅ |
| ~/.claude/hooks/pre-commit | hooks.md | pre-commit | ✅ |
| ~/Documents/APP_HOME/.claude/shell-config/setup.sh | claude-code-sync.md | Installation | ✅ |
| ~/Documents/APP_HOME/.claude/shell-config/aliases.sh | claude-code-sync.md | Alias shell | ✅ |
| ~/scripts/obsidian_session_manager.py | multi-session-protection.md | Session Manager | ✅ |
| ~/.claude/shell-config/obsidian-session-helpers.sh | multi-session-protection.md | Obsidian Helpers | ✅ |
| ~/.claude/shell-config/end-lock-helpers.sh | multi-session-protection.md | Lock Helpers | ✅ |
| ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/scripts/sync-to-vps.sh | mem0-local-vps-backup.md | Backup Script | ✅ |

## Statistiques

- **Total mappings:** 17
- **Status ✅:** 17 (100%)
- **Dernière vérification:** 2025-12-02

## Ajouter un nouveau mapping

Quand tu crées un nouveau fichier code significatif:

1. **Déterminer quel fichier doc correspond:**
   - Fonctionnalité Mem0 → `mem0-auto-sync-architecture.md`
   - Slash command → `slash-commands.md`
   - Hook système → `hooks.md`
   - Multi-machines → `claude-code-sync.md`
   - Autre → créer nouvelle doc si besoin

2. **Ajouter ligne au tableau:**
   ```markdown
   | ~/path/to/file.py | doc-file.md | Section Name | ⏳ |
   ```

3. **Créer/Mettre à jour la documentation:**
   - Ajouter section dans le fichier doc
   - Documenter le code

4. **Mettre status à ✅:**
   ```markdown
   | ~/path/to/file.py | doc-file.md | Section Name | ✅ |
   ```

## Validation automatique

### Pre-commit hook

Le hook `~/.claude/hooks/pre-commit` vérifie automatiquement:
- Fichier code changé → doc correspondante aussi changée
- Bloque commit si doc manquante

### Weekly audit

Le script `~/scripts/weekly-doc-audit.sh` génère rapport:
- Fichiers code sans mapping
- Mappings obsolètes (fichiers manquants)
- Code changé sans doc update

### Command /end

Le command `/end` propose review documentation avant save.

## Maintenance

**Vérification manuelle:**
```bash
# Vérifier tous les fichiers existent
while IFS='|' read -r code doc section status; do
    [ -f "${code// /}" ] || echo "Missing: $code"
done < CODE-DOC-MAP.md
```

**Trouver fichiers non mappés:**
```bash
# Scripts
for f in ~/scripts/mem0*.py; do
    grep -q "$(basename $f)" CODE-DOC-MAP.md || echo "Unmapped: $f"
done

# Commands
for f in ~/.claude/commands/*.md; do
    grep -q "$(basename $f)" CODE-DOC-MAP.md || echo "Unmapped: $f"
done

# Hooks
for f in ~/.claude/hooks/*.sh; do
    grep -q "$(basename $f)" CODE-DOC-MAP.md || echo "Unmapped: $f"
done
```

## Références

- [[doc-automation]] - Système d'automatisation documentation
- [[hooks]] - Hooks système et pre-commit
- [[slash-commands]] - Command /end avec doc review
- Script: `~/scripts/weekly-doc-audit.sh`
