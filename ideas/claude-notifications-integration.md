# Claude Notifications Integration

**Date**: 2025-12-01
**Statut**: À évaluer (test minimal)
**Repo**: https://github.com/777genius/claude-notifications-go

## Description

Plugin Go pour Claude Code qui envoie des notifications intelligentes sur l'état des tâches.

## Contexte

Actuellement, pas de notifications quand :
- Une tâche longue se termine (ex: backup, sync, build)
- Claude pose une question (mode async)
- Le contexte devient long (session limit)
- Erreur API (401, session expired)

## Solution proposée

Installer **claude-notifications-go** :
- **Détection intelligente** via state machine (6 types)
  - Task Complete ✅
  - Review Complete 🔍
  - Question ❓
  - Plan Ready 📋
  - Session Limit ⏱️
  - API Error 🔴
- **Notifications** : Desktop + sons personnalisables
- **Webhooks** : Slack, Discord, Telegram, custom
- **Cross-platform** : macOS/Linux/Windows

## Analyse

### Points positifs
- Complément naturel au Second Brain (Mem0 + Obsidian)
- Notifications pour `/start`, `/end`, tâches longues
- Webhooks intégrables avec queue Mem0
- Architecture robuste (retry, circuit breaker, rate limiting)
- Mature (CI/CD, tests, doc complète)

### Préoccupations
- **Charge cognitive** déjà élevée (Mem0, Obsidian, Git, MCP, Bash)
- **Besoin réel ?** Travail généralement synchrone dans le terminal
- **Maintenance** : 6ème système à documenter et maintenir
- Complexité (binaires Go, config.json, hooks)

## Plan de test

**Phase 1 : Installation minimale (1 semaine)**
1. Installer plugin avec notifications desktop uniquement
2. Pas de webhooks (garder simple)
3. Observer usage réel sur workflows quotidiens
4. Noter cas d'usage où c'est vraiment utile

**Critères de décision**
- ✅ **Adopter** : si >3 fois/jour où notifications sont utiles
- ❌ **Rejeter** : si <1 fois/jour d'utilité réelle
- 🤔 **Adapter** : si utile seulement pour certains workflows

## Next steps

- [ ] Décider si on teste (installer en mode minimal)
- [ ] Ou prioriser simplification système existant (memory #2)
- [ ] Ou finir stabilisation Mem0 + SecondBrain (memory #5, #16)

## Liens

- GitHub: https://github.com/777genius/claude-notifications-go
- Installation: `/plugin marketplace add 777genius/claude-notifications-go`
- Mem0 memory saved: 2025-12-01
