#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Deterministic Context Router for Claude Code.

Replaces Haiku-based agent routing (1/6 success rate) with keyword matching.
100% reliable, zero LLM cost, instant execution.

Input: task description via stdin (plain text or JSON with "task" key)
Output: JSON {"sections": [...], "reasoning": "..."}

Usage:
  echo "Создай React компонент логина" | uv run --script context_router.py
  echo '{"task": "Add FastAPI endpoint"}' | uv run --script context_router.py
"""
import json
import re
import sys


# Section → keyword patterns (case-insensitive)
# Each tuple: (section_id, [keywords], priority)
# Higher priority sections are added first
ROUTING_TABLE: list[tuple[str, list[str], int]] = [
    # ── Java Patterns ──
    ("java-patterns#basics", [
        "java", "spring", "controller", "entity",
        "jpa", "maven", "gradle", "lombok", "bean", "autowired",
        "springboot", "spring boot", "spring-boot",
        ".java", "pom.xml",
    ], 10),
    ("java-patterns#java17", [
        "record", "pattern matching", "switch expression", "text block",
        "sealed", "instanceof pattern",
    ], 5),
    ("java-patterns#java21", [
        "virtual thread", "sequenced collection", "pattern switch",
        "string template",
    ], 5),
    ("java-patterns#errors", [
        "exception", "error handling", "controlleradvice",
        "404", "400", "500", "http status", "error response",
        "exceptionhandler", "validation error",
        "ошибк", "ошибок",
    ], 8),
    ("java-patterns#search", [
        "serena", "code search", "find reference",
    ], 3),

    # ── Java Testing ──
    ("java-testing#philosophy", [
        "test strategy", "what to test", "test priorit",
    ], 4),
    ("java-testing#structure", [
        "given-when-then", "assertj", "allure", "test naming",
        "test structure",
    ], 6),
    ("java-testing#integration", [
        "testcontainers", "podman", "base test", "integration test",
        "интеграционн",
    ], 7),
    ("java-testing#http", [
        "mockmvc", "resttemplate", "rest test", "http test",
        "webmvctest", "webtestclient",
    ], 6),
    ("java-testing#kafka", [
        "kafka test", "consumer test", "producer test",
        "embeddedkafka",
    ], 5),
    ("java-testing#jdbc", [
        "database test", "repository test", "jdbc test",
        "datajpatest",
    ], 5),
    ("java-testing#wiremock", [
        "wiremock", "external api", "mock http", "mock server",
    ], 5),
    ("java-testing#mockito", [
        "mockito", "spy", "when(", "given(",
    ], 6),
    ("java-testing#e2e", [
        "selenide", "selenium", "browser test", "ui test",
        "page object", "e2e",
    ], 5),
    ("java-testing#maven", [
        "surefire", "failsafe", "jacoco", "maven plugin",
    ], 4),

    # ── React Patterns ──
    ("react-patterns#core", [
        "react", "component", "hook", "usestate", "useeffect",
        "usecallback", "usememo", "useref", "usecontext",
        "props", "children", "memo", "portal",
        "error boundary", "suspense", "tsx", "jsx",
        "button", "form", "modal", "header", "sidebar",
        "frontend", "компонент", "кнопк", "форм",
    ], 10),
    ("react-patterns#nextjs", [
        "next", "nextjs", "next.js", "server component", "client component",
        "app router", "server action", "rsc", "ssr", "isr",
        "metadata", "middleware", "route handler", "getserversideprops",
        "use server", "use client",
    ], 8),
    ("react-patterns#vite", [
        "vite", "react-router", "react router",
        "client-side routing", "lazy loading", "lazy(",
        "code splitting", "vite_", "hmr", "hot module",
        "createbrowserrouter",
    ], 8),

    # ── Python Patterns (granular sections) ──
    ("python-patterns#layout", [
        "project layout", "src layout", "src-layout",
        "pyproject", "pyproject.toml",
        "ruff", "pyright", "pre-commit",
        "uv lock", "poetry lock", "toolchain",
        "layout проекта", "структура проекта python",
    ], 4),
    ("python-patterns#typing", [
        "python", ".py",
        "typing", "type hint", "type-hint", "type hints",
        "mypy", "pyright",
        "typevar", "newtype", "literal type", "literal[",
        "final type", "self type", "@override",
        "assert_never", "type_checking", "type alias",
        "protocol", "typing.protocol",
        "abc", "abstractmethod",
        "generic[", "generic typing",
        "аннотации типов", "типизация",
        "type system",
    ], 10),
    ("python-patterns#data", [
        "dataclass", "dataclasses",
        "frozen=true", "slots=true", "kw_only",
        "namedtuple", "typeddict",
        "value object", "value-object",
        "enum python", "strenum", "intenum",
        "data class", "data modeling python",
        "domain model python",
    ], 7),
    ("python-patterns#errors", [
        "python exception", "exceptiongroup",
        "raise from", "raise ... from",
        "custom exception python", "exception hierarchy python",
        "питон ошибк", "питон исключени",
        "обработка ошибок python",
        "except*",
    ], 7),
    ("python-patterns#logging", [
        "structlog", "structured logging python",
        "python logging", "лог в python",
        "logger.bind", "contextvars logging",
        "queuehandler",
    ], 5),
    ("python-patterns#io", [
        "pathlib", "path object python",
        "контекстный менеджер", "context manager python",
        "with statement python",
        "asynccontextmanager", "contextmanager",
        "aiofiles",
    ], 5),
    ("python-patterns#idiom", [
        "list comprehension", "dict comprehension", "set comprehension",
        "comprehension python",
        "match case", "match-case", "pattern matching python",
        "functools", "lru_cache", "cached_property", "singledispatch",
        "@cache", "@lru_cache",
    ], 6),
    ("python-patterns#fastapi", [
        "fastapi", "apirouter",
        "pydantic", "basemodel",
        "depends", "dependency injection python",
        "lifespan",
        "backgroundtask", "background tasks fastapi",
        "httpexception",
        "uvicorn",
        "response_model", "status_code",
        "pydantic-settings", "basesettings",
        "field_validator", "model_validator", "computed_field",
        "endpoint fastapi", "api endpoint python",
        "middleware fastapi",
        "exception_handler",
    ], 9),
    ("python-patterns#concurrency", [
        "asyncio", "async def", "await",
        "asyncio.gather", "gather python",
        "taskgroup", "task group",
        "asyncio.semaphore", "asyncio.lock",
        "race condition", "race-condition",
        "contextvar", "contextvars",
        "cancellation", "cancellederror", "cancelled error",
        "connection pool", "pool_size", "max_connections",
        "asyncpg", "sqlalchemy async",
        "selectinload", "joinedload", "missinggreenlet",
        "threadpool", "to_thread", "run_in_executor",
        "processpool", "process pool",
        "uvloop",
        "graceful shutdown",
        "liveness", "readiness",
        "backpressure", "rate limit", "rate-limit", "circuit breaker",
        "tenacity",
        "streamingresponse", "streaming response",
        "sync client", "sync клиент", "синхронный клиент",
        "блокирующий клиент", "blocking client",
        "block event loop", "event loop lag",
        "многопоточн", "concurrency",
        "httpx", "asyncclient",
        "fastapi performance", "production fastapi",
    ], 9),

    # ── Python Testing (separate file) ──
    ("python-testing#philosophy", [
        "test strategy python", "тестовая стратегия python",
        "test pyramid python", "что тестировать в python",
        "integration vs unit python",
    ], 4),
    ("python-testing#structure", [
        "pytest", "pytest naming",
        "pytest assertion", "pytest plain assert",
        "arrange act assert", "given-when-then python",
        "pytest.raises", "pytest.approx",
        "pytest test class",
    ], 10),
    ("python-testing#config", [
        "pytest config", "pyproject pytest",
        "asyncio_mode", "strict-markers", "strict markers",
        "xfail_strict", "conftest hierarchy",
        "pytest.ini",
        "filterwarnings",
    ], 5),
    ("python-testing#fixtures", [
        "fixture", "фикстур",
        "fixture scope", "conftest",
        "session scope", "function scope", "module scope",
        "yield fixture", "factory fixture",
        "async fixture",
    ], 8),
    ("python-testing#parametrize", [
        "parametrize", "parameterize",
        "pytest.param", "data-driven test python",
        "indirect parametrize",
    ], 7),
    ("python-testing#integration", [
        "testcontainers", "testcontainers-python",
        "asgi transport", "asgitransport",
        "asyncclient test", "httpx asyncclient",
        "respx", "responses python",
        "real database test", "real postgres test",
        "интеграционный тест python",
        "integration test python",
    ], 8),
    ("python-testing#unit", [
        "pytest-mock", "mocker fixture",
        "autospec", "create_autospec",
        "fake repository", "protocol fake",
        "freezegun", "time-machine", "freeze time",
        "юнит-тест python",
        "unit test python",
        "mock python",
    ], 7),
    ("python-testing#property", [
        "hypothesis", "property-based", "property based test",
        "generative test", "hypothesis strategies",
        "@given",
    ], 5),
    ("python-testing#snapshot", [
        "snapshot test python", "syrupy", "inline-snapshot",
        "snapshot pytest",
    ], 4),
    ("python-testing#async", [
        "pytest-asyncio", "async test python",
        "asyncio_mode auto", "anyio backend",
    ], 6),
    ("python-testing#test-data", [
        "polyfactory", "faker",
        "test data builder python", "test factory python",
        "build_order",
    ], 5),
    ("python-testing#ci", [
        "pytest coverage", "pytest-xdist", "pytest parallel",
        "pytest-randomly", "pytest-timeout",
        "diff-cover", "branch coverage python",
    ], 4),
]

# Companion rules: if ANY section with prefix matched → auto-include companion
COMPANION_RULES: list[tuple[str, str]] = [
    ("java-patterns#", "java-patterns#basics"),
    ("java-testing#", "java-testing#structure"),
    ("react-patterns#", "react-patterns#core"),
    ("python-patterns#", "python-patterns#typing"),     # baseline для всех Python задач
    ("python-testing#", "python-testing#structure"),    # baseline для всех pytest задач
]

# Detect "test" keyword per stack → auto-include testing sections
TEST_KEYWORD_RULES: list[tuple[list[str], str]] = [
    # If Java context + "test" mentioned → java-testing#structure
    (["java", "spring", "controller", ".java", "jpa"], "java-testing#structure"),
    # If Python context + "test/тест" mentioned → python-testing#structure
    (["python", "fastapi", "pydantic", ".py", "pytest", "asyncio"],
     "python-testing#structure"),
]

MAX_SECTIONS = 8


def normalize(text: str) -> str:
    """Lowercase + collapse whitespace for matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def route(task: str) -> dict:
    """Match task text against routing table, return sections + reasoning."""
    task_norm = normalize(task)
    matched: list[tuple[str, int, str]] = []

    for section_id, keywords, priority in ROUTING_TABLE:
        for kw in keywords:
            if kw in task_norm:
                matched.append((section_id, priority, kw))
                break

    # Dedupe and sort by priority (descending)
    seen: set[str] = set()
    unique: list[tuple[str, int, str]] = []
    for section_id, priority, kw in sorted(matched, key=lambda x: -x[1]):
        if section_id not in seen:
            seen.add(section_id)
            unique.append((section_id, priority, kw))

    # Stack disambiguation: if Python/React matched WITHOUT explicit Java keywords,
    # remove Java false positives (e.g. "service" in "UserService" for pytest)
    stacks = {s.split("#")[0] for s, _, _ in unique}
    explicit_java = any(
        kw in task_norm
        for kw in ["java", "spring", "jpa", "maven", "gradle", ".java",
                    "spring boot", "springboot", "lombok", "controller"]
    )
    python_or_react_matched = (
        "python-patterns" in stacks
        or "python-testing" in stacks
        or "react-patterns" in stacks
    )
    if not explicit_java and python_or_react_matched:
        unique = [(s, p, kw) for s, p, kw in unique
                  if not s.startswith("java-")]
        seen = {s for s, _, _ in unique}

    # Apply companion rules: if any section with prefix matched, include companion
    prefixes_matched = {s.rsplit("#", 1)[0] + "#" for s, _, _ in unique}
    for prefix, companion in COMPANION_RULES:
        if prefix in prefixes_matched and companion not in seen:
            seen.add(companion)
            unique.append((companion, 1, "auto-rule"))

    # Apply test keyword rules
    has_test = any(kw in task_norm for kw in ["test", "тест"])
    if has_test:
        for stack_keywords, test_section in TEST_KEYWORD_RULES:
            if any(kw in task_norm for kw in stack_keywords):
                if test_section not in seen:
                    seen.add(test_section)
                    unique.append((test_section, 5, "test-rule"))

    # Cap at MAX_SECTIONS, sort by priority
    unique.sort(key=lambda x: -x[1])
    sections = [s for s, _, _ in unique[:MAX_SECTIONS]]
    keywords_used = [kw for _, _, kw in unique[:MAX_SECTIONS] if kw not in ("auto-rule", "test-rule")]

    if not sections:
        reasoning = "No matching keywords found in task"
    else:
        reasoning = f"Matched: {', '.join(dict.fromkeys(keywords_used))}"

    return {"sections": sections, "reasoning": reasoning}


def parse_input(raw: str) -> str:
    """Extract task text from stdin — supports plain text or JSON."""
    raw = raw.strip()
    if not raw:
        return ""

    # Try JSON first
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data.get("task", data.get("prompt", data.get("arguments", "")))
        return ""
    except json.JSONDecodeError:
        return raw


def main():
    raw = sys.stdin.read()
    task = parse_input(raw)

    if not task:
        print(json.dumps({"sections": [], "reasoning": "No task provided"}))
        return

    result = route(task)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
