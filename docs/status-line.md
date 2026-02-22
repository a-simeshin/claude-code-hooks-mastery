# Status Line (v10)

Real-time visibility into parallel sub-agents directly in the terminal — always visible, updates every 300ms, no extra cost.

## What It Looks Like

**Idle (no agents running):**
```
[Opus] [######---------] | 42.0% used | ~116k left | abc12345
```

**Agents running (multi-line):**
```
[Opus] [###-----] 42% | ▶2 ✓1
 ▶ builder         12s  Edit Service.java
 ▶ Explore         8s   Read App.tsx
```

## Dynamic Lifecycle

```
Step 1: agent starts     → ▶1  builder  0s  Read App.java
Step 2: second agent     → ▶2  builder Read App.java + Explore Write Cart.tsx
Step 3: action changes   → ▶2  builder Edit Service.java (updated!)
Step 4: agent finishes   → ▶1 ✓1  only running agents shown
Step 5: all done         → back to standard single-line format
```

## How It Works

- `status_line_v10.py` extends v6 (context window progress bar) with agent monitoring
- Reads `logs/subagent_start.json` + `logs/subagent_stop.json` to compute running/done agents
- Filters by current `session_id` — no phantom agents from old sessions
- For running agents, reads the last 64KB of transcript `.jsonl` to extract the current tool action
- `fcntl` file locking in hooks prevents race conditions when parallel agents write simultaneously
- Logs reset on session start — no infinite accumulation
- Filters out `monitor` and `context-router` agent types from display
- ~32ms per invocation (10x under the 300ms refresh limit)

## Other Status Line Versions

| Version | Feature |
|---------|---------|
| v1 | Basic model + session info |
| v2 | Token usage counters |
| v3 | Cost tracking (total_cost_usd) |
| v4 | Lines added/removed |
| v5 | Cost tracking with formatting |
| v6 | Context window progress bar |
| v7 | Session duration timer |
| v8 | Token usage with cache stats |
| v9 | Minimal powerline-style with Unicode |
| **v10** | **Context bar + real-time agent monitor** |

## Key Files

- `.claude/status_lines/status_line_v10.py` — active status line
- `.claude/hooks/subagent_start.py` — logs agent start events (with `fcntl` locking)
- `.claude/hooks/subagent_stop.py` — logs agent stop events (with `fcntl` locking)
- `.claude/hooks/session_start.py` — resets logs on new session
