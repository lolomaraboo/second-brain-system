# Documentation Automation

**Statut:** ✅ PRODUCTION
**Dernière mise à jour:** 2025-12-01

## Problème résolu

### Contexte

Audit du système Mem0 Auto-Sync (2025-12-01) a révélé **~930 lignes de code non documentées**:
- Emergency buffer system (mem0_emergency.json)
- Multi-machines setup (APP_HOME, setup.sh)
- Slash commands (/start, /end, /wiki)
- Hooks système (pre-session-start.sh, pre-commit)
- Backups automatiques
- MCP config location

### Cause racine

6 facteurs identifiés:
1. **Code-first development** - Code écrit sans documentation simultanée
2. **Évolution sans doc updates** - Features ajoutées, docs pas mises à jour
3. **Disconnection** - APP_HOME séparé du SecondBrain
4. **Pas de Definition of Done** - Documentation pas dans checklist
5. **Information scattered** - Décisions éparpillées dans Mem0/Obsidian/code
6. **Config confusion** - MCP location incorrectement documentée

### Conséquence

- Onboarding difficile (nouvelles machines)
- Bugs récurrents (cause oubliée)
- Drift entre code et docs
- Confiance réduite dans documentation

## Solution: 3-Layer System

```
┌─────────────────────────────────────────────────┐
│         Documentation Automation                │
├─────────────────┬─────────────┬─────────────────┤
│   Layer 1:      │  Layer 2:   │   Layer 3:      │
│   Reference     │  Prevention │   Monitoring    │
├─────────────────┼─────────────┼─────────────────┤
│ CODE-DOC-MAP    │ pre-commit  │ weekly-audit    │
│ FEATURE-TEMPLATE│ /end review │ extract-docs    │
└─────────────────┴─────────────┴─────────────────┘
```

### Layer 1: Reference (Source of Truth)

#### CODE-DOC-MAP.md

**Rôle:** Mapping unique code file → doc file

**Structure:**
```markdown
| Code File | Doc File | Section | Status |
|-----------|----------|---------|--------|
| ~/scripts/mem0_mcp_server.py | mem0-auto-sync-architecture.md | MCP Server | ✅ |
```

**Utilisé par:**
- Hook pre-commit (validation)
- Command /end (review)
- Script weekly-audit.sh (gap detection)

**Maintenance:**
- Ajouter ligne quand nouveau fichier code significatif créé
- Mettre status ⏳ → ✅ quand doc complétée
- Supprimer si fichier code supprimé

#### FEATURE-TEMPLATE.md

**Rôle:** Template standardisé pour features

**Sections obligatoires:**
1. **Décision** - Problème, alternatives, choix
2. **Architecture** - Diagramme, fichiers impactés
3. **Implémentation** - Checklist obligatoire, code details
4. **Monitoring & Safety** - Rollback plan, emergency cases
5. **Testing** - Tests unitaires et manuels
6. **Références** - Code, docs, mémoire
7. **Notes** - Challenges, lessons learned

**Checklist OBLIGATOIRE:**
```markdown
- [ ] Code écrit et testé
- [ ] Tests passent (100%)
- [ ] Documentation Obsidian créée/mise à jour
- [ ] CODE-DOC-MAP.md mis à jour
- [ ] mem0_save décisions importantes
- [ ] _INDEX.md mis à jour
- [ ] Hooks/commands ajoutés si applicable
- [ ] Pre-commit hook passe
```

**Usage:**
```bash
# Copier template pour nouvelle feature
cp SecondBrain/wiki/FEATURE-TEMPLATE.md \
   SecondBrain/projects/second-brain/features/2025-12-01-ma-feature.md

# Remplir sections pendant implémentation
# Cocher checkboxes au fur et à mesure
# Référencer dans commit message
git commit -m "feat: add X (see features/2025-12-01-ma-feature.md)"
```

### Layer 2: Prevention (Validation Gates)

#### pre-commit Hook

**Fichier:** `~/.claude/hooks/pre-commit`

**Rôle:** Bloquer commit si documentation manquante

**Validation (version améliorée à venir):**
```bash
# 1. Fichier code changé?
changed_files=$(git diff --cached --name-only)

# 2. Fichier dans CODE-DOC-MAP?
for file in $changed_files; do
    if grep -q "$file" CODE-DOC-MAP.md; then
        # 3. Doc correspondante aussi changée?
        doc_file=$(grep "$file" CODE-DOC-MAP.md | awk -F'|' '{print $3}')
        if ! echo "$changed_files" | grep -q "$doc_file"; then
            echo "❌ BLOCKED: $file changed but $doc_file not updated"
            exit 1
        fi
    fi
done
```

**Bypass (si vraiment nécessaire):**
```bash
git commit --no-verify -m "wip: emergency fix"
```

#### /end Command Review

**Fichier:** `~/.claude/commands/end.md`

**Rôle:** Review documentation avant save session

**Workflow (version améliorée à venir):**
1. User tape `/end`
2. Claude détecte fichiers code modifiés
3. Claude vérifie CODE-DOC-MAP.md
4. Claude propose: "Documentation à mettre à jour?"
5. User confirme ou skip
6. Claude exécute mem0_save + Obsidian update
7. Session close proprement

**Exemple dialogue:**
```
User: /end

Claude: 📝 Review documentation avant de sauvegarder:

Fichiers code modifiés:
- ~/scripts/mem0_mcp_server.py

Documentation correspondante (CODE-DOC-MAP):
- SecondBrain/wiki/tools/mem0-auto-sync-architecture.md

Ces fichiers docs sont-ils à jour? [o/n]

User: o

Claude: ✅ Sauvegarde session...
```

### Layer 3: Monitoring (Gap Detection)

#### weekly-doc-audit.sh

**Fichier:** `~/scripts/weekly-doc-audit.sh` (à créer)

**Rôle:** Détecter automatiquement les gaps hebdomadaires

**Checks:**
1. **Fichiers code non mappés**
   ```bash
   # Scripts
   for f in ~/scripts/mem0*.py; do
       grep -q "$(basename $f)" CODE-DOC-MAP.md || echo "Unmapped: $f"
   done
   ```

2. **Mappings obsolètes**
   ```bash
   # Fichiers code supprimés mais encore dans map
   grep '~/scripts' CODE-DOC-MAP.md | while read line; do
       file=$(echo "$line" | awk -F'|' '{print $2}')
       [ -f "$file" ] || echo "Obsolete mapping: $file"
   done
   ```

3. **Code changé sans doc update**
   ```bash
   # Comparer git log dates
   code_date=$(git log -1 --format=%ct ~/scripts/mem0_mcp_server.py)
   doc_date=$(git log -1 --format=%ct SecondBrain/wiki/tools/mem0-auto-sync-architecture.md)
   [ $code_date -gt $doc_date ] && echo "Gap: code newer than doc"
   ```

**Output exemple:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WEEKLY DOC AUDIT - 2025-12-01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Fichiers mappés: 11
⚠️  Gaps détectés: 2

❌ UNMAPPED FILES:
   - ~/scripts/backup_restore.py
   - ~/.claude/commands/debug.md

❌ CODE NEWER THAN DOC:
   - ~/scripts/mem0_queue_worker.py (code: 2025-12-01, doc: 2025-11-30)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action requise: Mettre à jour CODE-DOC-MAP.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Cron job (à configurer):**
```bash
# Chaque lundi 9h
0 9 * * 1 ~/scripts/weekly-doc-audit.sh | mail -s "Doc Audit" user@example.com
```

#### extract-obsidian-docs.py

**Fichier:** `~/scripts/extract-obsidian-docs.py` (à créer)

**Rôle:** Extraire documentation depuis code comments

**Utilise tag spécial:**
```python
def mem0_save(project_id: str, content: str):
    """
    OBSIDIAN_DOC: mem0-auto-sync-architecture.md#mcp-server

    Sauvegarde mémoire via MCP Mem0.

    Args:
        project_id: Identifiant projet
        content: Contenu à mémoriser
    """
    pass
```

**Extraction:**
```bash
# Trouver tous les tags OBSIDIAN_DOC
python3 ~/scripts/extract-obsidian-docs.py ~/scripts/mem0_mcp_server.py

# Output:
Found OBSIDIAN_DOC tag:
  File: mem0_mcp_server.py:105
  Doc: mem0-auto-sync-architecture.md#mcp-server
  Content: Sauvegarde mémoire via MCP Mem0...
```

**Auto-update (optionnel):**
```python
# Mettre à jour automatiquement le fichier doc
extract-obsidian-docs.py --auto-update ~/scripts/mem0_mcp_server.py
```

## Workflow complet

### Nouvelle feature

```bash
# 1. Copier template
cp FEATURE-TEMPLATE.md projects/second-brain/features/2025-12-01-ma-feature.md

# 2. Développer en suivant template
# - Écrire code
# - Ajouter OBSIDIAN_DOC tags
# - Remplir sections template
# - Cocher checkboxes

# 3. Ajouter mapping
echo "| ~/path/to/file.py | doc.md | Section | ⏳ |" >> CODE-DOC-MAP.md

# 4. Créer/Mettre à jour documentation
vim SecondBrain/wiki/tools/doc.md

# 5. Mettre status à ✅
sed 's/⏳/✅/' CODE-DOC-MAP.md

# 6. Commit (hook valide automatiquement)
git add .
git commit -m "feat: add feature X"

# 7. Review avec /end
/end
```

### Maintenance hebdomadaire

```bash
# Lundi matin: audit automatique
~/scripts/weekly-doc-audit.sh

# Si gaps détectés:
# 1. Ajouter mappings manquants à CODE-DOC-MAP.md
# 2. Mettre à jour docs obsolètes
# 3. Re-run audit pour confirmer
~/scripts/weekly-doc-audit.sh
```

## Metrics

### Before (2025-12-01 avant implémentation)

- Code documenté: ~60%
- Gaps identifiés: ~930 lignes
- MCP location: ❌ Incorrect
- Emergency buffer: ❌ Non documenté
- Slash commands: ❌ Non documenté
- Hooks: ❌ Non documenté

### After (objectif)

- Code documenté: 100%
- Gaps détectés automatiquement: < 24h
- Pre-commit validation: ✅ Active
- /end review: ✅ Active
- Weekly audit: ✅ Automatique

## Maintenance

### Mise à jour CODE-DOC-MAP

**Quand ajouter:**
- Nouveau fichier script (~/scripts/*.py, *.sh)
- Nouveau command (~/.claude/commands/*.md)
- Nouveau hook (~/.claude/hooks/*)
- Nouveau fichier config significatif

**Format:**
```markdown
| ~/path/to/file.ext | doc-file.md | Section Name | ⏳ |
```

**Status:**
- ⏳ - Documentation en cours
- ✅ - Documentation complète
- ❌ - Documentation bloquée (raison dans notes)

### Mise à jour FEATURE-TEMPLATE

Si nouvelle section nécessaire:
1. Ajouter section dans template
2. Expliquer rationale dans commit message
3. mem0_save la décision

### Mise à jour scripts audit

Si nouveaux patterns de fichiers:
1. Ajouter pattern à weekly-doc-audit.sh
2. Tester sur codebase actuel
3. Vérifier pas de faux positifs

## Troubleshooting

### Hook pre-commit bloque à tort

**Symptôme:** Hook bloque commit mais doc est à jour

**Causes possibles:**
1. Doc pas staged (`git add SecondBrain/wiki/...`)
2. Mauvais nom fichier dans CODE-DOC-MAP
3. Doc changée mais pas dans même commit

**Fix:**
```bash
# Vérifier fichiers staged
git diff --cached --name-only

# Ajouter doc manquante
git add SecondBrain/wiki/tools/doc.md

# Ou bypass si vraiment nécessaire
git commit --no-verify -m "..."
```

### Weekly audit détecte faux positifs

**Symptôme:** Script signale gap mais doc est à jour

**Causes possibles:**
1. Doc update dans commit séparé (dates différentes)
2. Fichier code refactoré mais même fonctionnalité
3. Pattern regex trop strict

**Fix:**
```bash
# Commit docs et code ensemble
git add code.py SecondBrain/wiki/doc.md
git commit -m "feat: X with documentation"

# Ou ajuster script si pattern incorrect
vim ~/scripts/weekly-doc-audit.sh
```

### extract-obsidian-docs.py ne trouve pas tags

**Symptôme:** Script ne détecte pas OBSIDIAN_DOC

**Causes possibles:**
1. Tag mal formaté (typo)
2. Tag pas dans docstring
3. Fichier pas analysé

**Fix:**
```python
# Format correct:
def function():
    """
    OBSIDIAN_DOC: doc-file.md#section

    Description...
    """
    pass

# Format INCORRECT:
def function():
    # OBSIDIAN_DOC: doc-file.md#section  ❌ (comment, pas docstring)
```

## Références

### Fichiers créés

- [[CODE-DOC-MAP]] - Mapping code→doc
- [[FEATURE-TEMPLATE]] - Template features
- `~/scripts/weekly-doc-audit.sh` (à créer)
- `~/scripts/extract-obsidian-docs.py` (à créer)

### Documentation liée

- [[mem0-auto-sync-architecture]] - Système Mem0 documenté
- [[claude-code-sync]] - Multi-machines setup
- [[slash-commands]] - Commands /start /end /wiki
- [[hooks]] - Hooks système

### Code

- `~/.claude/hooks/pre-commit` (à améliorer)
- `~/.claude/commands/end.md` (à améliorer)

### Décisions

- `SecondBrain/projects/second-brain/decisions/2025-12-01-doc-automation.md` (plan complet)

## Lessons Learned

### Ce qui a marché

- **CODE-DOC-MAP comme single source of truth** - Simple, clair, facile à maintenir
- **FEATURE-TEMPLATE avec checklist obligatoire** - Force discipline
- **3-layer approach** - Reference + Prevention + Monitoring = couverture complète

### Challenges

- **Adoption initiale** - Besoin discipline pour utiliser template systématiquement
- **Granularité CODE-DOC-MAP** - Tous les fichiers ou seulement "significatifs"?
- **Balance automation vs manual** - Pre-commit trop strict = friction, trop lax = gaps

### Next improvements possibles

- [ ] Badge "doc coverage %" dans README
- [ ] GitHub Action pour weekly audit automatique
- [ ] VSCode extension pour auto-insert OBSIDIAN_DOC tags
- [ ] Linter qui force FEATURE-TEMPLATE pour commits > 100 lines
