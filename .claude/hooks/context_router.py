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

    # ── Python Patterns ──
    ("python-patterns#core", [
        "python", "typing", "type hint", "dataclass",
        "await", "pathlib", "logging",
        "enum", "abc", "protocol", ".py",
        "pydantic", "fastapi", "pytest", "asyncio",
    ], 10),
    ("python-patterns#fastapi", [
        "fastapi", "apirouter", "pydantic", "basemodel",
        "depends", "dependency injection", "lifespan",
        "backgroundtask", "httpexception",
        "uvicorn",
    ], 8),
    ("python-patterns#testing", [
        "pytest", "fixture", "parametrize", "conftest",
        "patch", "httpx", "asyncclient", "testclient",
        "coverage",
    ], 8),
]

# Companion rules: if ANY section with prefix matched → auto-include companion
COMPANION_RULES: list[tuple[str, str]] = [
    ("java-patterns#", "java-patterns#basics"),
    ("java-testing#", "java-testing#structure"),
    ("react-patterns#", "react-patterns#core"),
    ("python-patterns#", "python-patterns#core"),
]

# Detect "test" keyword per stack → auto-include testing sections
TEST_KEYWORD_RULES: list[tuple[list[str], str]] = [
    # If Java context + "test" mentioned → java-testing#structure
    (["java", "spring", "controller", ".java", "jpa"], "java-testing#structure"),
    # If Python context + "test" mentioned → python-patterns#testing
    (["python", "fastapi", "pydantic", ".py", "pytest"], "python-patterns#testing"),
]

MAX_SECTIONS = 6


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
    if not explicit_java and ("python-patterns" in stacks or "react-patterns" in stacks):
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
