# OpenSpec

Optional integration with [@fission-ai/openspec](https://www.npmjs.com/package/@fission-ai/openspec) for living specifications, delta tracking, and change lifecycle management.

## What It Does

OpenSpec maintains living specs for your project — requirements (MUST/SHOULD/MAY), scenarios (Given/When/Then), and design decisions. When integrated into the pipeline, it connects plans to specs and tracks implementation progress.

```
/plan_w_team "add dark mode"
    ↓
Step 2:  Read existing specs → inform interview questions
Step 13: Create change artifacts → openspec/changes/add-dark-mode/
    ↓
/smart_build specs/add-dark-mode.md
    ↓
Step 4:  Mark tasks [x] → openspec view shows real-time progress
    ↓
/opsx:verify → /opsx:archive (user runs manually)
```

## Setup

```bash
npm install -g @fission-ai/openspec
openspec init --tools claude
```

This creates:
- `openspec/specs/`, `openspec/changes/`, `openspec/changes/archive/`
- `.claude/commands/opsx/*.md` — slash commands (`/opsx:explore`, `/opsx:propose`, etc.)
- `.claude/skills/openspec-*/*.md` — skills for Claude Code

## Integration Points

### 1. Explore (plan_w_team Step 2)

Reads existing specs before the requirements interview:

```bash
openspec list --specs --json 2>/dev/null
openspec show <spec-name> --json --requirements
openspec list --changes --json 2>/dev/null
```

Findings inform Interview Round 1 — the planner asks about conflicts with existing requirements, whether to extend or modify specs, and overlapping active changes.

### 2. Propose (plan_w_team Step 13)

After plan review passes, creates change artifacts:

```
openspec/changes/<name>/
├── proposal.md    — what and why
├── specs/         — delta specs (new/modified requirements)
├── design.md      — technical approach
└── tasks.md       — implementation checklist
```

### 3. Track (smart_build Step 4)

As each builder completes a task, the orchestrator marks the corresponding checkbox `[x]` in `tasks.md`. Progress is visible in real-time:

```bash
openspec view
# ◉ add-dark-mode  [████████░░░░░░░░░░░░] 40%
```

### 4. Post-build (user-driven)

After smart_build completes:
- `/opsx:verify` — validates implementation against specs
- `/opsx:archive` — finalizes change, merges delta specs into living specs

## Graceful Degradation

All OpenSpec steps check availability first (`openspec list ... 2>/dev/null`). If OpenSpec is not installed or initialized:
- Step 2 skips with "OpenSpec not available — skipping spec exploration"
- Step 13 skips with "OpenSpec not initialized — skipping artifact generation"
- Step 4 skips silently

The core pipeline works identically without OpenSpec.

## Key Files

- `.claude/commands/plan_w_team.md` — Steps 2, 13 (explore + propose)
- `.claude/commands/smart_build.md` — Steps 0, 4 (init + incremental tracking)
