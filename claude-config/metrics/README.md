# Metrics System

## Overview
Système de tracking d'usage des agents pour analytics et optimisation.

## Files

### agent-usage.json
Tracking de l'utilisation de chaque agent personnalisé.

**Structure:**
```json
{
  "agents": {
    "agent-name": {
      "total_calls": number,
      "last_used": "ISO-8601 date",
      ... agent-specific metrics
    }
  },
  "summary": {
    "most_used_agent": "agent-name",
    "least_used_agent": "agent-name",
    "total_agent_calls": number
  }
}
```

**Update mechanism:**
- ✅ **Automatic:** Use `log-agent-usage.sh` script (implemented)
- Manual: Direct jq commands (advanced users)

## Logging Agent Usage

### Using log-agent-usage.sh

**Basic usage:**
```bash
# Log agent call
./core/bin/log-agent-usage.sh <agent-name> [mode] [metadata]
```

**Examples:**
```bash
# session-manager with mode
./core/bin/log-agent-usage.sh session-manager --full

# brutal-critic with score
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 7.3}'

# Simple agent call
./core/bin/log-agent-usage.sh setup-assistant

# Verbose output
VERBOSE=1 ./core/bin/log-agent-usage.sh gemini-researcher
```

**Supported agents:**
- `session-manager` (modes: --summary, --close, --full)
- `brutal-critic` (metadata: {"score": float})
- `gemini-researcher`
- `perplexity-researcher`
- `setup-assistant`

### Integration in Agents

Add to agent execution flow:
```bash
# In your agent or wrapper script
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 7.3}'
```

Or in Claude Code (when calling agent):
```bash
# After agent execution
bash -c './core/bin/log-agent-usage.sh session-manager --full'
```

## Usage

### View Current Stats
```bash
cat .claude/metrics/agent-usage.json | jq '.summary'
```

### Most Used Agent
```bash
cat .claude/metrics/agent-usage.json | jq -r '.summary.most_used_agent'
```

### Never Used Agents
```bash
cat .claude/metrics/agent-usage.json | jq -r '.summary.agents_never_used[]'
```

### Agent-Specific Stats
```bash
# session-manager usage
cat .claude/metrics/agent-usage.json | jq '.agents["session-manager"]'

# brutal-critic average score
cat .claude/metrics/agent-usage.json | jq '.agents["brutal-critic"].avg_score'
```

## Future Enhancements

### ~~Automatic Tracking~~ ✅ DONE
~~Implement automatic logging when agents are called~~ → Implemented via `log-agent-usage.sh`

### Analytics Dashboard
Create simple dashboard to visualize:
- Usage trends over time
- Most/least used agents
- Average scores (brutal-critic)
- Session patterns

### Integration with ccm
Merge agent metrics with ccm (Claude Code Monitor) for unified analytics.

### Alerts
- Notify if agent never used after 30 days (consider deprecation)
- Alert on abnormal usage patterns
- Weekly usage summary

## Notes
- Data stored in JSON for easy parsing and portability
- Retention: 365 days (configurable)
- Privacy: No sensitive data tracked, only usage patterns
- Location: `.claude/metrics/` (synchronized via APP_HOME)
