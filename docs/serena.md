# Serena

Optional MCP integration for semantic code navigation via Language Server Protocol. When configured, agents use symbol-level tools instead of Glob/Grep for faster and more precise code exploration.

## What It Does

Serena connects to your project's language server and provides semantic understanding of the codebase — not just text search, but actual symbol resolution, type hierarchy, and reference tracking.

```
Glob/Grep approach:     search "UserService" → 47 matches across comments, imports, strings
Serena approach:         find_symbol "UserService" → class definition + 12 methods + 8 references
```

## Setup

Add Serena MCP server to your Claude Code config. See [Serena docs](https://github.com/oraios/serena) for language-specific setup.

## Tools

| Tool | Purpose |
|------|---------|
| `find_symbol` | Find a symbol by name path (e.g., `UserService/findById`) |
| `get_symbols_overview` | List all symbols in a file — classes, methods, fields |
| `find_referencing_symbols` | Find all code that references a symbol |
| `find_referencing_code_snippets` | Get code snippets around references |
| `search_for_pattern` | Regex search when symbol name is unknown |
| `write_memory` / `read_memory` | Persist knowledge across sessions |

## How Agents Use It

**Planning** (`/plan_w_team`):
- Steps 1, 4: Use `find_symbol` and `get_symbols_overview` instead of Glob/Grep to understand architecture
- Step 15: `write_memory` saves architectural decisions and patterns chosen for future sessions
- Step 1: `read_memory` loads past decisions to inform new plans

**Building** (`/smart_build`):
- Builder and validator agents use symbol navigation for precise code modifications
- `find_referencing_symbols` ensures changes are backward-compatible

**Fallback**: If Serena is not configured, all agents fall back to Glob/Grep/Read — no functionality is lost, only precision and speed.

## Key Files

- `.claude/commands/plan_w_team.md` — Serena integration in Steps 1, 4, 15
- `.claude/agents/team/builder.md` — builder agent with Serena tools
- `.claude/agents/team/plan-reviewer.md` — plan-reviewer with Serena tools
