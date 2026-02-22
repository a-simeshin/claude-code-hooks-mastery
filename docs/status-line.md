# Status Line (v10)

Context window progress bar in the terminal — always visible.

## What It Looks Like

```
[Opus] # [######---------] | 42.0% used | ~116k left | abc12345
```

## How It Works

- `status_line_v10.py` shows model name, context window usage progress bar, remaining tokens, and session ID
- Color-coded: green (<50%), yellow (<75%), red (<90%), bright red (90%+)
- ~5ms per invocation

## Key Files

- `.claude/status_lines/status_line_v10.py` — active status line
