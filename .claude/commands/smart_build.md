---
allowed-tools: Task, Read, Bash, Write, Edit, Glob, Grep
description: Smart builder with semantic context routing - loads only relevant sections
argument-hint: [task description]
---

# Smart Build

Build with **semantic context routing** - loads only the sections you need.

## Workflow

### Step 0: Plan Review (if argument is a plan file)

If `$ARGUMENTS` ends with `.md` and the file exists in `specs/`, this is a **plan execution** request. Run validation before building:

**Structural check:**
```bash
uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_plan.py --file $ARGUMENTS --team-dir $CLAUDE_PROJECT_DIR/.claude/agents/team
```

**Content review** (spawn plan-reviewer agent):
```
Task({
  subagent_type: "plan-reviewer",
  description: "Review plan before execution",
  prompt: "Review the plan at $ARGUMENTS. Check all 8 criteria and return a structured verdict."
})
```

- If structural check fails or review verdict is **FAIL** — show issues and ask user to fix, continue, or abort.
- If both pass — read and execute the plan directly (skip Steps 1-3).

### Step 1: Route Task to Sections

Run the deterministic context router (keyword matching, zero LLM cost).

When executing a plan, prepend the task's `**Stack**` field to the task description for accurate routing:

```bash
# Direct task — use as-is
echo '$ARGUMENTS' | uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/context_router.py

# Plan task — prepend Stack keywords for reliable routing
echo 'Stack: Java Spring Boot JPA. Task: Add @ConfigurationProperties for payment gateway' | \
  uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/context_router.py
```

The router returns JSON like:
```json
{
  "sections": ["java-patterns#basics", "java-testing#integration"],
  "reasoning": "Matched: java, endpoint, error"
}
```

### Step 2: Load Sections

Pipe the router output to the section loader:

```bash
echo '$ARGUMENTS' | uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/context_router.py | \
  uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/section_loader.py
```

Or in two steps if you need to inspect the routing:
```bash
ROUTE=$(echo '$ARGUMENTS' | uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/context_router.py)
echo "$ROUTE"  # inspect routing decision
echo "$ROUTE" | uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/section_loader.py
```

### Step 3: Execute with Focused Context

Now you have only the relevant reference sections loaded.

Use this context to implement the task following the patterns.

## Example

**Task:** "Добавь endpoint /users с тестами"

1. Router returns:
   ```json
   {
     "sections": ["java-patterns#basics", "java-patterns#errors", "java-testing#structure", "java-testing#http"],
     "reasoning": "REST endpoint needs code standards, error handling, and HTTP test patterns"
   }
   ```

2. Loader provides ~8k tokens instead of ~20k

3. You implement with focused, relevant patterns only

## Token Savings

| Approach | Tokens |
|----------|--------|
| Universal (all refs) | ~20,000 |
| Smart routing (avg) | ~5,000 |
| **Savings** | **75%** |
