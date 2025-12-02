# Fix: Commande /start - Relecture CLAUDE.md obligatoire

**Date :** 2025-12-01
**Type :** Bug fix / Amélioration système
**Impact :** Critique - Mémorisation automatique

## Symptôme

Après l'implémentation du système de protection multi-sessions, aucune mémorisation automatique n'a été effectuée :
- ❌ Pas de `mem0_save` automatique après l'implémentation
- ❌ Pas de proposition Obsidian pour la décision architecturale
- ❌ L'assistant a dit "sauvegardé" sans vérifier le résultat

## Cause racine

La commande `/start` ne forçait **pas** la relecture active de `CLAUDE.md`.

**Contexte :**
- `CLAUDE.md` est fourni dans un `<system-reminder>` au début de session
- Mais c'est **passif** : l'assistant ne le révise pas activement
- Résultat : oubli des règles de mémorisation automatique

**Règles oubliées (CLAUDE.md lignes 54-68) :**
```
**Pendant l'exécution :**
- Après chaque commit important
- Après création de repo/fichier significatif
- Après configuration établie
- Après décision technique prise

**Règle : Ne pas attendre que l'utilisateur demande.**
```

## Solution

Modification de `~/.claude/commands/start.md` pour ajouter **Étape 0 CRITIQUE** :

### Mode Rapide (lignes 28-30)
```markdown
**Étape 0 - Relire instructions (TOUJOURS en premier) :**
- Lire `~/.claude/CLAUDE.md` avec le Read tool
- Réviser section "Mémoire automatique" (lignes 54-68)
```

### Mode Complet (lignes 43-47)
```markdown
**0. CRITIQUE - Relire les instructions de mémorisation (TOUJOURS en premier) :**
   - Lire `~/.claude/CLAUDE.md` avec le Read tool
   - **Section obligatoire à réviser** : "Mémoire automatique (Mem0 + Obsidian)"
   - Lignes 54-68 : Règles de sauvegarde automatique (SANS attendre que l'utilisateur demande)
   - **Se rappeler** : mem0_save après chaque décision technique/config/commit important
```

## Impact

**Avant :**
- Mémorisation oubliée après tâches complexes
- Utilisateur doit rappeler manuellement

**Après :**
- Relecture systématique au `/start`
- Rappel actif des règles de mémorisation
- Comportement automatique respecté

## Test

À vérifier lors du prochain `/start` :
- [ ] CLAUDE.md est bien lu avec le Read tool
- [ ] Section "Mémoire automatique" est révisée
- [ ] Mémorisation automatique fonctionne après tâches importantes

## Fichiers modifiés

- `~/.claude/commands/start.md` (lignes 28-30, 43-47)
- Synchronisé avec `SecondBrain/.claude/commands/start.md`

## Mémorisation

- Mem0 : Sauvegardé dans project `second-brain`
- Obsidian : Ce fichier
