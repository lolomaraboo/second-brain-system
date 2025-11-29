# API Mem0 - Timeouts répétés

## Problème

**Date :** 2025-11-29
**Symptôme :** `HTTPConnectionPool(host='31.220.104.244', port=8081): Read timed out. (read timeout=30)`

## Contexte

API Mem0 hébergée sur IP VPS : `http://31.220.104.244:8081`

**Fréquence des timeouts observée :**
- Session du 29 nov : 5/8 tentatives de sauvegarde ont timeout
- Taux d'échec : ~62%

## Impact

- ❌ Mémoire de travail non sauvegardée (perte de contexte)
- ✅ Fallback : Knowledge graph (`mcp__memory__`) fonctionne
- ✅ Fallback : Obsidian (documentation manuelle)

## Cause probable

Issue critique #2 identifiée par brutal-critic :
- IP sans failover
- Pas de SLA
- Pas d'authentification visible
- Single point of failure

## Solutions possibles

### Court terme
1. Augmenter timeout de 30s à 60s
2. Retry logic avec backoff exponentiel
3. Fallback automatique vers knowledge graph

### Long terme
1. Auto-hébergement Mem0 en local
2. Migration vers solution cloud avec SLA (Pinecone, Weaviate)
3. Utiliser uniquement knowledge graph + Obsidian

## Workaround actuel

Utiliser `mcp__memory__add_observations` au lieu de `mcp__mem0__mem0_save` :
```javascript
// Au lieu de
mcp__mem0__mem0_save(project_id, content)

// Utiliser
mcp__memory__add_observations({
  entityName: "ProjectName",
  contents: ["observation 1", "observation 2"]
})
```

## Validation

Cette issue CONFIRME le diagnostic de brutal-critic : l'API Mem0 est effectivement fragile et pose un risque pour la fiabilité du système.

## Action recommandée

Planifier migration vers solution plus stable ou accepter Obsidian + knowledge graph comme seule source de vérité.
