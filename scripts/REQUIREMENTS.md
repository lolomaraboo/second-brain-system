# Memory Scripts - Requirements

## Python Version

**Required:** Python 3.9+

**Check your version:**
```bash
python3 --version
```

## Required Packages

```bash
pip install mem0ai requests openai
```

Or:
```bash
pip install -r requirements.txt
```

## System Requirements

- **Qdrant:** Running on localhost:6333
  - Container: `qdrant-secondbrain`
  - Check: `curl http://localhost:6333/collections/mem0`

- **OpenAI API Key:** Required for embeddings
  - Set in `~/.claude/.env`: `OPENAI_API_KEY=sk-...`
  - Or environment variable

## Scripts

### 1. reindex_missing_memories.py

**Purpose:** Re-index JSON memories to Qdrant (fixes gaps)

**Usage:**
```bash
/usr/bin/python3 scripts/reindex_missing_memories.py --help
```

**Dependencies:**
- `mem0` (Memory.from_config)
- `requests` (Qdrant API)
- `openai` (embeddings)

### 2. monitor_memory_gaps.py

**Purpose:** Detect JSON vs Qdrant divergence

**Usage:**
```bash
/usr/bin/python3 scripts/monitor_memory_gaps.py --help
```

**Dependencies:**
- `requests` (Qdrant scroll API)

## Troubleshooting

### "No module named 'mem0'"

**Solution:**
```bash
/usr/bin/python3 -m pip install mem0ai
```

### "Connection refused" (Qdrant)

**Check container:**
```bash
docker ps | grep qdrant
```

**Start if stopped:**
```bash
docker start qdrant-secondbrain
```

### "OpenAI API key not found"

**Add to ~/.claude/.env:**
```bash
echo "OPENAI_API_KEY=sk-your-key" >> ~/.claude/.env
```

### Wrong Python in venv

**Use system Python explicitly:**
```bash
/usr/bin/python3 script.py
```

**Or deactivate venv:**
```bash
deactivate
python3 script.py
```

## Development

### Installing in editable mode:

```bash
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain
pip install -e .
```

### Running tests:

```bash
python3 -m pytest tests/
```
