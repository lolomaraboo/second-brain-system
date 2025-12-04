# Memory Gap Monitoring

## Purpose

Prevents the "326 missing memories" problem by detecting when JSON files and Qdrant vectors diverge.

## Quick Start

```bash
# Check all projects
/usr/bin/python3 scripts/monitor_memory_gaps.py

# Check specific project
/usr/bin/python3 scripts/monitor_memory_gaps.py --project SecondBrain

# Only show if gaps exist (for automation)
/usr/bin/python3 scripts/monitor_memory_gaps.py --alert-only
```

## Automated Monitoring (Daily)

### Install launchd service:

```bash
cp scripts/com.mem0.gap-monitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mem0.gap-monitor.plist
```

### Check status:

```bash
launchctl list | grep mem0.gap-monitor
```

### View logs:

```bash
tail -f /tmp/mem0-gap-monitor.log
tail -f /tmp/mem0-gap-monitor-error.log
```

### Uninstall:

```bash
launchctl unload ~/Library/LaunchAgents/com.mem0.gap-monitor.plist
rm ~/Library/LaunchAgents/com.mem0.gap-monitor.plist
```

## Output Format

```
Memory Gap Monitor Report
==============================================
Timestamp: 2025-12-04 10:07:38
Qdrant: localhost:6333
==============================================

🚨 ALERTS: 3
⚠️  WARNINGS: 1
✅ OK: 1

Project              JSON     Qdrant   Status
--------------------------------------------------------------
SecondBrain          404      397      +7 vectors (1.7%)
yt-transcript        44       44       ✅ In sync
```

## Thresholds

- **Alert (🚨)**: Divergence > 5% (default)
- **Warning (⚠️)**: Divergence > 0% but < 5%
- **OK (✅)**: Perfect sync

Customize threshold:
```bash
/usr/bin/python3 scripts/monitor_memory_gaps.py --threshold 10
```

## Exit Codes

- `0`: All projects in sync
- `1`: Gaps or errors detected (triggers alert in automation)

## Integration with Re-indexing

If gaps are detected, run:
```bash
/usr/bin/python3 scripts/reindex_missing_memories.py -y
```

## Scheduling Options

| Frequency | StartInterval | When to Use |
|-----------|---------------|-------------|
| Daily | 86400 | Recommended (default) |
| Weekly | 604800 | Low-activity projects |
| Hourly | 3600 | High-activity projects |
| Every 6h | 21600 | Development phase |
