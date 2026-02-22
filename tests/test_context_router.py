#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Benchmark test for context_router.py against 80 realistic coding tasks.

Checks:
1. Stack precision — router loads sections from the correct stack(s)
2. Section recall — expected sections are present in the output
3. No false positives — irrelevant stacks are NOT loaded
4. Edge cases — empty tasks, docs-only tasks, ambiguous tasks

Usage:
  uv run --script tests/test_context_router.py
"""
import json
import os
import sys

# Add project root to path so we can import context_router
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "hooks"))
from context_router import route

BENCHMARK = [
    {"task": "Add a GET /api/users/{id} endpoint in UserController that returns 404 with a proper ErrorResponse body when the user is not found in the database.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
    {"task": "Implement a POST /api/orders endpoint that accepts a validated OrderDto, delegates to OrderService, and returns 201 Created. The service should throw ConflictException if an order already exists for the same idempotency key.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
    {"task": "Create a JPA entity Product with fields id, name, price, and stock quantity. Use Lombok annotations to eliminate boilerplate and add a Spring Data JPA repository.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "Write a GlobalExceptionHandler using @RestControllerAdvice that maps NotFoundException to 404, ConflictException to 409, and IllegalArgumentException to 400.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#errors"]},
    {"task": "Refactor OrderService.createOrder() to use Spring Assert for fail-fast validation of all input parameters.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "Replace all DTO classes that use Lombok @Value with Java 17 records. Add compact constructors for validation.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#java17"]},
    {"task": "Implement a PATCH /api/orders/{id}/cancel endpoint. The service layer must throw ConflictException if the order status is SHIPPED.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
    {"task": "Add a @ConfigurationProperties class for our external payment gateway with baseUrl, timeout, maxRetries, apiKey.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "Migrate all switch statements in the order processing pipeline to switch expressions using Java 14+ arrow syntax.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#java17"]},
    {"task": "Write integration tests for the POST /api/orders endpoint using TestRestTemplate and Testcontainers (PostgreSQL). Cover: happy path 201, empty items 400, duplicate 409.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#integration", "java-testing#http"]},
    {"task": "Add a Kafka integration test that verifies an ORDER_CREATED event is published to the orders.events topic after a successful POST /api/orders call.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#kafka", "java-testing#integration"]},
    {"task": "Create a BaseIntegrationTest abstract class that starts PostgreSQL and Kafka via Testcontainers using @ServiceConnection.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#integration"]},
    {"task": "Write unit tests for OrderService.cancel() edge cases using Mockito: concurrent OptimisticLockingFailureException triggers retry.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#mockito"]},
    {"task": "Write a JDBC integration test for OrderRepository.findByCustomerId() that seeds three orders for two customers.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#jdbc", "java-testing#integration"]},
    {"task": "Add a WireMock test for the payment gateway client: verify 200 updates order to PAID, 500 returns 502, 5-second delay returns 504.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#wiremock"]},
    {"task": "Set up Allure annotations (@Epic, @Feature, @Story, @Severity, @Step) across all integration test classes for the Orders domain.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#structure"]},
    {"task": "Configure the Maven Failsafe plugin inside an integration-tests profile so that *IT.java tests run during mvn verify with JaCoCo instrumentation.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#maven"]},
    {"task": "Create a reusable TestDataBuilders class with static factory methods for CreateOrderRequest, Order, and OrderItem.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#structure"]},
    {"task": "Enable virtual threads for all Spring Boot HTTP handling by setting spring.threads.virtual.enabled=true and verify with an integration test.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#java21", "java-testing#integration"]},
    {"task": "Build a React UserProfile component that fetches user data by ID. Extract all fetch logic into a useUser custom hook with AbortController cleanup.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Convert the RegistrationForm component from multiple useState calls to a useReducer with typed actions.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Add an ErrorBoundary component wrapping the Dashboard and Sidebar sections of the app.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Implement code splitting for all route-level pages using React.lazy() and wrap the router outlet with Suspense.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Set up a ThemeContext with useTheme hook to eliminate prop drilling of the theme through Layout, Header, and ThemeToggle.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Migrate the app from JSX-based BrowserRouter to createBrowserRouter with data loaders for the posts list route.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#vite"]},
    {"task": "Configure path aliases (@/) in both vite.config.ts and tsconfig.json, then replace all relative imports.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#vite"]},
    {"task": "Add a Vite dev proxy so all /api requests are forwarded to http://localhost:8080.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#vite"]},
    {"task": "Add a Next.js App Router page for /dashboard that is a Server Component fetching stats directly from the database, with loading.tsx and error.tsx.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Convert the post creation flow from a REST fetch inside a 'use client' component to a Server Action that revalidates /posts.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Add generateMetadata to the /posts/[slug]/page.tsx dynamic route for proper title and OpenGraph tags.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Write a Next.js middleware.ts that redirects unauthenticated users from /dashboard/* to /login.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Add generateStaticParams to /posts/[slug]/page.tsx so all known post slugs are pre-rendered at build time.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Add a manualChunks configuration to vite.config.ts to split vendor-react, vendor-router, vendor-charts into separate chunks.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#vite"]},
    {"task": "Implement a FastAPI POST /orders endpoint with a Pydantic v2 OrderCreate model that validates items are non-empty.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi", "python-patterns#core"]},
    {"task": "Add a FastAPI dependency get_order_service() that injects an AsyncSession via Depends(get_db).", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Add a global @app.exception_handler for AppError that returns JSON with code and message fields.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi", "python-patterns#core"]},
    {"task": "Write a Pydantic v2 model DateRangeFilter with a model_validator ensuring end_date is after start_date.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Replace deprecated @app.on_event('startup') with a lifespan async context manager for SQLAlchemy engine init.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Move the email send from inside POST /orders to a BackgroundTasks call so the client gets 201 immediately.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Create a pydantic-settings Settings class with database_url and secret_key, exposed via lru_cache get_settings().", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Add query parameter validation to GET /products/search: q min_length=2, page ge=1, page_size max 100.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "Split monolithic main.py with 60+ endpoints into separate APIRouter modules per domain (users, orders, payments).", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi", "python-patterns#core"]},
    {"task": "Add type hints to all functions in the order pipeline, replace dict-based structures with frozen dataclasses, add StrEnum for order status.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core"]},
    {"task": "Refactor get_dashboard() to use asyncio.gather() instead of three sequential awaits.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core"]},
    {"task": "Write pytest integration tests for POST /users using httpx AsyncClient covering: 201 happy path, 409 duplicate, 422 missing field.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    {"task": "Add a @pytest.mark.parametrize test for validate_email() covering 7 cases with descriptive ids.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    {"task": "Create make_user and make_order factory fixtures with sensible defaults, refactor all tests to use them.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    {"task": "Set up conftest.py with session-scoped db_engine, function-scoped db_session with transaction rollback, and async AsyncClient fixture.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    {"task": "Add pytest markers (slow, integration, e2e) to all test files and register them in pyproject.toml.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    # Cross-stack
    {"task": "Implement a full-stack feature: a React form (Next.js Server Action) to create a new product that calls a Spring Boot POST /api/products endpoint backed by a JPA entity and a Kafka event.", "expected_stacks": ["react-patterns", "java-patterns"], "expected_sections": ["react-patterns#nextjs", "java-patterns#basics"]},
    {"task": "Build a user registration flow: React form posts to a FastAPI POST /users endpoint with Pydantic validation; on success redirect to /dashboard using Next.js.", "expected_stacks": ["react-patterns", "python-patterns"], "expected_sections": ["react-patterns#core", "python-patterns#fastapi"]},
    {"task": "Add an order history page: Next.js Server Component fetches from Spring Boot GET /api/orders?userId={id} with pagination.", "expected_stacks": ["react-patterns", "java-patterns"], "expected_sections": ["react-patterns#nextjs", "java-patterns#basics"]},
    {"task": "Implement a real-time notification badge: React useEffect subscribes to a WebSocket endpoint served by FastAPI.", "expected_stacks": ["react-patterns", "python-patterns"], "expected_sections": ["react-patterns#core", "python-patterns#fastapi"]},
    {"task": "Wire up a full search feature: Vite React frontend debounces user input and calls GET /api/search on the Spring Boot backend with integration tests.", "expected_stacks": ["react-patterns", "java-patterns"], "expected_sections": ["react-patterns#vite", "java-patterns#basics"]},
    # Edge cases
    {"task": "Fix the typo in the error message — it says 'ordder' instead of 'order'. Fix in OrderService and update the test assertion.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#errors"]},
    {"task": "Rename usrId to userId everywhere in UserController method signature, body, and logs.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "Update the README to describe how to run integration tests with Podman.", "expected_stacks": [], "expected_sections": []},
    {"task": "Refactor ProductService — it has 4 levels of nesting. Extract inner logic into private methods.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "The checkout button sometimes does nothing. Investigate if onClick is being re-created on every render causing memoized child to skip updates.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "The /reports endpoint is slow. Profile and check if sequential awaits can be parallelised with asyncio.gather.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core"]},
    {"task": "The integration test suite fails on M1 because Testcontainers pulls the wrong Selenium image. Fix BaseE2ETest to detect OS architecture.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#e2e"]},
    {"task": "Add a CORS middleware to the FastAPI app permitting https://app.example.com as origin.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
    {"task": "The UserCard component re-renders on every parent render. Wrap with React.memo and stabilise onSelect with useCallback.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "A useEffect fetching comments has no cleanup. Add AbortController to prevent state update on unmounted component.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Add E2E Selenide tests for the catalog page: verify page loads with product cards, search filters correctly, clicking opens detail.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#e2e"]},
    {"task": "The DataGrid filters 50,000 rows on every render. Memoize with useMemo using only primitive filter values as deps.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#core"]},
    {"task": "Add VITE_ prefixed environment variables for API_URL and FEATURE_FLAGS with proper env.d.ts typing.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#vite"]},
    {"task": "A Kafka consumer test is flaky because it uses Thread.sleep(5000). Replace with Awaitility.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#kafka"]},
    {"task": "Create a Page Object for the checkout page in the Selenide E2E suite with @Step annotations for Allure.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#e2e"]},
    {"task": "Refactor all os.path calls to use pathlib.Path and path.read_text() / path.write_text().", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core"]},
    {"task": "Implement a Protocol-based NotificationSender interface that EmailSender and SmsSender satisfy structurally. Add a unit test with a mock.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core", "python-patterns#testing"]},
    {"task": "Add an async integration test firing 5 concurrent GET /users/{id} using anyio task groups, assert all return 200.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
    {"task": "Coverage shows OrderService at 64%. Add Mockito tests for null input, negative price, notification service down.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#mockito"]},
    {"task": "Replace all var usages in the service layer with explicit types to comply with code standards.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
    {"task": "Add pattern matching for instanceof to the polymorphic event handler, replacing explicit casts with Java 16+ syntax.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#java17"]},
    {"task": "Remove mutable static List<Order> cache in OrderService causing data leaks between tests. Replace with instance-level dependency.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-testing#structure"]},
    {"task": "Update multi-line SQL queries in OrderRepository from concatenated strings to Java text blocks.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#java17"]},
    {"task": "Replace all <Head> from next/head with App Router Metadata API (export const metadata or generateMetadata).", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Migrate route handler at app/api/posts/route.ts to Server Actions with 'use server' and revalidatePath.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
    {"task": "Add structlog-based RequestLoggingMiddleware to FastAPI that logs method, path, status_code, elapsed_ms.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi", "python-patterns#core"]},
    {"task": "Coverage for Python order service is at 71%. Add pytest tests for NotFoundError, ConflictError, and ValidationError branches.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing", "python-patterns#core"]},
]


def extract_stacks(sections: list[str]) -> set[str]:
    """Extract stack prefixes from section IDs."""
    return {s.split("#")[0] for s in sections}


def run_benchmark():
    total = len(BENCHMARK)
    stack_correct = 0
    section_hits = 0
    section_total = 0
    no_false_positives = 0
    failures = []

    for i, case in enumerate(BENCHMARK):
        result = route(case["task"])
        actual_sections = set(result["sections"])
        actual_stacks = extract_stacks(actual_sections)
        expected_stacks = set(case["expected_stacks"])
        expected_sections = set(case["expected_sections"])

        # Metric 1: Stack precision — correct stacks loaded
        stack_ok = expected_stacks.issubset(actual_stacks)
        if stack_ok:
            stack_correct += 1

        # Metric 2: Section recall — expected sections present
        hits = len(expected_sections & actual_sections)
        section_hits += hits
        section_total += len(expected_sections) if expected_sections else 0

        # Metric 3: No false positive stacks
        if expected_stacks:
            extra_stacks = actual_stacks - expected_stacks
            fp_ok = len(extra_stacks) == 0
        else:
            # Docs/edge case — should return empty or minimal
            fp_ok = True
        if fp_ok:
            no_false_positives += 1

        # Track failures
        if not stack_ok or hits < len(expected_sections):
            missing = expected_sections - actual_sections
            extra = actual_stacks - expected_stacks if expected_stacks else set()
            failures.append({
                "index": i + 1,
                "task": case["task"][:80] + "..." if len(case["task"]) > 80 else case["task"],
                "expected_sections": sorted(expected_sections),
                "actual_sections": sorted(actual_sections),
                "missing_sections": sorted(missing),
                "extra_stacks": sorted(extra),
            })

    # Print results
    section_recall = (section_hits / section_total * 100) if section_total else 100
    stack_precision = stack_correct / total * 100
    fp_rate = no_false_positives / total * 100

    print("=" * 70)
    print(f"CONTEXT ROUTER BENCHMARK — {total} tasks")
    print("=" * 70)
    print()
    print(f"  Stack Precision (correct stacks loaded):  {stack_correct}/{total}  ({stack_precision:.1f}%)")
    print(f"  Section Recall  (expected sections hit):  {section_hits}/{section_total}  ({section_recall:.1f}%)")
    print(f"  No False Positives (no extra stacks):     {no_false_positives}/{total}  ({fp_rate:.1f}%)")
    print()

    if failures:
        print(f"FAILURES ({len(failures)}):")
        print("-" * 70)
        for f in failures:
            print(f"  #{f['index']}: {f['task']}")
            if f["missing_sections"]:
                print(f"    MISSING: {f['missing_sections']}")
            if f["extra_stacks"]:
                print(f"    EXTRA STACKS: {f['extra_stacks']}")
            print(f"    GOT: {f['actual_sections']}")
            print()
    else:
        print("ALL TASKS PASSED!")

    print("=" * 70)
    return len(failures) == 0


def run_with_stack_prefix():
    """Re-run only the 18 failed tasks with Stack prefix prepended (simulating plan_w_team output)."""
    # These are the tasks that failed without Stack prefix, now with Stack: prefix added
    tasks_with_prefix = [
        {"task": "Stack: Java Spring Boot. Add a GET /api/users/{id} endpoint in UserController that returns 404 with a proper ErrorResponse body.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
        {"task": "Stack: Java Spring Boot. Implement a POST /api/orders endpoint that accepts a validated OrderDto, delegates to OrderService.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
        {"task": "Stack: Java Spring Boot. Implement a PATCH /api/orders/{id}/cancel endpoint. The service layer must throw ConflictException if SHIPPED.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics", "java-patterns#errors"]},
        {"task": "Stack: Java Spring Boot. Add a @ConfigurationProperties class for our external payment gateway with baseUrl, timeout, maxRetries.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
        {"task": "Stack: Java Kafka Testcontainers. Add a Kafka integration test that verifies an ORDER_CREATED event is published after a successful POST.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#kafka", "java-testing#integration"]},
        {"task": "Stack: Java JPA JDBC Testcontainers. Write a JDBC integration test for OrderRepository.findByCustomerId().", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#jdbc", "java-testing#integration"]},
        {"task": "Stack: Java testing. Create a reusable TestDataBuilders class with static factory methods for CreateOrderRequest and Order.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#structure"]},
        {"task": "Stack: React Next.js. Add generateStaticParams to /posts/[slug]/page.tsx so all known post slugs are pre-rendered.", "expected_stacks": ["react-patterns"], "expected_sections": ["react-patterns#nextjs"]},
        {"task": "Stack: Python FastAPI Pydantic. Add a global @app.exception_handler for AppError returning JSON with code and message.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core", "python-patterns#fastapi"]},
        {"task": "Stack: Python FastAPI. Add query parameter validation to GET /products/search: q min_length=2, page ge=1, page_size max 100.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#fastapi"]},
        {"task": "Stack: Java Spring Boot. Fix the typo in the error message — it says 'ordder' instead of 'order'. Fix in OrderService.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#errors"]},
        {"task": "Stack: Java Spring Boot. Refactor ProductService — it has 4 levels of nesting. Extract inner logic into private methods.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
        {"task": "Stack: Java Kafka testing. A Kafka consumer test is flaky because it uses Thread.sleep(5000). Replace with Awaitility.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#kafka"]},
        {"task": "Stack: Python pytest. Implement a Protocol-based NotificationSender interface. Add a unit test with a mock.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#core", "python-patterns#testing"]},
        {"task": "Stack: Python FastAPI pytest. Add an async integration test firing 5 concurrent GET /users/{id} using anyio task groups.", "expected_stacks": ["python-patterns"], "expected_sections": ["python-patterns#testing"]},
        {"task": "Stack: Java Mockito testing. Coverage shows OrderService at 64%. Add Mockito tests for null input, negative price.", "expected_stacks": ["java-testing"], "expected_sections": ["java-testing#mockito"]},
        {"task": "Stack: Java Spring Boot. Replace all var usages in the service layer with explicit types to comply with code standards.", "expected_stacks": ["java-patterns"], "expected_sections": ["java-patterns#basics"]},
        {"task": "Stack: Java Spring Boot testing. Remove mutable static List<Order> cache in OrderService causing data leaks between tests.", "expected_stacks": ["java-patterns", "java-testing"], "expected_sections": ["java-patterns#basics", "java-testing#structure"]},
    ]

    total = len(tasks_with_prefix)
    fixed = 0
    still_broken = []

    for i, case in enumerate(tasks_with_prefix):
        result = route(case["task"])
        actual_sections = set(result["sections"])
        actual_stacks = extract_stacks(actual_sections)
        expected_stacks = set(case["expected_stacks"])
        expected_sections = set(case["expected_sections"])

        stack_ok = expected_stacks.issubset(actual_stacks)
        hits = len(expected_sections & actual_sections)
        all_ok = stack_ok and hits == len(expected_sections)

        if all_ok:
            fixed += 1
        else:
            missing = expected_sections - actual_sections
            still_broken.append({
                "task": case["task"][:90],
                "missing": sorted(missing),
                "got": sorted(actual_sections),
            })

    print()
    print("=" * 70)
    print(f"WITH STACK PREFIX — Re-test of {total} previously failed tasks")
    print("=" * 70)
    print(f"  Fixed: {fixed}/{total}  ({fixed/total*100:.1f}%)")
    print(f"  Still broken: {total - fixed}")
    if still_broken:
        print()
        for sb in still_broken:
            print(f"  STILL BROKEN: {sb['task']}")
            print(f"    MISSING: {sb['missing']}")
            print(f"    GOT: {sb['got']}")
            print()
    print("=" * 70)


if __name__ == "__main__":
    success = run_benchmark()
    print()
    run_with_stack_prefix()
    sys.exit(0 if success else 1)
