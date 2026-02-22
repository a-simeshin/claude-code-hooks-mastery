---
description: Implement the plan
argument-hint: [path-to-plan]
---

# Build

Follow the `Workflow` to implement the `PATH_TO_PLAN` then `Report` the completed work.

## Variables

PATH_TO_PLAN: $ARGUMENTS

## Workflow

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user to provide it (AskUserQuestion).

### Step 1: Structural Validation

Run the deterministic plan validator:

```bash
uv run --script $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_plan.py --file PATH_TO_PLAN --team-dir $CLAUDE_PROJECT_DIR/.claude/agents/team
```

- If errors are found, show them to the user and ask (AskUserQuestion): fix the plan, continue anyway, or abort?
- If the user chooses to fix — edit the plan file and re-run validation.
- If the user chooses to continue — proceed to Step 2.

### Step 2: Plan Review

Spawn the plan-reviewer agent for critical content review:

```
Task({
  subagent_type: "plan-reviewer",
  description: "Review plan before execution",
  prompt: "Review the plan at PATH_TO_PLAN. The original request was: '<Task Description from the plan>'. Check all 8 criteria and return a structured verdict."
})
```

- If verdict is **FAIL**, show the issues to the user and ask: fix the plan, continue anyway, or abort?
- If verdict is **PASS** or **CONDITIONAL PASS**, proceed to Step 3.

### Step 3: Execute

Read and execute the plan at `PATH_TO_PLAN`. Think hard about the plan and implement it into the codebase.

## Report

- Present the `## Report` section of the plan.