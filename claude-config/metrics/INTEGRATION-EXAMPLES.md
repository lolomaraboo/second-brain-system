# Integration Examples - Agent Metrics Tracking

## Overview
Exemples d'intégration du tracking métrique dans différents workflows.

## Example 1: Manual Logging (Simple)

Après avoir utilisé un agent manuellement:

```bash
# Utilisé brutal-critic
@brutal-critic analyse ce code

# Log manuel après
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 7.5}'
```

## Example 2: Wrapper Script

Créer un wrapper qui log automatiquement:

```bash
#!/bin/bash
# brutal-critic-wrapper.sh

# Execute agent (simulé ici)
echo "Running brutal-critic..."
# ... agent execution ...

# Log usage with score
SCORE=7.5
./core/bin/log-agent-usage.sh brutal-critic "" "{\"score\": $SCORE}"

echo "✓ Metrics logged"
```

## Example 3: Session Manager Integration

Intégrer dans session-manager:

```markdown
# Dans session-manager.md

## Post-Execution Hook

Après chaque exécution de session-manager, logger l'usage:

\`\`\`bash
# Déterminer le mode utilisé
MODE="--full"  # ou --summary, --close

# Log metrics
bash -c "./core/bin/log-agent-usage.sh session-manager $MODE"
\`\`\`
```

## Example 4: Claude Code Hook

Créer un hook qui log automatiquement tous les appels agents:

```bash
# .claude/hooks/post-agent-call.sh (fictif, à implémenter)
#!/bin/bash

AGENT_NAME="$1"
MODE="$2"

# Log all agent calls
./core/bin/log-agent-usage.sh "$AGENT_NAME" "$MODE"
```

## Example 5: Batch Logging

Logger plusieurs appels d'un coup:

```bash
#!/bin/bash
# batch-log-session.sh

# Session du 2025-11-05
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 5.7}'
./core/bin/log-agent-usage.sh session-manager --full
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 7.3}'
./core/bin/log-agent-usage.sh setup-assistant

echo "✓ Session logged"
```

## Example 6: View Metrics After Work

Workflow quotidien:

```bash
# Matin: Check metrics
cat .claude/metrics/agent-usage.json | jq '.summary'

# Travail: Utiliser agents...
@brutal-critic ...
@session-manager --full

# Soir: View updated metrics
cat .claude/metrics/agent-usage.json | jq '.summary'

# Weekly: Full report
cat .claude/metrics/agent-usage.json | jq '{
  total_calls: .summary.total_agent_calls,
  most_used: .summary.most_used_agent,
  agents: .agents | to_entries | map({
    name: .key,
    calls: .value.total_calls,
    last_used: .value.last_used
  })
}'
```

## Example 7: Error Handling

Gestion d'erreurs robuste:

```bash
#!/bin/bash
# safe-log-agent.sh

AGENT="$1"
MODE="$2"
METADATA="$3"

# Try to log, but don't fail if it errors
if ./core/bin/log-agent-usage.sh "$AGENT" "$MODE" "$METADATA" 2>/dev/null; then
    echo "✓ Metrics logged"
else
    echo "⚠ Metrics logging failed (non-fatal)" >&2
fi
```

## Example 8: Metrics Dashboard (Simple)

Script bash simple pour dashboard:

```bash
#!/bin/bash
# metrics-dashboard.sh

echo "📊 Agent Metrics Dashboard"
echo "=========================="
echo ""

echo "Total Calls: $(jq -r '.summary.total_agent_calls' .claude/metrics/agent-usage.json)"
echo "Most Used: $(jq -r '.summary.most_used_agent' .claude/metrics/agent-usage.json)"
echo "Least Used: $(jq -r '.summary.least_used_agent' .claude/metrics/agent-usage.json)"
echo ""

echo "Individual Agents:"
jq -r '.agents | to_entries[] | "  \(.key): \(.value.total_calls) calls"' .claude/metrics/agent-usage.json

echo ""
echo "Never Used:"
jq -r '.summary.agents_never_used[]' .claude/metrics/agent-usage.json | sed 's/^/  - /'
```

## Example 9: Integration with Task Tracking

Combiner avec TodoWrite:

```bash
# Après complétion d'une tâche utilisant brutal-critic
./core/bin/log-agent-usage.sh brutal-critic "" '{"score": 8.5}'

# Update todo
echo "Task completed with score 8.5"
```

## Example 10: Automated Weekly Report

Cron job pour rapport hebdomadaire:

```bash
#!/bin/bash
# weekly-metrics-report.sh

REPORT_FILE="session-summaries/metrics-$(date +%Y-%m-%d).txt"

{
  echo "Weekly Metrics Report - $(date)"
  echo "================================"
  echo ""

  cat .claude/metrics/agent-usage.json | jq '
    {
      period: "Weekly",
      total_calls: .summary.total_agent_calls,
      most_used: .summary.most_used_agent,
      least_used: .summary.least_used_agent,
      never_used_count: (.summary.agents_never_used | length),
      agents: .agents | to_entries | map({
        name: .key,
        calls: .value.total_calls
      }) | sort_by(.calls) | reverse
    }
  '
} > "$REPORT_FILE"

echo "✓ Report saved to $REPORT_FILE"
```

## Best Practices

1. **Log after execution** - Toujours logger après l'agent, pas avant
2. **Include metadata** - Score pour brutal-critic, mode pour session-manager
3. **Handle errors gracefully** - Metrics logging ne doit pas bloquer workflow
4. **Review regularly** - Check metrics hebdo pour détecter agents inutilisés
5. **Backup metrics** - `.bak` créé automatiquement par le script

## Troubleshooting

### "jq: command not found"
```bash
brew install jq
```

### "Metrics file not found"
```bash
# Vérifier path
ls -la ~/.claude/metrics/agent-usage.json

# Si manquant, le fichier a été créé dans APP_HOME/.claude/metrics/
# Créer symlink si nécessaire
```

### "Permission denied"
```bash
chmod +x ./core/bin/log-agent-usage.sh
```

---

**Next:** Implement full automation via hooks or agent modifications.
