# Status Line

We recommend [claude-hud](https://github.com/jarrodwatts/claude-hud) — a full-featured HUD plugin for Claude Code.

## Install

```
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud
/claude-hud:setup
```

## What It Shows

- **Context window** — usage bar with autocompact awareness, remaining tokens
- **Usage rate limits** — 5-hour and 7-day quota with time-to-reset
- **Tool activity** — running and completed tools with file targets
- **Subagent tracking** — agent type, model, description, elapsed time
- **Todo progress** — current task and completion count
- **Git status** — branch, dirty state, ahead/behind, file stats
- **Environment** — CLAUDE.md count, MCP servers, hooks
- **Output speed** — tokens per second
- **Session duration** — elapsed time

## Configure

```
/claude-hud:configure
```

Choose layout (compact/expanded), toggle elements, customize colors. Config stored at `~/.claude/plugins/claude-hud/config.json`.
