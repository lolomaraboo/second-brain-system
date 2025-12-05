# Installation Second Brain

Guide pour installer votre propre instance de Second Brain (système de mémoire Mem0+Qdrant pour Claude Code).

---

## Prérequis

- **Python 3.9+**
- **Docker** (pour Qdrant)
- **Claude Code** installé
- **OpenAI API Key** (pour embeddings)

---

## Installation Automatique (Recommandé)

### Script d'installation en 1 commande

```bash
git clone https://github.com/lolomaraboo/second-brain-system.git SecondBrain
cd SecondBrain
./install.sh
```

Le script installe automatiquement :
- ✅ Qdrant (Docker)
- ✅ Packages Python (mem0ai, requests, openai, watchdog)
- ✅ MCP Server configuration
- ✅ Claude Code slash commands et hooks
- ✅ Structure de mémoires
- ✅ **Phase 2:** Filesystem watcher + auto-documentation

**Seule chose à fournir :** Clé API OpenAI (obtenir sur [platform.openai.com/api-keys](https://platform.openai.com/api-keys))

**Durée :** ~2-3 minutes

---

## Installation Manuelle (Alternative)

Si vous préférez installer manuellement :

### 1. Cloner le repo

```bash
git clone https://github.com/lolomaraboo/second-brain-system.git SecondBrain
cd SecondBrain
```

### 2. Installer Qdrant (vecteur store)

```bash
docker run -d \
  --name qdrant-secondbrain \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

**Vérifier :**
```bash
curl http://localhost:6333
# Doit retourner: {"title":"qdrant - vector search engine",...}
```

### 3. Configurer l'API OpenAI

```bash
mkdir -p ~/.claude
echo "OPENAI_API_KEY=sk-your-key-here" >> ~/.claude/.env
```

⚠️ **Important :** Remplace `sk-your-key-here` par ta vraie clé API

### 4. Installer les packages Python

```bash
pip install mem0ai requests openai watchdog
```

### 5. Configurer le MCP Server Mem0

```bash
# Copier le script MCP server dans ~/scripts/
cp ~/path/to/mem0_mcp_server_local.py ~/scripts/

# Le rendre exécutable
chmod +x ~/scripts/mem0_mcp_server_local.py
```

**Ajouter dans ta config MCP** (`~/.claude/mcp.json` ou équivalent) :
```json
{
  "mcpServers": {
    "mem0": {
      "command": "/usr/bin/python3",
      "args": ["/Users/ton-username/scripts/mem0_mcp_server_local.py"]
    }
  }
}
```

### 6. Synchroniser la configuration Claude

```bash
# Copier les commandes et hooks dans ta config Claude
./scripts/sync-to-claude.sh
```

Ou manuellement :
```bash
mkdir -p ~/.claude/commands ~/.claude/hooks

# Copier les slash commands
cp claude-config/commands/*.md ~/.claude/commands/

# Copier les hooks
cp claude-config/hooks/*.md ~/.claude/hooks/

# Copier CLAUDE.md (instructions globales)
cp claude-config/CLAUDE.md ~/.claude/
```

---

## Configuration des Projets

### Option A : Structure recommandée (hiérarchique)

```bash
# Créer la structure de mémoires
mkdir -p ~/Memories/memories/{dev,perso,studio}

# Exemple de projets
mkdir -p ~/Memories/memories/dev/mon-projet
mkdir -p ~/Memories/memories/perso/notes
```

### Option B : Structure plate (simple)

```bash
mkdir -p ~/Memories/memories/mon-projet
```

---

## Premier Test

### 1. Tester Mem0

```bash
cd ~/Memories/memories
mkdir -p test-project

# Lancer Claude Code dans ce dossier
# Puis dans Claude Code :
/start test-project
```

### 2. Créer ta première mémoire

Dans Claude Code :
```
Mémorise que ce projet de test fonctionne correctement.
```

### 3. Rechercher la mémoire

```
Cherche dans la mémoire "projet test"
```

Si tu vois ta mémoire, c'est bon ! ✅

---

## Monitoring Automatique (Optionnel mais recommandé)

### Installer le monitoring quotidien

```bash
# Copier le plist
cp scripts/com.mem0.gap-monitor.plist ~/Library/LaunchAgents/

# Éditer pour ajuster les paths (remplace marabook_m1 par ton username)
nano ~/Library/LaunchAgents/com.mem0.gap-monitor.plist

# Charger le service
launchctl load ~/Library/LaunchAgents/com.mem0.gap-monitor.plist
```

### Test manuel du monitoring

```bash
/usr/bin/python3 scripts/monitor_memory_gaps.py
```

---

## Nettoyage (NE PAS partager les mémoires)

### Supprimer les mémoires de l'ancien propriétaire

```bash
# ATTENTION : Ceci supprime toutes les mémoires existantes
rm -rf ~/Memories/memories/*
rm -rf qdrant_storage/*

# Redémarrer Qdrant pour réinitialiser
docker restart qdrant-secondbrain
```

### Vérifier que c'est vide

```bash
curl http://localhost:6333/collections/mem0
# Doit retourner une erreur (collection n'existe pas)
```

La collection `mem0` sera créée automatiquement lors de ta première sauvegarde.

---

## Structure des Fichiers (après installation)

```
~/
├── .claude/
│   ├── .env (OPENAI_API_KEY)
│   ├── CLAUDE.md (instructions globales)
│   ├── commands/
│   │   ├── start.md
│   │   └── end.md
│   └── mcp.json (config MCP servers)
├── scripts/
│   └── mem0_mcp_server_local.py
└── Memories/
    └── memories/
        └── [tes-projets]/
            └── [fichiers-json-mémoires]

SecondBrain/ (repo git)
├── scripts/
│   ├── monitor_memory_gaps.py
│   ├── reindex_missing_memories.py
│   ├── MONITORING.md
│   └── REQUIREMENTS.md
├── claude-config/ (à copier dans ~/.claude/)
└── qdrant_storage/ (données Qdrant locales)
```

---

## Troubleshooting

### "No module named 'mem0'"

```bash
/usr/bin/python3 -m pip install mem0ai
```

### "Connection refused" (Qdrant)

```bash
docker ps | grep qdrant
# Si absent :
docker start qdrant-secondbrain
```

### "OpenAI API key not found"

```bash
# Vérifier que la clé existe
cat ~/.claude/.env | grep OPENAI_API_KEY

# Sinon, l'ajouter
echo "OPENAI_API_KEY=sk-your-key" >> ~/.claude/.env
```

### Qdrant storage permissions

```bash
# Donner les permissions
chmod -R 755 qdrant_storage/
```

---

## Utilisation au Quotidien

### Commandes principales

```bash
/start                 # Charge le contexte du projet actuel
/start mon-projet      # Charge un projet spécifique
/end                   # Sauvegarde le contexte
```

### Mémorisation automatique

Claude mémorise automatiquement après :
- Décisions techniques importantes
- Bugs résolus
- Configurations créées
- Commits importants

### Recherche sémantique

```
Cherche dans la mémoire "comment configurer X"
```

---

## Mise à Jour

```bash
cd SecondBrain
git pull
./scripts/sync-to-claude.sh
```

---

## Support

- **Documentation complète :** `docs/reviews/`
- **Guide monitoring :** `scripts/MONITORING.md`
- **Requirements :** `scripts/REQUIREMENTS.md`
- **Issues :** https://github.com/lolomaraboo/second-brain-system/issues

---

## Architecture

**Mémoire :** Mem0 (pour sauvegardes JSON) + Qdrant (pour recherche sémantique)
**LLM :** OpenAI GPT-4o-mini
**Embeddings :** text-embedding-3-small (1536 dimensions)
**Storage :** Local (pas de VPS, pas de cloud)

**Coût :** ~$0.002 pour 1000 mémoires (embeddings)

---

## Phase 2 - Auto-Documentation (2025-12-04)

### Qu'est-ce que Phase 2 ?

Phase 2 ajoute l'**auto-documentation intelligente** via GPT-4o-mini :

1. **Pattern Detection Automatique**
   - Chaque `mem0_save` est analysé par GPT-4o-mini
   - Détecte 6 types de patterns : Bug résolu, Décision technique, Config/Secret, Nouveau tool, Pattern réutilisable, Migration
   - Si confidence > 0.7 → Suggestion automatique avec draft pré-généré

2. **Filesystem Watcher**
   - Service macOS 24/7 (LaunchAgent)
   - Surveille `Memories/vault/` pour changements .md
   - Re-indexe automatiquement Qdrant après chaque modification (debounce 2s)

### Installation Phase 2

**Automatique (via install.sh) :**
Le script install.sh installe automatiquement Phase 2 si tu utilises la dernière version.

**Manuel :**

```bash
# 1. Installer watchdog
pip install watchdog

# 2. Copier le watcher script
cp scripts/obsidian_vault_watcher.py ~/path/to/SecondBrain/scripts/

# 3. Créer le LaunchAgent
cat > ~/Library/LaunchAgents/com.secondbrain.obsidian-watcher.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.secondbrain.obsidian-watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/TON-USERNAME/path/to/SecondBrain/scripts/obsidian_vault_watcher.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/Users/TON-USERNAME/path/to/SecondBrain/logs/obsidian-watcher.error.log</string>
</dict>
</plist>
EOF

# 4. Charger le service
launchctl load ~/Library/LaunchAgents/com.secondbrain.obsidian-watcher.plist
```

### Vérifier Phase 2

```bash
# Vérifier que le watcher tourne
launchctl list | grep obsidian-watcher

# Voir les logs
tail -f SecondBrain/logs/obsidian-watcher.error.log

# Tester la détection de patterns
# Dans Claude Code, fais un mem0_save avec un bug résolu
# Tu devrais voir une suggestion automatique avec confidence score
```

### Coût Phase 2

- **GPT-4o-mini analysis :** ~$0.000075 par mem0_save
- **100 mem0_save/jour :** ~$0.0075/jour = **$0.58/mois**
- **Total (embeddings + Phase 2) :** ~$1/mois pour usage actif

### Patterns Détectés

| Pattern | Mots-clés | Obsidian Path Suggéré |
|---------|-----------|----------------------|
| Bug résolu | "bug", "fix", "résolu", "solution" | `wiki/troubleshooting/bug-name.md` |
| Décision technique | "décision", "choix", "opté pour" | `projects/[projet]/decisions/decision.md` |
| Config/Secret | "config", "ENV", "variable", "secret" | `wiki/secrets/service.md` |
| Nouveau tool | "script créé", "outil", "helper" | `wiki/tools/tool-name.md` |
| Pattern réutilisable | "workaround", "astuce", "pattern" | `wiki/patterns/pattern-name.md` |
| Migration | "migration", "refactoring", "breaking change" | `projects/[projet]/architecture.md` |

---

**Bon usage de ton Second Brain !** 🧠
