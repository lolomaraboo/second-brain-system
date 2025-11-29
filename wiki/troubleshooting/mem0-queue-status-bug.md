# Bug: mem0_queue_status KeyError 'total_queued'

## Symptôme
`mem0_queue_status` retourne l'erreur: `Error executing mem0_queue_status: 'total_queued'`

## Cause
La fonction `get_queue_status()` dans `mem0_mcp_server.py` ne retournait pas la clé `total_queued`, mais le code de formatage (ligne 438) essayait de l'utiliser.

## Solution
Ajout de la ligne manquante dans le dictionnaire retourné par `get_queue_status()`:
```python
"total_queued": queue["stats"].get("total_queued", 0),
```

## Fichier modifié
`~/scripts/mem0_mcp_server.py:134`

## Note
Nécessite redémarrage de Claude Code pour que le serveur MCP recharge le code.

## Date
2025-11-29

## Lien
[[mem0-solution-2a]]
