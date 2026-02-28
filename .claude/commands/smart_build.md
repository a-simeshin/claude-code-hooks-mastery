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

### Step 4: Update OpenSpec Change (if available)

After all tasks have been executed and validated:

1. Check if an OpenSpec change exists for this plan:
   ```bash
   openspec list --changes --json 2>/dev/null
   ```
   Look for a change matching the plan filename (kebab-case).

2. If found, read the OpenSpec tasks file:
   ```bash
   openspec show <change-name> --json 2>/dev/null
   ```

3. Mark completed tasks in `openspec/changes/<change-name>/tasks.md`:
   - For each task that the builder successfully implemented, mark its checkbox as `[x]`
   - For tasks that failed or were skipped, leave them as `[ ]`

4. Report completion status and suggest next steps:
   ```
   OpenSpec Change Updated: openspec/changes/<change-name>/tasks.md
   Completed: X/Y tasks

   Next steps:
   - Run `/opsx:verify` to validate implementation against specs
   - Run `/opsx:archive` to finalize and merge delta specs
   ```

If no OpenSpec change exists, skip this step silently.

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
