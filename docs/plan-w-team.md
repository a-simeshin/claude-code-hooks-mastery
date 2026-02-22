# Plan With Team

`/plan_w_team` generates implementation plans for multi-agent execution. It analyzes requirements, interviews the user, reads the codebase, and produces a spec document that `/smart_build` can execute with a team of builder agents.

## Workflow

```mermaid
flowchart TD
    A["1. Analyze requirements"] --> B["2. Clarify requirements<br/>(AskUserQuestion)"]
    B --> C["3. Read codebase"]
    C --> D["4. Clarify implementation<br/>(AskUserQuestion)"]
    D --> E["5. Design solution"]
    E --> F["6. Define team & tasks"]
    F --> G["7. Save plan to specs/"]
    G --> H["validate_plan.py<br/>(7 structural checks)"]
    H -->|FAIL| G
    H -->|PASS| I["Ready for /smart_build"]
```

## Two-Round Requirements Interview

Before designing a solution, the planner asks clarifying questions in two rounds.

### Round 1: After Analyzing Requirements

Questions about ambiguities in the user's request — before reading any code:

- **Mutually exclusive approaches** — "Should duplicate favorites return 409 or silently succeed?"
- **Missing behavior specs** — "What should unauthenticated users see when clicking the heart?"
- **Scope boundaries** — "Should the admin panel also display favorite counts?"
- **Priority tradeoffs** — "Optimize for simplicity or for performance at scale?"

### Round 2: After Reading the Codebase

Questions about implementation choices visible from the code:

- **Pattern selection** — "The codebase has both CartService (optimistic) and OrderService (pessimistic) patterns — which to mirror?"
- **Technical tradeoffs** — "Denormalized counter vs COUNT query — the codebase uses both, which fits here?"
- **Edge cases from code** — "SecurityConfig has a catch-all rule — add explicit matcher for consistency, or rely on the catch-all?"

The number of questions scales with complexity. Simple fixes need 0 questions. Complex features may need 3-5 per round.

## Section Routing Catalog

Every task in a plan has a `**Stack**` field — keywords that tell the [context router](context-routing.md) which coding standards to load for the builder.

The planner picks keywords from a catalog embedded in its prompt:

| Section | Trigger keywords | Add when task involves |
|---------|-----------------|----------------------|
| **Java** | | |
| `java-patterns#basics` | `java`, `spring`, `controller`, `entity`, `jpa` | Any Java/Spring Boot code |
| `java-patterns#errors` | `exception`, `error handling`, `controlleradvice` | Exception handling, HTTP errors |
| `java-patterns#java17` | `record`, `pattern matching`, `switch expression` | Java 17 features |
| `java-patterns#java21` | `virtual thread`, `sequenced collection` | Java 21 features |
| **Java Testing** | | |
| `java-testing#structure` | `assertj`, `allure`, `test naming`, `test structure` | Test organization, Allure annotations |
| `java-testing#integration` | `testcontainers`, `integration test`, `podman` | Integration tests with containers |
| `java-testing#http` | `mockmvc`, `resttemplate`, `http test` | REST endpoint testing |
| `java-testing#kafka` | `kafka test`, `consumer test`, `producer test` | Kafka testing |
| `java-testing#jdbc` | `database test`, `repository test`, `jdbc test` | Database testing |
| `java-testing#mockito` | `mockito`, `spy` | Unit tests with mocking |
| `java-testing#e2e` | `selenide`, `e2e`, `page object` | E2E browser testing |
| `java-testing#maven` | `surefire`, `failsafe`, `jacoco` | Maven test plugins, coverage |
| **React** | | |
| `react-patterns#core` | `react`, `component`, `hook`, `useState`, `useEffect`, `tsx` | Any React code |
| `react-patterns#nextjs` | `next.js`, `server component`, `app router` | Next.js App Router |
| `react-patterns#vite` | `vite`, `react-router`, `code splitting` | Vite, React Router |
| **Python** | | |
| `python-patterns#core` | `python`, `typing`, `dataclass`, `asyncio` | Any Python code |
| `python-patterns#fastapi` | `fastapi`, `pydantic`, `apirouter`, `depends` | FastAPI endpoints |
| `python-patterns#testing` | `pytest`, `fixture`, `parametrize`, `conftest` | Python testing |

The Stack field combines stack keywords (selects the stack) with section keywords (selects specific sections):

```
Stack: "Java Spring Boot controller exception error handling"
         ↓ stack keywords            ↓ section keywords
     java-patterns#basics      java-patterns#errors
```

## Stack Validation (Check 7)

The plan validator runs Check 7 on every task — imports `context_router.route()` and verifies the Stack field produces sections:

```python
result = route_fn(stack)
if not result.get("sections"):
    errors.append(f"Stack doesn't match any routing keywords")
```

Two failure modes caught:
- **Missing Stack** — task has no `**Stack**` field at all
- **Dead keywords** — Stack contains words that don't trigger any section

A plan with broken routing is rejected at validation, not discovered during build.

## Plan Format

The generated plan includes these sections:

| Section | Content |
|---------|---------|
| Task Description | What needs to be done |
| Objective | What "done" looks like |
| Problem Statement | Why this work is needed *(medium/complex tasks)* |
| Solution Approach | How the objective will be achieved *(medium/complex tasks)* |
| Relevant Files | Existing files to modify + new files to create |
| Implementation Phases | Foundation → Core → Integration *(medium/complex tasks)* |
| Team Orchestration | Team members with roles and agent types |
| Step by Step Tasks | Ordered tasks with IDs, dependencies, Stack, assignments |
| Acceptance Criteria | Measurable completion conditions |
| Validation Commands | Shell commands to verify the work |

## Research

| Research | Direct relevance |
|----------|-----------------|
| [ClarifyGPT](https://dl.acm.org/doi/10.1145/3660810) (FSE 2024) | Asking clarifying questions before code generation: GPT-4 Pass@1 +9.84pp. Validates two-round interview. |
| [TiCoder](https://arxiv.org/abs/2404.10100) (ICSE 2024, Microsoft) | Interactive intent clarification: +45.97pp Pass@1 within 5 interactions. |
| [SpecFix](https://arxiv.org/abs/2505.07270) (ASE 2025) | Repairing ambiguous specs before generation: +30.9% Pass@1. Transfers across models. |

## Key Files

- `.claude/commands/plan_w_team.md` — planner prompt with workflow, catalog, and plan format
- `.claude/hooks/validators/validate_plan.py` — structural validator (7 checks including Stack)
- `.claude/hooks/context_router.py` — keyword router that Stack fields feed into
- `.claude/refs/*.md` — reference files with coding standards sections
