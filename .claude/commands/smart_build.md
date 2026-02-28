---
allowed-tools: Task, Read, Bash, Write, Edit, Glob, Grep
description: Smart builder with semantic context routing - loads only relevant sections
argument-hint: [task description]
---

# Smart Build

Build with **semantic context routing** - loads only the sections you need.

## Workflow

### Step 0: Load Plan (if argument is a plan file)

If `$ARGUMENTS` ends with `.md` and the file exists in `specs/`, this is a **plan execution** request. The plan has already been reviewed by plan-reviewer during `/plan_w_team`. Read the plan and execute tasks directly (skip Steps 1-3 for context routing — use the plan's Stack keywords instead).

**OpenSpec tracking init:** At the start of plan execution, check if an OpenSpec change exists:
```bash
openspec list --changes --json 2>/dev/null
```
Look for a change matching the plan filename (kebab-case). If found, note the change name — you will update its `tasks.md` incrementally as builders complete tasks (see Step 4).

### Step 1: Route Task to Sections

Run the deterministic context router (keyword matching, zero LLM cost).

When executing a plan, prepend the task's `**Stack**` field to the task description for accurate routing:

```bash
# Direct task — use as-is
echo '$ARGUMENTS' | uv run --script .claude/hooks/context_router.py

# Plan task — prepend Stack keywords for reliable routing
echo 'Stack: Java Spring Boot JPA. Task: Add @ConfigurationProperties for payment gateway' | \
  uv run --script .claude/hooks/context_router.py
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
echo '$ARGUMENTS' | uv run --script .claude/hooks/context_router.py | \
  uv run --script .claude/hooks/section_loader.py
```

Or in two steps if you need to inspect the routing:
```bash
ROUTE=$(echo '$ARGUMENTS' | uv run --script .claude/hooks/context_router.py)
echo "$ROUTE"  # inspect routing decision
echo "$ROUTE" | uv run --script .claude/hooks/section_loader.py
```

### Step 3: Execute with Focused Context

Now you have only the relevant reference sections loaded.

Use this context to implement the task following the patterns.

### Step 4: Track OpenSpec Progress (if available)

This step runs **incrementally throughout plan execution**, not as a batch at the end.

**After each builder completes a task:**
1. Find the matching task in `openspec/changes/<change-name>/tasks.md` by task name or description
2. Mark its checkbox as `[x]` immediately using Edit tool
3. This enables real-time progress tracking via `openspec view`

**After ALL tasks are complete — final report:**
```
OpenSpec Change Updated: openspec/changes/<change-name>/tasks.md
Completed: X/Y tasks

Next steps:
- Run `/opsx:verify` to validate implementation against specs
- Run `/opsx:archive` to finalize and merge delta specs
```

If no OpenSpec change was found in Step 0, skip this step silently.

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
