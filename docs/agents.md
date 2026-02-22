# Agents

Multi-agent team with specialized roles, each running on a cost-appropriate model.

## Team

| Agent | Model | Role | File |
|-------|-------|------|------|
| **builder** | Opus | Writes code for Java/React/Python with Context7 docs integration | `.claude/agents/team/builder.md` |
| **validator** | Sonnet | Read-only verification — runs checks, reads files, never modifies | `.claude/agents/team/validator.md` |
| **plan-reviewer** | Opus | Critic agent — reviews plans against [8 criteria](plan-review.md) before execution | `.claude/agents/team/plan-reviewer.md` |
| **monitor** | Haiku | Observes parallel sub-agents, reports status every 10 seconds | `.claude/agents/team/monitor.md` |
| **meta-agent** | — | Generates new agent configuration files from descriptions | `.claude/agents/meta-agent.md` |

## Builder

The builder is the primary coding agent. Its workflow:

1. **Detect stacks** — scans for `pom.xml`, `package.json`, `pyproject.toml`
2. **Load context** — uses [context routing](context-routing.md) to load only relevant ref sections
3. **Implement** — writes code following loaded patterns
4. **Auto-validate** — every Write/Edit triggers [validator dispatcher](validators.md)
5. **Fix on failure** — if validators fail, reads errors and fixes

Configured with PostToolUse hooks that run `validator_dispatcher.py` on every file write.

## Validator

Read-only agent (Write, Edit, NotebookEdit disabled). Runs on Sonnet instead of Opus — 80% cost savings for read-only checks that don't need deep reasoning.

Used for:
- Verifying acceptance criteria after build
- Running compilation and test commands
- Checking file structure and content

## Plan-Reviewer

Opus-powered critic that evaluates plans before execution. See [Plan Review](plan-review.md) for the full 8-criteria framework.

## Monitor

Lightweight Haiku agent that reports sub-agent progress during parallel execution. Works with [status line v10](status-line.md) for terminal visibility.

## Model Cost Strategy

| Model | Cost | Used For |
|-------|------|----------|
| Opus | $15/M tokens | Complex reasoning (builder, plan-reviewer) |
| Sonnet | $3/M tokens | Read-only verification (validator) |
| Haiku | $0.25/M tokens | Observation, monitoring (monitor) |
