# Testing Strategy

Every plan created by `/plan_w_team` includes a mandatory testing strategy following the **80/15/5 test pyramid**.

## Test Pyramid

```
         ┌─────────┐
         │  UI E2E │  5%   — critical user flows only
         │  (5%)   │
         ├─────────┤
         │  Integ  │  15%  — API endpoints, DB queries, Kafka
         │  (15%)  │
         ├─────────┤
         │         │
         │  Unit   │  80%  — service logic, utils, components
         │  (80%)  │
         └─────────┘
```

| Layer | Ratio | What to test | Tools |
|-------|-------|-------------|-------|
| **Unit** | 80% | Service logic, utility functions, component rendering, hooks | JUnit + AssertJ, Jest, Pytest |
| **Integration / API** | 15% | Controller endpoints (MockMvc), repository tests (Testcontainers), API contracts | @WebMvcTest, @DataJpaTest, httpx |
| **UI E2E** | 5% | Login + action, full CRUD flow, cross-page navigation | Selenide, Playwright, Cypress |

## How It's Enforced

1. **Plan creation** — `/plan_w_team` requires a `## Testing Strategy` section with all three layers
2. **Stack keywords** — each task includes test-specific keywords (`mockito`, `mockmvc`, `pytest`) for [context routing](context-routing.md)
3. **Dedicated task** — a `write-tests` task always precedes `validate-all` in the step-by-step tasks
4. **Per-task coverage** — every implementation task has a `**Tests**` field specifying what test coverage it requires
5. **Stop hook** — `validate_file_contains.py` rejects plans missing `## Testing Strategy`

## Plan Format

```markdown
## Testing Strategy

Test pyramid ratio: **80% unit / 15% integration-API / 5% UI e2e**

### Unit Tests (80%)
- FavoriteServiceTest — add/remove/check logic
- FavoriteMapperTest — DTO mapping

### Integration / API Tests (15%)
- FavoriteControllerTest — MockMvc for all endpoints
- FavoriteRepositoryTest — @DataJpaTest with Testcontainers

### UI E2E Tests (5%)
- Login → add favorite → verify in list → remove
```

## Task Example

```markdown
### 5. Write Tests
- **Task ID**: write-tests
- **Depends On**: all implementation task IDs
- **Stack**: Java MockMvc Mockito assertj allure test structure
- **Tests**: Unit: FavoriteServiceTest. Integration: FavoriteControllerTest.
```

## Key Files

- `.claude/commands/plan_w_team.md` — testing strategy requirement in plan format
- `.claude/hooks/validators/validate_file_contains.py` — Stop hook enforcing `## Testing Strategy` section
