---
description: Creates a concise engineering implementation plan based on user requirements and saves it to specs directory
argument-hint: [user prompt] [orchestration prompt]
model: opus
disallowed-tools: EnterPlanMode
hooks:
  Stop:
    - hooks:
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_new_file.py
            --directory specs
            --extension .md
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_file_contains.py
            --directory specs
            --extension .md
            --contains '## Task Description'
            --contains '## Objective'
            --contains '## Relevant Files'
            --contains '## Step by Step Tasks'
            --contains '## Testing Strategy'
            --contains '## Test Infrastructure (User-Declared)'
            --contains '## Acceptance Criteria'
            --contains '## Team Orchestration'
            --contains '### Team Members'
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_plan.py
            --directory specs
            --extension .md
            --team-dir $CLAUDE_PROJECT_DIR/.claude/agents/team
---

# Plan With Team

Create a detailed implementation plan based on the user's requirements provided through the `USER_PROMPT` variable. Analyze the request, think through the implementation approach, and save a comprehensive specification document to `PLAN_OUTPUT_DIRECTORY/<name-of-plan>.md` that can be used as a blueprint for actual development work. Follow the `Instructions` and work through the `Workflow` to create the plan.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/`
TEAM_MEMBERS: `.claude/agents/team/*.md`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is a plan document saved to `PLAN_OUTPUT_DIRECTORY`.
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Determine the task type (chore|feature|refactor|fix|enhancement) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents to understand existing patterns and architecture
- Follow the Plan Format below to create a comprehensive implementation plan
- Include all required sections and conditional sections based on task type and complexity
- Generate a descriptive, kebab-case filename based on the main topic of the plan
- Save the complete implementation plan to `PLAN_OUTPUT_DIRECTORY/<descriptive-name>.md`
- Ensure the plan is detailed enough that another developer could follow it to implement the solution
- Include code examples or pseudo-code where appropriate to clarify complex concepts
- Consider edge cases, error handling, and scalability concerns
- Understand your role as the team lead. Refer to the `Team Orchestration` section for more details.
- **CRITICAL — Testing Strategy**: Every plan MUST include a `## Testing Strategy` section defining the test pyramid for this feature. Follow the **80/15/5 ratio**: 80% unit tests, 15% integration/API tests, 5% UI e2e tests. A dedicated testing task MUST exist before the final validation task. Each implementation task should note what test coverage it requires in the `**Tests**` field.
- **CRITICAL — Plan-as-Contract**: Every plan MUST include a `## Test Infrastructure (User-Declared)` section that records — per stack — machine-verifiable test layer assertions: `Files glob`, `Infra signature` (regex), `Happy-path scenarios` (named), `Runner command`, `Realism rationale`. The post-build hook `check_test_layers.py` and the `validator` agent both rely on this section to verify the realism of what was actually built. The section is filled during the **Test Infra Interview** (Workflow Step 4.5) — never invent it from thin air.
- **CRITICAL — Mandatory Integration Layer**: The integration happy-path layer is **mandatory and cannot be opted out of** — not even for "internal-only refactor" changes. Every plan MUST declare ≥1 integration scenario per affected user-facing endpoint or use-case. Plans that try to mark `### Integration Layer` as `Skipped`/`Opted out` will be rejected by `plan-reviewer` (criterion 10). The E2E layer is the only optional layer, and only when no frontend is detected in the project.
- **CRITICAL — Separate Test-Layer Tasks**: The single combined `write-tests` task is forbidden. Plans MUST split the testing work into per-layer task IDs: `unit-tests` and `integration-tests` are mandatory; `e2e-tests` is required if the E2E layer is enabled. Each task gets its own context, its own `**Stack**`, and its own `**Tests**` field.
- **CRITICAL — Context Routing**: Every task MUST include a `**Stack**` field with keywords from the **Section Routing Catalog** below. The builder agent uses keyword-based context routing to load coding standards. Without correct keywords, the builder works without project standards.
  - Always include at least one **stack keyword** (Java/React/Python) to select the correct stack
  - Then add **section keywords** matching what the task actually does (error handling, testing, etc.)
  - Example: a task creating a Spring controller with error handling → `Stack: Java Spring Boot controller exception error handling`
  - Example: a task writing MockMvc integration tests → `Stack: Java MockMvc integration test Testcontainers`
  - The Stop hook validator will reject plans where Stack keywords don't route to any section

#### Section Routing Catalog

Pick keywords from the **Trigger keywords** column. Each keyword you include loads the corresponding section into the builder's context.

| Section | Trigger keywords | Add when task involves |
|---------|-----------------|----------------------|
| **Java** | | |
| `java-patterns#basics` | `java`, `spring`, `controller`, `entity`, `jpa`, `maven`, `lombok` | Any Java/Spring Boot code |
| `java-patterns#errors` | `exception`, `error handling`, `controlleradvice`, `404`, `400`, `500` | Exception classes, @ControllerAdvice, HTTP error responses |
| `java-patterns#java17` | `record`, `pattern matching`, `switch expression`, `text block`, `sealed` | Java 17 language features |
| `java-patterns#java21` | `virtual thread`, `sequenced collection` | Java 21 language features |
| **Java Testing** | | |
| `java-testing#structure` | `assertj`, `allure`, `test naming`, `test structure` | Test organization, naming, Allure annotations |
| `java-testing#integration` | `testcontainers`, `integration test`, `podman` | Integration tests with containers |
| `java-testing#http` | `mockmvc`, `resttemplate`, `http test` | HTTP/REST endpoint testing |
| `java-testing#kafka` | `kafka test`, `consumer test`, `producer test` | Kafka integration testing |
| `java-testing#jdbc` | `database test`, `repository test`, `jdbc test` | Database/repository testing |
| `java-testing#mockito` | `mockito`, `spy` | Unit tests with mocking |
| `java-testing#e2e` | `selenide`, `e2e`, `page object` | End-to-end browser testing |
| `java-testing#maven` | `surefire`, `failsafe`, `jacoco` | Maven test plugins, coverage |
| **React** | | |
| `react-patterns#core` | `react`, `component`, `hook`, `useState`, `useEffect`, `tsx` | Any React code |
| `react-patterns#nextjs` | `next.js`, `server component`, `app router`, `server action` | Next.js App Router features |
| `react-patterns#vite` | `vite`, `react-router`, `code splitting` | Vite bundler, React Router |
| **Python Patterns** | | |
| `python-patterns#layout` | `pyproject`, `ruff`, `pyright`, `pre-commit`, `src layout` | Project layout, toolchain |
| `python-patterns#typing` | `python`, `.py`, `typing`, `Protocol`, `Final`, `Literal`, `NewType`, `@override` | Type system baseline (companion auto) |
| `python-patterns#data` | `dataclass`, `frozen=True`, `slots`, `Pydantic`, `Enum`, `StrEnum` | Data modeling, value objects |
| `python-patterns#errors` | `python exception`, `ExceptionGroup`, `raise from`, `custom exception` | Error handling, exception hierarchy |
| `python-patterns#logging` | `structlog`, `python logging`, `logger.bind` | Structured logging |
| `python-patterns#io` | `pathlib`, `Path`, `context manager`, `aiofiles` | I/O, resources |
| `python-patterns#idiom` | `comprehension`, `match/case`, `functools`, `lru_cache`, `singledispatch` | Functional idioms |
| `python-patterns#fastapi` | `fastapi`, `apirouter`, `depends`, `lifespan`, `pydantic-settings`, `field_validator` | FastAPI endpoints, Pydantic |
| `python-patterns#concurrency` | `asyncio`, `gather`, `taskgroup`, `connection pool`, `cancellation`, `httpx`, `streamingresponse`, `sync клиент` | Async/concurrency for FastAPI |
| **Python Testing** | | |
| `python-testing#structure` | `pytest`, `pytest.raises`, `arrange act assert` | Pytest baseline (companion auto) |
| `python-testing#config` | `asyncio_mode`, `strict-markers`, `xfail_strict`, `conftest hierarchy` | Pytest configuration |
| `python-testing#fixtures` | `fixture`, `scope`, `factory fixture`, `polyfactory` | Fixtures, factories |
| `python-testing#parametrize` | `parametrize`, `pytest.param`, `data-driven` | Parametrized tests |
| `python-testing#integration` | `testcontainers`, `httpx asyncclient`, `respx`, `asgitransport` | Integration tests |
| `python-testing#unit` | `pytest-mock`, `mocker`, `autospec`, `freezegun` | Unit tests with mocks |
| `python-testing#property` | `hypothesis`, `property-based`, `@given` | Property-based testing |
| `python-testing#snapshot` | `syrupy`, `inline-snapshot` | Snapshot testing |
| `python-testing#async` | `pytest-asyncio`, `anyio backend` | Async tests |
| `python-testing#test-data` | `polyfactory`, `faker`, `test data builder` | Test data generation |
| `python-testing#ci` | `coverage`, `pytest-xdist`, `pytest-randomly`, `pytest-timeout`, `diff-cover` | CI gates, coverage |

### Team Orchestration

As the team lead, you have access to powerful tools for coordinating work across multiple agents. You NEVER write code directly - you orchestrate team members using these tools.

#### Task Management Tools

**TaskCreate** - Create tasks in the shared task list:
```typescript
TaskCreate({
  subject: "Implement user authentication",
  description: "Create login/logout endpoints with JWT tokens. See specs/auth-plan.md for details.",
  activeForm: "Implementing authentication"  // Shows in UI spinner when in_progress
})
// Returns: taskId (e.g., "1")
```

**TaskUpdate** - Update task status, assignment, or dependencies:
```typescript
TaskUpdate({
  taskId: "1",
  status: "in_progress",  // pending → in_progress → completed
  owner: "builder-auth"   // Assign to specific team member
})
```

**TaskList** - View all tasks and their status:
```typescript
TaskList({})
// Returns: Array of tasks with id, subject, status, owner, blockedBy
```

**TaskGet** - Get full details of a specific task:
```typescript
TaskGet({ taskId: "1" })
// Returns: Full task including description
```

#### Task Dependencies

Use `addBlockedBy` to create sequential dependencies - blocked tasks cannot start until dependencies complete:

```typescript
// Task 2 depends on Task 1
TaskUpdate({
  taskId: "2",
  addBlockedBy: ["1"]  // Task 2 blocked until Task 1 completes
})

// Task 3 depends on both Task 1 and Task 2
TaskUpdate({
  taskId: "3",
  addBlockedBy: ["1", "2"]
})
```

Dependency chain example:
```
Task 1: Setup foundation     → no dependencies
Task 2: Implement feature    → blockedBy: ["1"]
Task 3: Write tests          → blockedBy: ["2"]
Task 4: Final validation     → blockedBy: ["1", "2", "3"]
```

#### Owner Assignment

Assign tasks to specific team members for clear accountability:

```typescript
// Assign task to a specific builder
TaskUpdate({
  taskId: "1",
  owner: "builder-api"
})

// Team members check for their assignments
TaskList({})  // Filter by owner to find assigned work
```

#### Agent Deployment with Agent Tool

**Agent** — spawn a subagent to do work (formerly named `Task`; renamed in Claude Code 2.x):
```typescript
Agent({
  description: "Implement auth endpoints",
  prompt: "Implement the authentication endpoints as specified in Task 1...",
  subagent_type: "general-purpose",
  model: "opus",            // "opus" for complex reasoning, "sonnet" balanced, "haiku" for very simple
  run_in_background: false  // true for parallel execution
})
// Returns: agentId (e.g., "a1b2c3")
```

#### Resume Pattern (continue an existing agent)

The `Agent` tool no longer accepts a `resume` parameter. To continue a previously spawned agent with preserved context, use the `SendMessage` tool, passing the agent's id or name as `to`:

```typescript
// First deployment — fresh agent
Agent({
  description: "Build user service",
  prompt: "Create the user service with CRUD operations...",
  subagent_type: "general-purpose"
})
// Returns: agentId: "abc123"

// Later — resume SAME agent with full context preserved
SendMessage({
  to: "abc123",
  message: "Now add input validation to the endpoints you created..."
})
```

When to resume vs start fresh:
- **Resume (`SendMessage`)**: continuing related work, agent needs prior context
- **Fresh (`Agent`)**: unrelated task, clean slate preferred

#### Parallel Execution

Run multiple agents simultaneously with `run_in_background: true`:

```typescript
// Launch multiple agents in parallel
Agent({
  description: "Build API endpoints",
  prompt: "...",
  subagent_type: "general-purpose",
  run_in_background: true
})
// Returns immediately with agentId and an output_file path

Agent({
  description: "Build frontend components",
  prompt: "...",
  subagent_type: "general-purpose",
  run_in_background: true
})
// Both agents now working simultaneously
```

To monitor a background agent, prefer `Read` on the returned `output_file` path, or stream events with `Monitor`:

```typescript
// Non-blocking check — read accumulated output so far
Read({ file_path: "<output_file from Agent return>" })

// Stream events as they arrive (blocks per-event, exits on stop)
Monitor({ file_path: "<output_file>", pattern: "..." })
```

**Note:** `TaskOutput` is deprecated (Claude Code 2.1.91+) in favor of the Read/Monitor pattern above.

#### Orchestration Workflow

1. **Create tasks** with `TaskCreate` for each step in the plan
2. **Set dependencies** with `TaskUpdate` + `addBlockedBy`
3. **Assign owners** with `TaskUpdate` + `owner`
4. **Deploy agents** with `Agent` to execute assigned work
5. **Monitor progress** with `TaskList` (status) and `Read` on each agent's `output_file` (or `Monitor` to stream)
6. **Resume agents** with `SendMessage` + `to: <agentId>` for follow-up work
7. **Mark complete** with `TaskUpdate` + `status: "completed"`

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome. If Serena MCP tools are available, call `read_memory` and `list_memories` to check for existing knowledge about related features or past decisions.
2. **Explore OpenSpec (if available)** — Check if OpenSpec is initialized by running:
   ```bash
   openspec list --specs --json 2>/dev/null
   ```
   - If the command fails or returns empty → OpenSpec not installed/initialized. Skip with note: "OpenSpec not available — skipping spec exploration." Proceed directly to Interview Round 1.
   - If specs exist, extract keywords from USER_PROMPT and search for related specifications:
     ```bash
     openspec show <matching-spec> --json --requirements
     ```
   - Also check for active changes that might overlap:
     ```bash
     openspec list --changes --json 2>/dev/null
     ```
   - Summarize findings: related requirements (MUST/SHOULD/MAY), scenarios (Given/When/Then), active changes, and carry these into Interview Round 1. If existing specs define requirements for this domain, prepare questions about whether the new feature should MODIFY existing requirements or ADD alongside them.
3. **Clarify Requirements (Interview Round 1)** — If OpenSpec findings were produced in Step 2, incorporate them into your questions — ask about conflicts with existing requirements, whether to extend or modify existing specs, and whether historical design decisions still apply. Analyze the USER_PROMPT for ambiguities before reading the codebase. Ask when:
   - **Contradiction detected** — the prompt contains two statements that conflict or imply mutually exclusive approaches (e.g., "return 409" and "silently succeed" for the same case)
   - **Underspecified behavior** — the prompt describes a feature but not what happens in key user states (unauthorized, empty data, error). If the prompt says "user clicks heart" but doesn't say what unauthorized user sees — ask.
   - **Multiple valid approaches** — you see two or more reasonable ways to implement something, each with different tradeoffs. Present both with pros/cons and ask which one.
   - **Design/UX choices** — visual placement, copy text, interaction details that are matters of taste, not engineering (e.g., "badge next to text or on icon?", "what message for empty state?")
   - **Scope ambiguity** — it's unclear whether adjacent features are in or out of scope (e.g., "also update admin panel?", "include tests in this task?")
   - **Spec conflict** — OpenSpec findings reveal that the requested feature would modify, contradict, or overlap with existing living requirements. Ask the user how to reconcile.
   - Do NOT ask about things that have exactly one obvious answer from the prompt.
   - Do NOT ask about implementation details you can determine from the codebase — save those for step 5.
   - Use `AskUserQuestion` (supports 1-4 questions per call, call multiple times if needed).
4. Understand Codebase - Without subagents, directly understand existing patterns, architecture, and relevant files. **In addition to architecture, MUST analyze the test landscape of the project**: which test frameworks/libraries are present (read `pom.xml`/`build.gradle`/`pyproject.toml`/`package.json`); which test infrastructure (Testcontainers, H2, EmbeddedKafka, Playwright, Cypress, Selenide, fakeredis, respx, etc.) is already in use; which naming conventions identify integration vs. unit tests in this repo (`*IT.java`, `tests/integration/`, `*.e2e.spec.ts`, etc.); **which command actually runs the most realistic tests for this repo today** (Surefire vs. Failsafe vs. a custom Maven profile vs. `pytest -m integration` vs. `npx playwright test` vs. a Gradle task vs. a CI script). This information is the input to Step 4.5. If Serena MCP tools are available, prefer `find_symbol` and `get_symbols_overview` for navigating classes, methods, and dependencies instead of manual Glob/Grep. If Serena is not available, use Glob/Grep/Read as usual.
4.5. **Test Infra Interview (mandatory)** — On the basis of what you observed in Step 4, conduct a short interview with the user via `AskUserQuestion`. **This step runs every time** — never skip it.
   - **Q1 (always):** "The integration happy-path layer is mandatory. I see in the project: <observed test libs and conventions>. Which happy-path scenarios should the integration layer cover for this change, and what infrastructure should they use? (Suggest the infra you observed; if the project has Testcontainers, recommend it; if it only has H2/EmbeddedKafka, that is acceptable; otherwise propose adding what fits.)"
   - **Q2 (only if you observed any frontend in Step 4 — React/Vue/Angular/Svelte/Playwright/Cypress/Selenide):** "I detected <which frontend libs>. The E2E layer is optional. Should this change include an E2E happy-path? Options: enable + which runner; or skip — no UI changes in this change."
   - **Q3 (only if Q1 answer is ambiguous about scenarios):** "Which exact happy-path scenarios should integration cover? (To avoid 'one test for everything'.)"
   - Record the user's verbatim answers — they become the basis of the `## Test Infrastructure (User-Declared)` section in the plan, with assertions filled in by you (planner) on the basis of those answers (Files glob, Infra signature regex, scenario names, Runner command, Realism rationale).
   - The integration layer can never be `Skipped`/`Opted out`. If the user pushes back ("this is a refactor only"), explain that integration happy-path is still mandatory and ask which behavior the change preserves — that becomes the scenario.
5. **Clarify Implementation (Interview Round 2)** — Now that you know the codebase, check for implementation-specific ambiguities. Ask when:
   - **Multiple patterns exist** — the codebase has more than one way to solve this type of problem, and it's not clear which fits better (e.g., "CartService uses optimistic UI, OrderService uses server-confirmed — which pattern for favorites?"). Present both with pros/cons.
   - **Technical tradeoff with no clear winner** — both options are valid and the choice depends on priorities the user hasn't stated (e.g., "denormalized counter is faster but can drift vs. COUNT query is accurate but slower")
   - **Integration ambiguity** — the existing code can accommodate the new feature in more than one place or way (e.g., "add to existing DTO or create a new one?", "extend current controller or create separate?")
   - **Discovered edge case** — reading the code revealed a scenario the prompt didn't address (e.g., "the material can be soft-deleted — should favorites to deleted materials auto-remove?")
   - Do NOT ask about things where the codebase has exactly one established pattern — just follow it.
   - Skip this step entirely if every implementation choice has a single obvious answer from the code.
6. Design Solution - Develop technical approach including architecture decisions and implementation strategy
7. Define Testing Strategy + Test Infrastructure (User-Declared) - Plan the test pyramid: 80% unit tests, 15% integration/API tests, 5% UI e2e tests. Map each test to the source code it validates. Reference existing test patterns from the codebase. **Then fill in `## Test Infrastructure (User-Declared)`** based on the interview answers from Step 4.5: per stack, write `### Unit Layer (<stack>)`, `### Integration Layer (<stack>)`, and (if E2E enabled) `### E2E Layer (<stack>)` blocks with the machine-verifiable fields (Files glob, Infra signature, Happy-path scenarios, Runner command, Realism rationale). The Integration Layer block can never be `Skipped`. Multi-stack projects produce one block per stack per layer.
8. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `.claude/agents/team/*.md` or use `general-purpose`. Include test-builder members — one per layer (unit-tests, integration-tests, optional e2e-tests). Document in plan.
9. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments, and `**Tests**` field. **Test work MUST be split into per-layer tasks: `unit-tests` and `integration-tests` are mandatory; `e2e-tests` is required if the E2E layer is enabled in `## Test Infrastructure (User-Declared)`.** The single combined `write-tests` task is forbidden. Document in plan.
10. Generate Filename - Create a descriptive kebab-case filename based on the plan's main topic
11. Save Plan - Write the plan to `PLAN_OUTPUT_DIRECTORY/<filename>.md`
12. **Plan Review** — Run structural validation and architectural review on the saved plan. This ensures plan quality BEFORE OpenSpec artifacts are generated.

    **Structural check:**
    ```bash
    uv run --script .claude/hooks/validators/validate_plan.py --file <plan-path> --team-dir .claude/agents/team
    ```

    **Content review** (spawn plan-reviewer agent):
    ```
    Agent({
      subagent_type: "plan-reviewer",
      description: "Review plan before OpenSpec propose",
      prompt: "Review the plan at <plan-path>. Check all 8 criteria and return a structured verdict."
    })
    ```

    - If structural check fails or review verdict is **FAIL** → show issues, ask user to fix or abort. Do NOT proceed to Step 13.
    - If both pass → proceed to OpenSpec Propose.
13. **OpenSpec Propose (if available)** — If OpenSpec is initialized (Step 2 succeeded), create OpenSpec change artifacts from the reviewed plan.

    Run the following to check availability:
    ```bash
    openspec list --specs --json 2>/dev/null
    ```

    If available, provide the plan context to OpenSpec by referencing the saved plan:
    - The change name should match the plan filename (kebab-case)
    - Tell the user: "Plan review passed. Creating OpenSpec change artifacts..."
    - Execute `/openspec-propose` with context from the plan: task description, objective, solution approach, implementation phases, and step by step tasks
    - OpenSpec will create: `openspec/changes/<name>/` with proposal.md, specs/, design.md, tasks.md

    If OpenSpec is not available, skip with note: "OpenSpec not initialized — skipping artifact generation."
14. Report - Follow the `Report` section to provide a summary of key components
15. Record Knowledge (Serena only) - If Serena MCP tools are available, call `write_memory` with a summary of: what was planned, key architectural decisions, patterns chosen, and any tradeoffs resolved during interviews. Use the plan filename as memory name. If Serena is not available, skip this step.

## Plan Format

- IMPORTANT: Replace <requested content> with the requested content. It's been templated for you to replace. Consider it a micro prompt to replace the requested content.
- IMPORTANT: Anything that's NOT in <requested content> should be written EXACTLY as it appears in the format below.
- IMPORTANT: Follow this EXACT format when creating implementation plans:

```md
# Plan: <task name>

## Task Description
<describe the task in detail based on the prompt>

## Objective
<clearly state what will be accomplished when this plan is complete>

<if task_type is feature or complexity is medium/complex, include these sections:>
## Problem Statement
<clearly define the specific problem or opportunity this task addresses>

## Solution Approach
<describe the proposed solution approach and how it addresses the objective>
</if>

## Relevant Files
Use these files to complete the task:

<list files relevant to the task with bullet points explaining why. Include new files to be created under an h3 'New Files' section if needed>

<if complexity is medium/complex, include this section:>
## Implementation Phases
### Phase 1: Foundation
<describe any foundational work needed>

### Phase 2: Core Implementation
<describe the main implementation work>

### Phase 3: Integration & Polish
<describe integration, testing, and final touches>
</if>

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
<list the team members you'll use to execute the plan>

- Builder
  - Name: <unique name for this builder - this allows you and other team members to reference THIS builder by name. Take note there may be multiple builders, the name make them unique.>
  - Role: <the single role and focus of this builder will play>
  - Agent Type: <the subagent type of this builder, you'll specify based on the name in TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
  - Resume: <default true. This lets the agent continue working with the same context. Pass false if you want to start fresh with a new context.>
- <continue with additional team members as needed in the same format as above>

## Testing Strategy

Test pyramid ratio: **80% unit / 15% integration-API / 5% UI e2e**

### Unit Tests (80%)
<list unit tests to write: service logic, utility functions, component rendering, hooks. Each test class mirroring a source class.>

### Integration / API Tests (15%)
<list integration tests: controller endpoints with MockMvc/@WebMvcTest, repository tests with @DataJpaTest/Testcontainers, API contract tests.>

### UI E2E Tests (5%)
<list critical user flows to cover with e2e tests: login + action, full CRUD flow, cross-page navigation. Use Selenide/Playwright/Cypress as per project.>

## Test Infrastructure (User-Declared)

This section is the machine-verifiable contract that `check_test_layers.py` and the `validator` agent enforce after build. Every field must be filled from the Test Infra Interview answers (Workflow Step 4.5). Multi-stack projects produce one block per stack per layer.

### Unit Layer (<stack name, e.g. Java | Python | React>)
- **Files glob:** `<glob pattern locating unit test files in this repo, e.g. src/test/java/**/*Test.java>`
- **Infra signature (regex, optional for unit):** `<regex that proves these are unit tests, or "n/a">`
- **Happy-path scenarios (≥1 named):**
  - `<ClassName#methodName or describe>it or path/to/test::test_name>`
- **Runner command:** `<exact command this repo uses to run these unit tests, e.g. mvn test>`
- **Realism rationale:** `<one sentence: why this is the appropriate unit-level setup for this repo>`

### Integration Layer (<stack name>)  — MANDATORY, never Skipped
- **Files glob:** `<glob locating integration test files, e.g. src/test/java/**/*IT.java | tests/integration/**/*.py>`
- **Infra signature (regex, ≥1 match per file):** `<regex proving the user-chosen infra is actually used, e.g. @Testcontainers|import org\.testcontainers — or @EmbeddedKafka — or import org\.springframework\.boot\.test\.context\.SpringBootTest with H2>`
- **Happy-path scenarios (≥1 named):**
  - `<ClassName#methodName | describe>it | path::test_name — one per affected user-facing endpoint or use-case>`
- **Runner command:** `<the command that actually runs these tests in this repo — surefire/failsafe/pytest -m integration/custom — whatever the repo really uses>`
- **Realism rationale:** `<one sentence: why these are the most realistic tests this repo can run today (e.g. "Testcontainers PostgreSQL is the real DB the prod uses; failsafe is wired in pom; this is the highest realism tier available")>`

### E2E Layer (<stack name>)  — optional; required only if frontend detected
- **Status:** `<Enabled | Skipped — no UI changes in this change | Skipped — no frontend in this project>`
- *(if Enabled, fill the same five fields: Files glob, Infra signature, Happy-path scenarios, Runner command, Realism rationale)*

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

<list step by step tasks as h3 headers. Start with foundational work, then core implementation, then testing, then validation.>

### 1. <First Task Name>
- **Task ID**: <unique kebab-case identifier, e.g., "setup-database">
- **Depends On**: <Task ID(s) this depends on, or "none" if no dependencies>
- **Assigned To**: <team member name from Team Members section>
- **Agent Type**: <subagent from TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
- **Stack**: <technology keywords for context routing, e.g., "Java Spring Boot JPA", "React Next.js", "Python FastAPI pytest">
- **Parallel**: <true if can run alongside other tasks, false if must be sequential>
- **Tests**: <what test coverage this task's code needs from Testing Strategy, e.g., "Unit: FavoriteServiceTest — add/remove/check. Integration: FavoriteControllerTest — all endpoints.">
- <specific action to complete>
- <specific action to complete>

### 2. <Second Task Name>
- **Task ID**: <unique-id>
- **Depends On**: <previous Task ID, e.g., "setup-database">
- **Assigned To**: <team member name>
- **Agent Type**: <subagent type from TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
- **Stack**: <technology keywords for context routing>
- **Parallel**: <true/false>
- **Tests**: <what test coverage this task's code needs>
- <specific action>
- <specific action>

### 3. <Continue Pattern>

### N-3. <Write Unit Tests>
- **Task ID**: unit-tests
- **Depends On**: <all implementation task IDs>
- **Assigned To**: <test-builder team member>
- **Agent Type**: builder
- **Stack**: <unit-testing keywords, e.g., "Java JUnit Mockito assertj test structure" or "Python pytest pytest-mock unit" or "React jest testing-library tsx unit">
- **Parallel**: <true if integration/e2e tests don't share fixtures>
- Write unit tests (80%) as defined in Testing Strategy and `### Unit Layer (<stack>)` block
- Cover service logic, utility functions, component rendering, hooks
- Follow project test patterns (reference existing test files from Relevant Files)

### N-2. <Write Integration Tests>  — MANDATORY
- **Task ID**: integration-tests
- **Depends On**: <all implementation task IDs>
- **Assigned To**: <test-builder team member>
- **Agent Type**: builder
- **Stack**: <integration-testing keywords, e.g., "Java MockMvc Testcontainers integration test failsafe" or "Python pytest testcontainers httpx asyncclient integration" or "Java MockMvc h2 integration test" — pick keywords matching the user-declared infra in `### Integration Layer (<stack>)`>
- **Parallel**: false
- Write integration/API tests (15%) — **happy-path scenarios from `### Integration Layer (<stack>)` are mandatory**
- Use the exact infra declared in `### Integration Layer (<stack>)` (Testcontainers / EmbeddedKafka / H2 / fakeredis / etc. — whatever the user picked)
- Test method names should match the scenarios listed in the User-Declared block so `check_test_layers.py` can find them by fuzzy grep

### N-1. <Write E2E Tests>  — only if E2E layer is Enabled
- **Task ID**: e2e-tests
- **Depends On**: <all implementation task IDs>
- **Assigned To**: <test-builder team member>
- **Agent Type**: builder
- **Stack**: <e2e-testing keywords, e.g., "Java Selenide e2e page object" or "React Playwright e2e" or "Cypress e2e">
- **Parallel**: false
- Skip this task entirely if `### E2E Layer (<stack>)` is `Skipped` in `## Test Infrastructure (User-Declared)`
- Write UI e2e tests (5%) for the happy-path scenarios declared in `### E2E Layer (<stack>)`
- Use the runner declared in the `Runner command` field of that block

### N. <Final Validation Task>
- **Task ID**: validate-all
- **Depends On**: <all previous Task IDs including unit-tests, integration-tests, and e2e-tests if enabled>
- **Assigned To**: <validator team member>
- **Agent Type**: <validator agent>
- **Stack**: <full stack keywords for validation>
- **Parallel**: false
- Run all validation commands
- For each non-Skipped layer in `## Test Infrastructure (User-Declared)`, execute the declared `Runner command` verbatim and verify that **tests actually ran** (parse runner output for "Tests run: N" / "N passed" / Playwright JSON reporter — N must be ≥ number of declared scenarios for that layer)
- Run `check_test_layers.py` post-build hook (already covered by `/smart_build` Step 5.5, but verify here too)
- Verify acceptance criteria met

<continue with additional tasks as needed. Agent types must exist in .claude/agents/team/*.md>

## Acceptance Criteria
<list specific, measurable criteria that must be met for the task to be considered complete>

## Validation Commands
Execute these commands to validate the task is complete:

<list specific commands to validate the work. Be precise about what to run>
- Example: `uv run python -m py_compile apps/*.py` - Test to ensure the code compiles

## Notes
<optional additional context, considerations, or dependencies. If new libraries are needed, specify using `uv add`>
```

## Report

After creating and saving the implementation plan, provide a concise report with the following format:

```
✅ Implementation Plan Created

File: PLAN_OUTPUT_DIRECTORY/<filename>.md
Topic: <brief description of what the plan covers>
Key Components:
- <main component 1>
- <main component 2>
- <main component 3>

Team Task List:
- <list of tasks, and owner (concise)>

Team members:
- <list of team members and their roles (concise)>

OpenSpec Change: openspec/changes/<name>/ (if created)

When you're ready, you can execute the plan in a new agent by running:
/smart_build <replace with path to plan>
```
