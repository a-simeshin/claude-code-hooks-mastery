# Context7

Optional MCP integration for live documentation lookup. When configured, builder and validator agents query Context7 before implementation to get current API references instead of relying on training data.

## What It Does

Context7 resolves a library name to its documentation and returns relevant code examples for the specific API you're using. This means the builder works with current docs — not stale training data from months ago.

```
Builder task: "Add @ConfigurationProperties for payment gateway"
    ↓
Context7: resolve "spring-boot" → query "ConfigurationProperties binding"
    ↓
Returns: current Spring Boot 3.x docs with @ConfigurationProperties examples
    ↓
Builder writes code matching the actual current API
```

## Setup

Add Context7 MCP server to your Claude Code config:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

## How Agents Use It

When Context7 is available, agents have two tools:

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Find the Context7 ID for a library (e.g., "spring-boot" → `/spring-projects/spring-boot`) |
| `query-docs` | Get documentation for a specific topic from that library |

Agents check for Context7 availability before querying. If not configured, they fall back to `.claude/refs/*.md` and training data.

## Which Agents Use It

- **builder** — queries docs before implementing tasks
- **validator** — queries docs to verify implementation matches current API
- **plan-reviewer** — queries docs to validate pattern compliance

## Key Files

- `.claude/agents/team/builder.md` — builder agent with Context7 tools in frontmatter
- `.claude/agents/team/plan-reviewer.md` — plan-reviewer with Context7 tools
