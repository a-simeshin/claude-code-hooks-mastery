# Install / Uninstall

One-line installer that copies the `.claude/` directory into your project.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/install.sh | bash
```

Interactive prompts:
1. **Status line variant** — choose from 3 options (usage bar, powerline, cost tracking)
2. **TTS** — enable/disable text-to-speech notifications

## Non-Interactive Install

For CI pipelines or Claude Code automation:

```bash
bash install.sh --force
```

With custom options:

```bash
STATUS_LINE_CHOICE=2 TTS_ENABLED=y bash install.sh --force
```

| Variable | Values | Default |
|----------|--------|---------|
| `STATUS_LINE_CHOICE` | `1` (usage bar), `2` (powerline), `3` (cost tracking) | `1` |
| `TTS_ENABLED` | `y` / `n` | `n` |

## What Gets Installed

```
.claude/
├── commands/          — slash commands (plan_w_team, smart_build, etc.)
├── agents/team/       — agent definitions (builder, validator, plan-reviewer)
├── hooks/             — context router, section loader, validators
├── refs/              — coding standards (Java, React, Python)
├── settings.json      — hook configuration
├── status_lines/      — status line scripts
└── CLAUDE.md          — project instructions
```

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/uninstall.sh | bash
```

Removes the `.claude/` directory and all installed files.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — CLI tool
- [Astral UV](https://docs.astral.sh/uv/) — auto-installed by the script if missing

## Optional Dependencies

| Tool | What for | Install |
|------|----------|---------|
| [Context7](context7.md) | Live documentation lookup | Add MCP server to config |
| [Serena](serena.md) | Semantic code navigation | Add MCP server to config |
| [OpenSpec](openspec.md) | Living specs & delta tracking | `npm i -g @fission-ai/openspec && openspec init --tools claude` |
