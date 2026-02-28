# Plan Review (Critic Pattern)

During planning, `/plan_w_team` runs a **two-stage validation gate** (Step 12) — structural checks + architect-level content review. This prevents wasted compute on flawed plans and ensures quality before OpenSpec artifacts are generated.

## How It Works

```mermaid
flowchart LR
    A["specs/*.md"] --> B["validate_plan.py<br/>(structural)"]
    B -->|FAIL| C[Fix & retry]
    B -->|PASS| D["plan-reviewer<br/>(Opus critic)"]
    D -->|FAIL| C
    D -->|PASS| E[Execute plan]
```

## Stage 1 — Structural Validation

`validate_plan.py` — deterministic, zero cost:

- Required sections present (Task Description, Objective, Steps, Acceptance Criteria)
- Agent types reference existing `.claude/agents/team/*.md` files
- Task dependencies form a valid DAG (no cycles, no missing refs)
- Team member roles match available agent types

## Stage 2 — Content Review

`plan-reviewer.md` — Opus critic agent evaluates the plan against **8 criteria**:

| # | Criterion | PASS | FAIL |
|---|-----------|------|------|
| 1 | **Problem Alignment** | Plan directly addresses the stated problem | Plan solves a different or tangential problem |
| 2 | **Completeness** | Every requirement maps to at least one task | Major requirements have no corresponding tasks |
| 3 | **Questions Gap** | No critical unknowns remain | Critical decisions assumed without justification |
| 4 | **Risk Assessment** | Risks identified and mitigated | Risky operations present without safeguards |
| 5 | **Overengineering** | Complexity matches problem scope | Unnecessarily complex for the problem |
| 6 | **Pattern Compliance** | Follows existing project patterns | Contradicts patterns without explanation |
| 7 | **Dependency Correctness** | Dependencies reflect actual build order | Tasks depend on things not yet built |
| 8 | **Cost Appropriateness** | Models match task complexity | Opus for trivial tasks or Haiku for complex reasoning |

**Verdict:** PASS / CONDITIONAL PASS / FAIL. One FAIL on any criterion = overall FAIL.

## Integration with `/plan_w_team`

```bash
/plan_w_team "add dark mode"
# Steps 1-11: analyze, interview, design, save plan
# Step 12: validate_plan.py → structural check
# Step 12: plan-reviewer agent → content review
# If both pass → Step 13 (OpenSpec propose)
# If either fails → show issues, ask user to fix or abort
```

`/smart_build` no longer runs plan review — it trusts that the plan was reviewed during `/plan_w_team`.

## Real-World Example

When tested on `specs/hooks-update-with-team.md`, the critic detected:

- All 5 "new" hook files **already existed** (up to 319 lines each with `fcntl` file locking, TTS, regex patterns)
- All 5 status lines v5-v9 **already existed**, plus v10 the plan didn't know about
- `settings.json` **already configured** with all hooks
- The plan deployed **14 agents for zero-delta work**

**Verdict: FAIL** on 4/8 criteria (Problem Alignment, Questions Gap, Overengineering, Cost Appropriateness) — prevented a 14-agent deployment that would have either been a no-op or destructively overwritten working code.

## Research Basis

- [ACC-Collab (ICLR 2025)](https://openreview.net/forum?id=nfKfAzkiez) — Actor-Critic Constrained Collaboration outperforms unconstrained multi-agent debate. The builder (actor) proposes, the critic reviews with structured constraints.
- [MAST (ICLR 2025)](https://arxiv.org/abs/2503.13657) — Multi-Agent Software Testing failure taxonomy. 53.1% of multi-agent failures stem from planning errors — validating plans before execution addresses the largest failure category.
- [AdaptOrch (2026)](https://arxiv.org/abs/2602.16873) — Adaptive orchestration shows 12-23% improvement from optimal agent topology selection, validating the cost-appropriateness criterion.

## Key Files

- `.claude/hooks/validators/validate_plan.py` — structural plan validation
- `.claude/agents/team/plan-reviewer.md` — Opus critic agent definition
- `.claude/commands/plan_w_team.md` — integration point (Step 12)
