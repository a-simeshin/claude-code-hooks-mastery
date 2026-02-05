---
allowed-tools: Task, Read, Bash, Write, Edit, Glob, Grep
description: Smart builder with semantic context routing - loads only relevant sections
argument-hint: [task description]
---

# Smart Build

Build with **semantic context routing** - loads only the sections you need.

## Workflow

### Step 1: Analyze Task with Context Router

Call `@agent-context-router` with the task:

```
Task: $ARGUMENTS
```

The router will return JSON like:
```json
{
  "sections": ["java-patterns#basics", "java-testing#integration"],
  "reasoning": "..."
}
```

### Step 2: Load Sections

Run section loader with the router's output:

```bash
echo '{"sections": ["java-patterns#basics", "java-testing#integration"]}' | \
  uv run $CLAUDE_PROJECT_DIR/.claude/hooks/section_loader.py
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
