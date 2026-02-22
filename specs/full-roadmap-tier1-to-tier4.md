# Plan: Full Roadmap — Tier 1 through Tier 4

## Task Description

Implement the complete development roadmap for `claude-code-hooks-mastery` repository, evolving it from a hooks showcase into a production-grade multi-agent framework for full-stack (Java + React/TypeScript + Python) applications. The roadmap spans 4 tiers: Foundation quick wins, Architecture improvements, Advanced patterns based on SOTA research, and Frontier research implementations.

## Objective

When complete, this repository will demonstrate:
1. **Tier 1**: Optimized validator dispatch (✅ DONE), populated CLAUDE.md, complete reference files for all 3 stacks, cost-optimized agent models
2. **Tier 2**: Skills-based progressive disclosure architecture, git worktree isolation for parallel agents, persistent cross-session memory, automated validation on task completion
3. **Tier 3**: Actor-critic verification pattern, multi-model patch selection, adaptive orchestration topology routing, per-task token budgeting
4. **Tier 4**: MCTS-based workflow optimization, multi-agent→single-agent distillation, market-based resource allocation

## Problem Statement

The current repository has strong hooks infrastructure (17 lifecycle events, 14 validators, smart dispatcher) and a team of 4 agents (builder, validator, monitor, context-router + meta-agent). However:
- CLAUDE.md is empty — agents get no project-level conventions
- Only Java refs exist (java-patterns.md, java-testing.md) — React and Python stacks have no reference files
- Validator agent runs on opus ($15/M tokens) when sonnet ($3/M) suffices for read-only checks
- No skills architecture — builder loads entire ref files (~20K tokens) instead of on-demand sections
- No git worktree isolation — parallel agents can conflict
- No persistent memory — agents lose learnings between sessions
- No critic/reviewer pattern — builder's work goes straight to production
- No cost controls — no token budgets, no model routing based on complexity
- No self-improvement loop — workflows are static, manually designed

## Solution Approach

Phased implementation following the research-backed principle: **"1 iteration with structure ≈ 8 iterations without"** (Slide 26 of SOTA research). Each tier builds on the previous:

- **Tier 1**: Fix foundations that every session benefits from. Low risk, high ROI.
- **Tier 2**: Architectural patterns that reduce cost and enable parallelism. Medium complexity.
- **Tier 3**: Research-backed patterns (ACC-Collab, AdaptOrch, TRAE). High impact, moderate risk.
- **Tier 4**: Frontier capabilities. Research-grade, experimental.

## Relevant Files

### Existing Infrastructure (Read/Modify)
- `.claude/settings.json` — Hook config, status line, permissions
- `.claude/agents/team/builder.md` — Builder agent with PostToolUse validator hooks
- `.claude/agents/team/validator.md` — Read-only validator agent (opus → sonnet candidate)
- `.claude/agents/team/monitor.md` — Lightweight haiku monitor agent
- `.claude/agents/context-router.md` — Haiku-based semantic context router
- `.claude/agents/meta-agent.md` — Agent configuration generator
- `.claude/commands/smart_build.md` — Semantic context routing workflow
- `.claude/commands/plan_w_team.md` — Team orchestration planning
- `.claude/hooks/validators/validator_dispatcher.py` — Smart validator dispatch (✅ Tier 1.1 DONE)
- `.claude/hooks/section_loader.py` — Section-based reference loading
- `.claude/refs/java-patterns.md` — Java code standards (816 lines, sectioned)
- `.claude/refs/java-testing.md` — Java testing patterns (1731 lines, sectioned)
- `CLAUDE.md` — Project conventions (currently empty!)

### New Files (To Create)

#### Tier 1
- `CLAUDE.md` — Project conventions (50-100 lines)
- `.claude/refs/react-patterns.md` — React/TypeScript patterns with section markers
- `.claude/refs/fastapi-patterns.md` — Python/FastAPI patterns with section markers

#### Tier 2
- `.claude/skills/java/*.md` — Java skills (spring-controller, spring-service, etc.)
- `.claude/skills/react/*.md` — React skills (component, hook, state, routing)
- `.claude/skills/python/*.md` — Python skills (fastapi-endpoint, pydantic-model, etc.)
- `.claude/hooks/task_completed.py` — TaskCompleted hook for auto-validation
- `.claude/agents/team/builder.md` — Add `memory: project` to frontmatter

#### Tier 3
- `.claude/agents/team/critic.md` — Critic agent (actor-critic pattern)
- `.claude/hooks/model_router.py` — Multi-model patch selection dispatcher
- `.claude/hooks/orchestration_router.py` — Adaptive topology selection
- `.claude/hooks/cost_budget.py` — Per-task token budget tracking
- `.claude/commands/review.md` — Critic review command

#### Tier 4
- `.claude/optimization/workflow_optimizer.py` — AFlow-inspired MCTS workflow search
- `.claude/optimization/distiller.py` — Multi-agent→single-agent distillation
- `.claude/hooks/resource_auction.py` — Market-based allocation
- `specs/aflow-experiments.md` — Experiment tracking for workflow optimization

## Implementation Phases

### Phase 1: Foundation (Tier 1) — ~2-3 hours
Complete the remaining quick wins that every session benefits from:
- 1.2: CLAUDE.md with project conventions
- 1.3: React and Python reference files with section markers
- 1.4: Downgrade validator agent from opus to sonnet

### Phase 2: Architecture (Tier 2) — ~4-6 hours
Build the architectural patterns that reduce cost and enable scale:
- 2.1: Skills architecture for on-demand loading
- 2.2: Git worktree support in builder agent
- 2.3: Persistent memory for agents
- 2.4: TaskCompleted hook for auto-validation

### Phase 3: Advanced Patterns (Tier 3) — ~6-8 hours
Implement research-backed patterns from SOTA papers:
- 3.1: Critic agent (ACC-Collab ICLR 2025)
- 3.2: Multi-model patch selection (TRAE/Devlo SWE-bench)
- 3.3: Adaptive orchestration (AdaptOrch arXiv:2602.16873)
- 3.4: Cost budgeting with token tracking

### Phase 4: Frontier (Tier 4) — ~8-12 hours, experimental
Research-grade implementations:
- 4.1: AFlow-style workflow optimization via MCTS
- 4.2: Distillation (multi-agent→single-agent compression)
- 4.3: Market-based resource allocation

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to to the building, validating, testing, deploying, and other tasks.
  - This is critical. You're job is to act as a high level director of the team, not a builder.
  - You're role is to validate all work is going well and make sure the team is on track to complete the plan.
  - You'll orchestrate this by using the Task* Tools to manage coordination between the team members.
  - Communication is paramount. You'll use the Task* Tools to communicate with the team members and ensure they're on track to complete the plan.
- Take note of the session id of each team member. This is how you'll reference them.

### Team Members

- Builder
  - Name: builder-foundation
  - Role: Implements Tier 1 items (CLAUDE.md, ref files, model changes)
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: builder-architecture
  - Role: Implements Tier 2 items (skills, worktrees, memory, hooks)
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: builder-patterns
  - Role: Implements Tier 3 items (critic agent, model router, orchestration, budgets)
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: builder-frontier
  - Role: Implements Tier 4 items (AFlow, distillation, market allocation)
  - Agent Type: general-purpose
  - Resume: true

- Validator
  - Name: validator-tier
  - Role: Validates each tier's deliverables against acceptance criteria
  - Agent Type: validator
  - Resume: false

- Monitor
  - Name: monitor-progress
  - Role: Reports agent progress every 10 seconds during parallel execution
  - Agent Type: monitor
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

---

### 1. Populate CLAUDE.md with Project Conventions (Tier 1.2)
- **Task ID**: tier1-claude-md
- **Depends On**: none
- **Assigned To**: builder-foundation
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier1-refs)
- Write CLAUDE.md (50-100 lines) with:
  - Project description: Claude Code hooks mastery repo demonstrating all 17 lifecycle hooks + multi-agent patterns
  - Language/stack detection rules (pom.xml → Java, package.json → React/TS, pyproject.toml → Python)
  - Code style rules: link to `.claude/refs/` for each stack
  - Agent conventions: builder writes code, validator reads only, monitor observes
  - Hook conventions: all hooks in `.claude/hooks/`, validators in `.claude/hooks/validators/`
  - Ref file structure: section markers `<!-- section:name -->` ... `<!-- /section:name -->`
  - Testing conventions: validators run automatically via PostToolUse hooks
  - Important: keep under 100 lines, only what Claude can't infer from code
- Read existing CLAUDE.md (empty), java-patterns.md (for section marker format), settings.json (for hook config)

### 2. Create React/TypeScript Reference File (Tier 1.3a)
- **Task ID**: tier1-react-ref
- **Depends On**: none
- **Assigned To**: builder-foundation
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier1-claude-md and tier1-python-ref)
- Create `.claude/refs/react-patterns.md` with section markers matching context-router.md's expected sections:
  - `<!-- section:components -->` — Component patterns (functional, composition, props, children)
  - `<!-- section:hooks -->` — Hook patterns (useState, useEffect, useMemo, custom hooks)
  - `<!-- section:state -->` — State management (Context API, Redux Toolkit, Zustand patterns)
  - `<!-- section:routing -->` — React Router patterns (nested routes, loaders, guards)
- Use Context7 to get latest React docs for accurate patterns
- Follow same structure as java-patterns.md: code examples with BAD/GOOD comparisons
- Target: 400-600 lines covering the 80/20 of React development

### 3. Create Python/FastAPI Reference File (Tier 1.3b)
- **Task ID**: tier1-python-ref
- **Depends On**: none
- **Assigned To**: builder-foundation
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier1-react-ref)
- Create `.claude/refs/fastapi-patterns.md` with section markers:
  - `<!-- section:basics -->` — Code style (ruff rules, type hints, Pydantic models)
  - `<!-- section:endpoints -->` — FastAPI endpoint patterns (routers, dependencies, responses)
  - `<!-- section:models -->` — Pydantic v2 patterns (validators, serializers, settings)
  - `<!-- section:testing -->` — Pytest patterns (fixtures, parametrize, httpx AsyncClient)
  - `<!-- section:security -->` — Security patterns (OAuth2, JWT, CORS, input validation)
- Use Context7 to get latest FastAPI docs
- Target: 400-600 lines

### 4. Downgrade Validator Agent to Sonnet (Tier 1.4)
- **Task ID**: tier1-validator-model
- **Depends On**: none
- **Assigned To**: builder-foundation
- **Agent Type**: builder
- **Parallel**: true
- Edit `.claude/agents/team/validator.md`: change `model: opus` → `model: sonnet`
- Rationale: Validator is read-only (disallowedTools: Write, Edit), runs verification commands and reads files. Sonnet ($3/M) is sufficient for read-only checks vs opus ($15/M). Saves 80% on validation cost.
- Update context-router.md to add react-patterns and fastapi-patterns sections to the Available Sections table

### 5. Validate Tier 1 Deliverables
- **Task ID**: tier1-validate
- **Depends On**: tier1-claude-md, tier1-react-ref, tier1-python-ref, tier1-validator-model
- **Assigned To**: validator-tier
- **Agent Type**: validator
- **Parallel**: false
- Verify CLAUDE.md exists and is 50-100 lines
- Verify `.claude/refs/react-patterns.md` exists with section markers (components, hooks, state, routing)
- Verify `.claude/refs/fastapi-patterns.md` exists with section markers (basics, endpoints, models, testing, security)
- Verify validator.md has `model: sonnet`
- Verify context-router.md includes react-patterns and fastapi-patterns sections
- Run section_loader.py with test inputs to verify sections load correctly:
  ```bash
  echo '{"sections": ["react-patterns#components"]}' | uv run --script .claude/hooks/section_loader.py
  echo '{"sections": ["fastapi-patterns#endpoints"]}' | uv run --script .claude/hooks/section_loader.py
  ```

---

### 6. Create Skills Architecture (Tier 2.1)
- **Task ID**: tier2-skills
- **Depends On**: tier1-validate
- **Assigned To**: builder-architecture
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier2-worktrees)
- Create `.claude/skills/` directory structure:
  ```
  .claude/skills/
  ├── java/
  │   ├── spring-controller.md    — REST controller patterns
  │   ├── spring-service.md       — Service layer patterns
  │   ├── spring-entity.md        — JPA entity patterns
  │   ├── spring-repository.md    — Repository patterns
  │   └── spring-test.md          — Test patterns (unit + integration)
  ├── react/
  │   ├── component.md            — Component creation patterns
  │   ├── hook.md                 — Custom hook patterns
  │   ├── form.md                 — Form handling patterns
  │   └── api-integration.md      — API call patterns (React Query, SWR)
  └── python/
      ├── fastapi-endpoint.md     — Endpoint patterns
      ├── pydantic-model.md       — Model patterns
      ├── pytest-fixture.md       — Test fixture patterns
      └── dependency-injection.md — FastAPI DI patterns
  ```
- Each skill file is 50-150 lines, focused on ONE pattern
- Skills replace monolithic refs for builder agent context — load only the skill needed
- Update builder.md to reference skills in Auto-References section
- Skills are loaded by context-router based on task keywords → more granular than ref sections
- Research: This follows "Skills-based loading: 82% improvement over upfront loading" (Slide 25)

### 7. Add Git Worktree Support (Tier 2.2)
- **Task ID**: tier2-worktrees
- **Depends On**: tier1-validate
- **Assigned To**: builder-architecture
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier2-skills)
- Update `.claude/commands/plan_w_team.md` to document worktree usage in Task tool:
  ```yaml
  Task({
    description: "Build feature X",
    prompt: "...",
    subagent_type: "builder",
    isolation: "worktree"  # Each agent works in isolated git worktree
  })
  ```
- Update builder.md instructions to be worktree-aware:
  - Check if running in worktree (detect `.git` file vs `.git` directory)
  - Use relative paths, not absolute
  - Don't modify files outside worktree
- Create `.claude/hooks/worktree_cleanup.py` — SessionEnd hook that cleans up stale worktrees:
  - List worktrees: `git worktree list`
  - Remove worktrees older than 1 hour with no changes
  - Log cleanup to `logs/worktree_cleanup.log`
- Research: incident.io pattern — "Parallel feature shipping with git worktrees"

### 8. Add Persistent Memory to Agents (Tier 2.3)
- **Task ID**: tier2-memory
- **Depends On**: tier1-validate
- **Assigned To**: builder-architecture
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier2-skills and tier2-worktrees)
- Add `memory: project` to builder.md frontmatter (enables cross-session learning)
- Create `.claude/memory/` directory for project-level memory storage:
  - `.claude/memory/patterns.md` — Patterns learned across sessions
  - `.claude/memory/failures.md` — Common failures and fixes
  - `.claude/memory/decisions.md` — Architectural decisions made
- Update builder.md workflow to check memory before implementing:
  ```
  Step 0: Check Memory
  - Read .claude/memory/patterns.md for relevant patterns
  - Read .claude/memory/failures.md for known pitfalls
  ```
- Create `.claude/hooks/memory_update.py` — Stop hook that:
  - Extracts key learnings from session transcript
  - Appends to appropriate memory file
  - Keeps each file under 200 lines (prune oldest entries)
- Research: A-MEM (NeurIPS 2025) — self-organizing Zettelkasten pattern for agent memory

### 9. Create TaskCompleted Auto-Validation Hook (Tier 2.4)
- **Task ID**: tier2-task-completed
- **Depends On**: tier1-validate
- **Assigned To**: builder-architecture
- **Agent Type**: builder
- **Parallel**: true
- Create `.claude/hooks/task_completed.py` — fires when a task is marked completed:
  - Read task details from stdin JSON
  - If task has acceptance criteria, auto-spawn validator agent
  - Log validation results to `logs/task_validation.log`
  - If validation fails, update task status back to `in_progress` with failure reason
- NOTE: This requires the `TaskCompleted` hook event. If not yet available in Claude Code, implement as a PostToolUse hook on TaskUpdate that triggers when status changes to "completed"
- Register in settings.json (or builder.md hooks section)

### 10. Validate Tier 2 Deliverables
- **Task ID**: tier2-validate
- **Depends On**: tier2-skills, tier2-worktrees, tier2-memory, tier2-task-completed
- **Assigned To**: validator-tier
- **Agent Type**: validator
- **Parallel**: false
- Verify skills directory structure exists with all skill files
- Verify each skill file has clear patterns and is 50-150 lines
- Verify builder.md has `memory: project` in frontmatter
- Verify worktree documentation is updated
- Verify worktree_cleanup.py hook exists and is syntactically correct
- Verify memory directory exists with template files
- Verify task_completed.py hook exists and handles JSON input correctly
- Run: `uv run --script .claude/hooks/task_completed.py < test_input.json` with mock data

---

### 11. Create Critic Agent (Tier 3.1)
- **Task ID**: tier3-critic
- **Depends On**: tier2-validate
- **Assigned To**: builder-patterns
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier3-model-router)
- Create `.claude/agents/team/critic.md`:
  ```yaml
  ---
  name: critic
  description: Actor-Critic review agent. Reviews code changes for correctness, security, performance, and adherence to patterns.
  model: sonnet
  disallowedTools: Write, Edit, NotebookEdit
  tools: Read, Bash, Glob, Grep, TaskGet, TaskUpdate
  color: red
  ---
  ```
- Critic agent workflow:
  1. Read the task description and acceptance criteria (TaskGet)
  2. Read the files that were changed (from task description)
  3. Check against reference patterns (load appropriate .claude/refs/ or .claude/skills/)
  4. Run static analysis commands (read-only)
  5. Produce structured review:
     - ✅ Passes / ❌ Fails for each criterion
     - Security concerns (OWASP top 10 check)
     - Performance concerns (N+1 queries, unnecessary allocations)
     - Pattern adherence (matches ref file patterns?)
  6. Update task with review results
- Create `/review` command (`.claude/commands/review.md`) that:
  1. Takes a task ID or file list
  2. Deploys critic agent to review
  3. Returns structured pass/fail report
- Research: ACC-Collab ICLR 2025 — Actor (builder) + Critic (reviewer) outperforms unconstrained multi-agent debate

### 12. Implement Multi-Model Patch Selection (Tier 3.2)
- **Task ID**: tier3-model-router
- **Depends On**: tier2-validate
- **Assigned To**: builder-patterns
- **Agent Type**: builder
- **Parallel**: true (can run alongside tier3-critic)
- Create `.claude/hooks/model_router.py` — PreToolUse hook for Task tool:
  - Reads task description and complexity estimation
  - Routes to appropriate model:
    ```
    Simple (typo fix, single file) → haiku ($0.25/M)
    Medium (feature, 2-5 files)    → sonnet ($3/M)
    Complex (architecture, 5+ files) → opus ($15/M)
    ```
  - Complexity heuristics:
    - Count mentioned files → more files = more complex
    - Keywords: "refactor", "architecture", "redesign" → complex
    - Keywords: "fix typo", "update text", "rename" → simple
    - Default: sonnet (best cost/quality ratio)
  - Logs routing decisions to `logs/model_routing.log`
- Update plan_w_team.md to recommend model routing in orchestration
- Research: TRAE/Devlo SWE-bench pattern — generate patches with multiple models, pick best

### 13. Add Adaptive Orchestration (Tier 3.3)
- **Task ID**: tier3-adaptive-orch
- **Depends On**: tier2-validate
- **Assigned To**: builder-patterns
- **Agent Type**: builder
- **Parallel**: true
- Create `.claude/hooks/orchestration_router.py`:
  - Analyzes task structure to select optimal topology:
    ```
    Independent subtasks     → Parallel agents (fan-out/fan-in)
    Sequential pipeline      → Chain (builder → critic → validator)
    Quality-critical         → Layered MoA (multiple builders → critic selects best)
    Simple single task       → Single agent (skip orchestration overhead)
    ```
  - Decision based on:
    - Task decomposability (can it be split?)
    - Verification requirements (does it need review?)
    - File overlap (can agents work independently?)
  - Returns recommended orchestration as JSON:
    ```json
    {
      "topology": "parallel",
      "agents": ["builder-api", "builder-frontend"],
      "critic": true,
      "worktrees": true,
      "estimated_cost": "$0.50"
    }
    ```
- Update smart_build.md to use orchestration_router before deploying agents
- Research: AdaptOrch (arXiv:2602.16873) — 12-23% gain from optimal orchestration vs 3-5% from model switch

### 14. Implement Cost Budget Tracking (Tier 3.4)
- **Task ID**: tier3-cost-budget
- **Depends On**: tier2-validate
- **Assigned To**: builder-patterns
- **Agent Type**: builder
- **Parallel**: true
- Create `.claude/hooks/cost_budget.py`:
  - Tracks estimated token usage per session/task
  - Token estimation:
    - Read tool: ~tokens of file content
    - Write/Edit tool: ~tokens of changes
    - Bash tool: ~500 tokens average
    - Task (subagent): model-specific rate × estimated turns
  - Budget enforcement:
    - Per-task budget (default: $1 for simple, $5 for complex)
    - Per-session budget (default: $20)
    - Warning at 80% budget consumed
    - Hard stop at 100% (return budget exceeded message)
  - Budget defined in CLAUDE.md or per-task in spec files
  - Logs to `logs/cost_tracking.log` and updates status line data
- Update status_line_v10.py to show cost tracking in status bar
- Create `.claude/hooks/cost_report.py` — SessionEnd hook that:
  - Summarizes total token usage and estimated cost
  - Breaks down by agent/model
  - Compares to budget
  - Writes report to `logs/cost_reports/session_{id}.json`

### 15. Validate Tier 3 Deliverables
- **Task ID**: tier3-validate
- **Depends On**: tier3-critic, tier3-model-router, tier3-adaptive-orch, tier3-cost-budget
- **Assigned To**: validator-tier
- **Agent Type**: validator
- **Parallel**: false
- Verify critic.md agent exists with correct frontmatter (model: sonnet, disallowedTools: Write/Edit)
- Verify /review command exists and references critic agent
- Verify model_router.py handles simple/medium/complex routing
- Verify orchestration_router.py returns valid topology JSON
- Verify cost_budget.py tracks and enforces budgets
- Test model_router.py with mock task inputs at each complexity level
- Test cost_budget.py budget exceeded scenario

---

### 16. AFlow-Style Workflow Optimization (Tier 4.1)
- **Task ID**: tier4-aflow
- **Depends On**: tier3-validate
- **Assigned To**: builder-frontier
- **Agent Type**: general-purpose
- **Parallel**: true (can run alongside tier4-distillation)
- Create `.claude/optimization/workflow_optimizer.py`:
  - Implements simplified MCTS over workflow configurations:
    - Node = workflow configuration (agent topology + model selection + prompt template)
    - Edge = modification (add/remove agent, change model, modify prompt)
    - Reward = task success rate × (1/cost) — balance quality vs cost
  - Workflow representation as code (AFlow pattern):
    ```python
    class Workflow:
        agents: list[AgentConfig]
        topology: str  # "parallel" | "chain" | "layered"
        model_routing: dict[str, str]
        prompt_templates: dict[str, str]
    ```
  - MCTS search:
    1. Select: UCB1 to pick promising workflow variant
    2. Expand: Modify one aspect (add critic, change model, etc.)
    3. Simulate: Run modified workflow on test task
    4. Backpropagate: Update success rate
  - Experiment tracking in `specs/aflow-experiments.md`
- This is experimental — start with 3-5 test tasks, measure success rate
- Research: AFlow ICLR 2025 Oral (top 1.8%) — arXiv:2410.10762

### 17. Multi-Agent→Single-Agent Distillation (Tier 4.2)
- **Task ID**: tier4-distillation
- **Depends On**: tier3-validate
- **Assigned To**: builder-frontier
- **Agent Type**: general-purpose
- **Parallel**: true (can run alongside tier4-aflow)
- Create `.claude/optimization/distiller.py`:
  - Records successful multi-agent sessions:
    - Task description
    - Agent interactions (who did what)
    - Final output
    - Validation results
  - Compresses multi-agent patterns into single-agent prompts:
    - Extract the "chain of thought" from multi-agent collaboration
    - Convert agent roles into prompt sections
    - Example: builder+critic → single prompt with "First implement, then self-review with checklist: [...]"
  - Creates distilled skills in `.claude/skills/distilled/`:
    - `spring-crud-distilled.md` — Distilled from builder+critic+validator sessions
    - Each distilled skill encodes the multi-agent workflow as a single-agent checklist
  - Cost comparison tracking: multi-agent vs distilled single-agent
- Research: AgentArk (arXiv:2602.03955) — compress multi-agent intelligence into single LLM

### 18. Market-Based Resource Allocation (Tier 4.3)
- **Task ID**: tier4-market
- **Depends On**: tier3-validate
- **Assigned To**: builder-frontier
- **Agent Type**: general-purpose
- **Parallel**: true
- Create `.claude/hooks/resource_auction.py`:
  - Implements simple auction mechanism for agent resource allocation:
    - Each task has a "value" (estimated business impact)
    - Each agent has a "cost" (model rate × estimated tokens)
    - Auction: tasks compete for agent time based on value/cost ratio
  - Priority queue:
    ```
    Priority = task_value / estimated_cost × urgency_multiplier
    ```
  - Resource constraints:
    - Max parallel agents (configurable, default: 3)
    - Total budget per session
    - Model availability (prefer cheaper models when budget is low)
  - Dynamic reallocation:
    - If task is taking longer than estimated, reassess priority
    - If budget is running low, switch to cheaper models
    - If task value drops (user changes mind), release resources
- Integrate with cost_budget.py for budget enforcement
- Research: Economic/market-based multi-agent coordination (Section 17 of SOTA research)

### 19. Validate Tier 4 Deliverables
- **Task ID**: tier4-validate
- **Depends On**: tier4-aflow, tier4-distillation, tier4-market
- **Assigned To**: validator-tier
- **Agent Type**: validator
- **Parallel**: false
- Verify workflow_optimizer.py exists and implements MCTS search
- Verify distiller.py records sessions and produces distilled skills
- Verify resource_auction.py implements priority queue allocation
- Verify each script handles edge cases (empty input, budget exceeded, no tasks)
- Run: `python -m py_compile` on all new Python files to verify syntax
- Check all new files follow existing patterns (uv script headers, logging, etc.)

### 20. Final Integration Validation
- **Task ID**: final-validate
- **Depends On**: tier4-validate
- **Assigned To**: validator-tier
- **Agent Type**: validator
- **Parallel**: false
- Full system check:
  - All 4 tiers implemented
  - CLAUDE.md populated (50-100 lines)
  - 4 ref files (java-patterns, java-testing, react-patterns, fastapi-patterns)
  - Skills directory with 12+ skill files
  - 5 agent definitions (builder, validator, monitor, context-router, critic)
  - Validator on sonnet model
  - Memory directory with template files
  - All new hooks syntactically valid
  - All new commands reference correct agent types
- Generate summary report with file counts, line counts, estimated cost savings

## Acceptance Criteria

### Tier 1 (Foundation)
- [ ] CLAUDE.md exists, 50-100 lines, covers all stacks and conventions
- [ ] `.claude/refs/react-patterns.md` exists with 4 sections (components, hooks, state, routing)
- [ ] `.claude/refs/fastapi-patterns.md` exists with 5 sections (basics, endpoints, models, testing, security)
- [ ] section_loader.py correctly loads new sections
- [ ] validator.md has `model: sonnet`
- [ ] context-router.md includes react-patterns and fastapi-patterns

### Tier 2 (Architecture)
- [ ] `.claude/skills/` directory exists with 12+ skill files across 3 stacks
- [ ] Each skill file is 50-150 lines with clear patterns
- [ ] builder.md references skills in workflow
- [ ] builder.md has `memory: project` in frontmatter
- [ ] `.claude/memory/` directory exists with template files
- [ ] worktree_cleanup.py hook exists and is syntactically valid
- [ ] task_completed.py hook exists and processes JSON input
- [ ] plan_w_team.md documents worktree isolation pattern

### Tier 3 (Advanced Patterns)
- [ ] critic.md agent exists with read-only constraints
- [ ] `/review` command exists and deploys critic agent
- [ ] model_router.py routes simple→haiku, medium→sonnet, complex→opus
- [ ] orchestration_router.py selects topology based on task structure
- [ ] cost_budget.py tracks token usage and enforces budgets
- [ ] cost_report.py generates session cost reports

### Tier 4 (Frontier)
- [ ] workflow_optimizer.py implements MCTS search skeleton
- [ ] distiller.py records sessions and produces distilled skill templates
- [ ] resource_auction.py implements priority queue allocation
- [ ] All new Python files pass `python -m py_compile`
- [ ] Experiment tracking spec exists

## Validation Commands

Execute these commands to validate the task is complete:

```bash
# Tier 1: Check files exist and have content
wc -l CLAUDE.md  # Should be 50-100 lines
wc -l .claude/refs/react-patterns.md  # Should be 400-600 lines
wc -l .claude/refs/fastapi-patterns.md  # Should be 400-600 lines
grep "model: sonnet" .claude/agents/team/validator.md  # Should match

# Tier 1: Test section loading
echo '{"sections": ["react-patterns#components"]}' | uv run --script .claude/hooks/section_loader.py
echo '{"sections": ["fastapi-patterns#endpoints"]}' | uv run --script .claude/hooks/section_loader.py

# Tier 2: Check skills structure
find .claude/skills -name "*.md" | wc -l  # Should be >= 12
ls .claude/memory/  # Should have template files

# Tier 2: Verify memory in builder
grep "memory: project" .claude/agents/team/builder.md  # Should match

# Tier 3: Check new agents and hooks
ls .claude/agents/team/critic.md  # Should exist
ls .claude/commands/review.md  # Should exist
python -m py_compile .claude/hooks/model_router.py
python -m py_compile .claude/hooks/orchestration_router.py
python -m py_compile .claude/hooks/cost_budget.py

# Tier 4: Check frontier scripts
python -m py_compile .claude/optimization/workflow_optimizer.py
python -m py_compile .claude/optimization/distiller.py
python -m py_compile .claude/hooks/resource_auction.py

# Full count
find .claude -name "*.md" -o -name "*.py" | wc -l  # Total file count
```

## Notes

### Dependencies & Tools
- No new external dependencies needed for Tier 1-2
- Tier 3-4 may need: `tiktoken` for token counting (cost tracking), `numpy` for MCTS statistics
- Install via: `uv add tiktoken numpy` (only when implementing Tier 3-4)

### Risk Mitigation
- **Tier 1**: Zero risk — purely additive, no breaking changes
- **Tier 2**: Low risk — skills are additive, memory is opt-in, worktrees are isolated
- **Tier 3**: Medium risk — model routing needs testing to avoid sending complex tasks to haiku. Cost tracking needs careful token estimation.
- **Tier 4**: High risk — experimental by design. AFlow MCTS may not converge. Distillation quality depends on session diversity. Market allocation may be over-engineered. Implement as opt-in only.

### Execution Strategy
- **Tier 1**: Execute all 4 tasks in parallel (no dependencies between them)
- **Tier 2**: Execute all 4 tasks in parallel (all depend only on Tier 1)
- **Tier 3**: Execute all 4 tasks in parallel (all depend only on Tier 2)
- **Tier 4**: Execute all 3 tasks in parallel (all depend only on Tier 3)
- Each tier ends with a validation step before proceeding to next tier

### Research References
- ACC-Collab (ICLR 2025): Actor-Critic pattern — [openreview.net](https://openreview.net/forum?id=nfKfAzkiez)
- AdaptOrch (Feb 2026): Adaptive orchestration — [arXiv:2602.16873](https://arxiv.org/abs/2602.16873)
- AFlow (ICLR 2025 Oral): Workflow optimization — [arXiv:2410.10762](https://arxiv.org/abs/2410.10762)
- AgentArk (Feb 2026): Distillation — [arXiv:2602.03955](https://arxiv.org/abs/2602.03955)
- Google/DeepMind Scaling (Dec 2025): Scaling laws — [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)
- MAST (ICLR 2025): Failure taxonomy — [arXiv:2503.13657](https://arxiv.org/abs/2503.13657)
- HULA/Atlassian (ICSE 2025): Human-AI teaming — [arXiv:2411.12924](https://arxiv.org/abs/2411.12924)
- incident.io: Git worktrees in production — [incident.io/blog](https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees)
