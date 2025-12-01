# Feature: [NOM DE LA FEATURE]

**Date:** YYYY-MM-DD
**Author:** [Votre nom]
**Project:** [project-id]

---

## 1. Décision

### Problème résolu

Décrire le problème ou besoin que cette feature résout:
- Pourquoi cette feature est nécessaire?
- Quel pain point résout-elle?
- Quel bénéfice apporte-t-elle?

### Alternatives considérées

| Option | Avantages | Inconvénients | Décision |
|--------|-----------|---------------|----------|
| A. [Description] | - ... | - ... | ❌ Rejetée |
| B. [Description] | - ... | - ... | ❌ Rejetée |
| C. [Description] | - ... | - ... | ✅ **Choisie** |

**Raison du choix:** [Expliquer pourquoi option C]

---

## 2. Architecture

### Diagramme

```
[Diagramme ASCII de l'architecture]

Exemple:
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Component  │
└─────────────┘
```

### Fichiers impactés

**Code:**
- `~/path/to/file1.py` - [Description changement]
- `~/path/to/file2.sh` - [Description changement]

**Documentation:**
- `SecondBrain/wiki/tools/doc-file.md` - [Section à créer/modifier]

**Tests:**
- `tests/test_feature.py` - [Tests à écrire]

**Configuration:**
- `.mcp.json` - [Config à ajouter si applicable]
- `.env` - [Variables à ajouter si applicable]

### CODE-DOC-MAP Update

**Nouveaux mappings à ajouter:**

| Code File | Doc File | Section |
|-----------|----------|---------|
| ~/path/to/new_file.py | existing-doc.md | New Feature Section |

---

## 3. Implémentation

### Checklist OBLIGATOIRE

Avant de considérer la feature terminée:

**Code & Tests:**
- [ ] Code écrit et fonctionne
- [ ] Tests unitaires écrits
- [ ] Tests passent (100%)
- [ ] Code review (si équipe)

**Documentation:**
- [ ] Documentation Obsidian créée/mise à jour
- [ ] CODE-DOC-MAP.md mis à jour
- [ ] Exemples d'usage ajoutés
- [ ] Diagrammes/schémas créés

**Mémoire:**
- [ ] mem0_save décisions importantes
- [ ] _INDEX.md mis à jour si nouveau fichier doc
- [ ] Références croisées ajoutées

**Hooks & Commands:**
- [ ] Slash command ajouté si applicable
- [ ] Hook créé/modifié si applicable
- [ ] Pre-commit hook passe

**Validation:**
- [ ] Testé manuellement
- [ ] Edge cases considérés
- [ ] Rollback plan si critique

### Code Details

#### Changement 1: [Titre]

**Fichier:** `path/to/file.py`

**Avant:**
```python
# Code existant
def old_function():
    pass
```

**Après:**
```python
# Nouveau code
def new_function():
    """
    OBSIDIAN_DOC: doc-file.md#new-feature

    Description de la fonction
    """
    pass
```

**Rationale:** [Pourquoi ce changement]

#### Changement 2: [Titre]

[Même format...]

---

## 4. Monitoring & Safety

### Emergency Cases

Si cette feature touche des composants critiques:

- [ ] **Emergency buffer documenté** (si Mem0)
  - Comment ça marche en cas de lock?
  - Fallback si échec?

- [ ] **Backups documentés** (si data critique)
  - Quoi est sauvegardé?
  - Comment restaurer?

- [ ] **Monitoring ajouté** (metrics, logs)
  - Quelles métriques suivre?
  - Alertes configurées?

### Rollback Plan

**Si la feature cause des problèmes:**

1. **Immediate action:**
   ```bash
   # Commands pour rollback
   git revert [commit-hash]
   ```

2. **Data recovery (si applicable):**
   ```bash
   # Commands pour restaurer data
   cp backup.json current.json
   ```

3. **Communication:**
   - Qui notifier?
   - Quel message?

### Vérification Post-Deploy

- [ ] Hook pre-commit passe
- [ ] Command /end review OK
- [ ] Weekly audit clean (aucun nouveau gap)
- [ ] Monitoring metrics normales

---

## 5. Testing

### Tests Unitaires

**Fichier:** `tests/test_feature.py`

```python
def test_feature_basic():
    """Test cas de base"""
    assert feature() == expected_result

def test_feature_edge_case():
    """Test edge case"""
    assert feature(edge_input) == expected_output
```

### Tests Manuels

| Scénario | Steps | Résultat attendu | Status |
|----------|-------|------------------|--------|
| Happy path | 1. ... 2. ... | Success | ⏳ |
| Error handling | 1. ... 2. ... | Graceful error | ⏳ |
| Edge case | 1. ... 2. ... | Handled correctly | ⏳ |

---

## 6. Références

### Code

- Primary: `~/path/to/main_file.py`
- Related: `~/path/to/related_file.py`
- Tests: `tests/test_feature.py`

### Documentation

- Main doc: `SecondBrain/wiki/tools/doc-file.md#section`
- Related docs: `[[other-doc]]`

### Mémoire

- Project ID: `[project-id]`
- mem0_save timestamp: `[timestamp]`
- Decision record: `SecondBrain/projects/[project]/decisions/YYYY-MM-DD-feature-name.md`

### External

- GitHub Issue: `#123` (si applicable)
- Pull Request: `#456` (si applicable)
- External docs: [liens]

---

## 7. Notes & Lessons Learned

### Challenges rencontrés

- **Challenge 1:** [Description]
  - Solution: [Comment résolu]
  - Lesson: [Ce qu'on a appris]

### Optimisations futures

- [ ] [Optimisation possible 1]
- [ ] [Optimisation possible 2]

### Questions ouvertes

- [ ] Question 1 à investiguer
- [ ] Question 2 à résoudre

---

## Template Usage

**Comment utiliser ce template:**

1. Copier dans `SecondBrain/projects/[project]/features/YYYY-MM-DD-feature-name.md`
2. Remplir toutes les sections
3. Utiliser comme guide pendant implémentation
4. Cocher checkboxes au fur et à mesure
5. Référencer dans commit message: `feat: add X (see features/YYYY-MM-DD-feature-name.md)`

**Rappel:** Ce template garantit documentation complète et évite les gaps!
