# Claude Code Hooks Mastery

> **Fork Notice:** This is a personal fork of [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) tailored for **Java** and **Java + React** projects.

## What's Different in This Fork

### Validators (PostToolUse hooks)

| Stack | Tools |
|-------|-------|
| **Java** | Spotless (Palantir), Maven compile, JaCoCo 80%, PMD, OSS Index |
| **React/TS** | ESLint, TypeScript compiler, Prettier |
| **Python** | Ruff, Ty, Bandit |

### References (`.claude/refs/`)

| File | Content |
|------|---------|
| `java-patterns.md` | Java 17/21 coding standards, Spring Boot patterns |
| `java-testing.md` | Testcontainers, Podman, Allure, Selenide E2E, JaCoCo |

### Agents (`.claude/agents/team/`)

| Agent | Model | Purpose |
|-------|-------|---------|
| `builder.md` | Opus | Universal builder for Java/React/Python with Context7 integration |
| `validator.md` | Opus | Read-only validation agent |
| `monitor.md` | Haiku | Lightweight sub-agent observer — reports parallel agent progress every 10s |

### Monitor Agent

When running parallel sub-agents via `/build`, the **monitor agent** provides real-time visibility into what each agent is doing. It runs on **Haiku** (minimal cost) and reports every 10 seconds:

```
━━━ Agent Monitor [12:05:30] ━━━
Tasks: 2/7 done | Agents: 2 running, 1 done

▶ builder (45s)
  Last 10s: Write CartController.java, Edit SecurityConfig.java
  Now: Bash: mvn compile

▶ builder (32s)
  Last 10s: Write CartContext.tsx
  Now: Edit App.tsx

✓ builder (18s) → Created CheckoutPage.tsx placeholder

Tasks:
  ✓ #1 Backend Cart Foundation
  ▶ #2 Frontend Cart API
  ◻ #3 MaterialPage Buttons (blocked by #2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**How it works:**
- `monitor_check.py` parses `subagent_start/stop` hook logs and reads agent transcripts incrementally (byte offsets)
- Extracts tool calls (Write, Edit, Read, Bash) from new JSONL transcript entries
- Monitor agent formats the data and calls `TaskList` for task progress
- Exits automatically when all observed agents are done

**Usage in orchestrator:**
```python
Task(builder-backend, run_in_background: true)
Task(builder-frontend, run_in_background: true)
Task(monitor, model: haiku, run_in_background: false)  # foreground — writes to chat
```

### Semantic Context Routing

Instead of loading all refs or creating multiple agents, this fork uses **dynamic section loading**:

```mermaid
flowchart LR
    A[Task] --> B[Context Router]
    B --> C{Semantic Analysis}
    C --> D["sections: [basics, errors, http]"]
    D --> E[Section Loader]
    E --> F[Focused Context<br/>~5k tokens]
    F --> G[Builder]
    G --> H[Validators]
    H -->|Fail| G
    H -->|Pass| I[Done]
```

**How it works:**
1. `context_router.py` analyzes task semantically
2. Returns only required section names
3. `section_loader.py` extracts marked sections from refs
4. Builder gets focused context instead of full files

### Real Example: Token Savings

**Task:** `"Add GET /api/tutors/{id} endpoint with 404 handling and integration test"`

| Approach | What's Loaded | Tokens |
|----------|---------------|--------|
| **Full refs** | java-patterns.md + java-testing.md | ~20,000 |
| **Semantic routing** | basics + errors + structure + http | ~5,847 |
| **Savings** | | **71%** |

```bash
# Router output
{
  "sections": ["java-patterns#basics", "java-patterns#errors",
               "java-testing#structure", "java-testing#integration"],
  "reasoning": "'endpoint' → basics; '404' → errors; 'test' → structure..."
}
```

### Available Sections

**java-patterns.md:**
| Section | Content |
|---------|---------|
| `basics` | No-nest, fail-fast, final, Lombok, comments |
| `errors` | @ControllerAdvice, exceptions, 404/400/409 |
| `java17` | Records, pattern matching, switch expressions |
| `java21` | Virtual threads, sequenced collections |

**java-testing.md:**
| Section | Content |
|---------|---------|
| `structure` | Naming, given-when-then, AssertJ, Allure |
| `integration` | Testcontainers, Podman, base test class |
| `http` | REST tests, MockMvc, TestRestTemplate |
| `kafka` | Kafka consumer/producer tests |
| `jdbc` | Repository tests, transactions |
| `mockito` | Unit tests, mocks, edge cases |
| `e2e` | Selenide, browser tests, page objects |
| `maven` | Surefire, Failsafe, JaCoCo config |

### Comparison with Other Approaches

| Approach | Tokens | Agents | Flexibility |
|----------|--------|--------|-------------|
| Universal (load all) | 22,500 | 1 | Low |
| Specialized (3 agents) | 7,500-15,500 | 3 | Medium |
| **Semantic routing** | **~5,000** | **1** | **High** |

**Key Differences:**

| Aspect | Default Claude | This Fork |
|--------|----------------|-----------|
| **Context loading** | Reactive exploration | Semantic pre-routing |
| **Standards** | Agent's training data | Your `.claude/refs/*.md` |
| **Granularity** | Full files | Marked sections |
| **Validation** | Manual review | Auto-validators |

## Quick Start

Run in your project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/install.sh | bash
```

This installs `.claude/` with refs, agents, and validators. Start Claude Code to use them.

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/uninstall.sh | bash
```

## Validators Auto-Trigger by File Extension

| Extension | Validators |
|-----------|------------|
| `.java` | spotless, maven_compile |
| `.ts`, `.tsx` | eslint, tsc |
| `.js`, `.jsx` | eslint, prettier |
| `.py` | ruff, ty, bandit |

## Prerequisites

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — Anthropic's CLI for Claude AI
- **[Astral UV](https://docs.astral.sh/uv/)** — Auto-installed by installer (or `brew install uv`)

## Original Documentation

- [Original repository](https://github.com/disler/claude-code-hooks-mastery) by [@disler](https://github.com/disler)
