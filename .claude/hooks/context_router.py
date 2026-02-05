#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Context Router - Analyzes task and returns required reference sections.

Usage:
    echo "Добавь endpoint /users с тестами" | python context_router.py

Output: JSON with sections to load
"""

import json
import re
import sys


# Section mappings: pattern -> sections
PATTERNS = {
    # Java code patterns
    r"(?i)(endpoint|api|controller|rest|service|repository|entity|dto)": [
        "java-patterns#basics"
    ],
    r"(?i)(ошибк|error|exception|404|400|401|403|409|not.?found|validation)": [
        "java-patterns#errors"
    ],
    r"(?i)(record|pattern.?match|switch|text.?block|sealed)": [
        "java-patterns#java17"
    ],
    r"(?i)(virtual.?thread|sequenced|java.?21)": [
        "java-patterns#java21"
    ],

    # Testing patterns
    r"(?i)(тест|test|junit|jupiter|assert|mock|verify)": [
        "java-testing#structure"
    ],
    r"(?i)(интеграц|integration|testcontainer|podman|docker)": [
        "java-testing#integration"
    ],
    r"(?i)(http|rest.?template|mockmvc|web.?test)": [
        "java-testing#http"
    ],
    r"(?i)(kafka|consumer|producer|messag)": [
        "java-testing#kafka"
    ],
    r"(?i)(jdbc|jpa|repository|database|sql|postgres)": [
        "java-testing#jdbc"
    ],
    r"(?i)(wiremock|external|mock.?server|stub)": [
        "java-testing#wiremock"
    ],
    r"(?i)(mockito|mock|spy|when\(|given\()": [
        "java-testing#mockito"
    ],
    r"(?i)(e2e|selenium|selenide|browser|ui.?test|page.?object)": [
        "java-testing#e2e"
    ],
    r"(?i)(maven|pom|surefire|failsafe|jacoco|coverage)": [
        "java-testing#maven"
    ],

    # React patterns (when available)
    r"(?i)(react|component|hook|button|form|modal|ui|tsx|jsx)": [
        "react-patterns#components"
    ],
    r"(?i)(useState|useEffect|useContext|useMemo|useCallback)": [
        "react-patterns#hooks"
    ],
    r"(?i)(redux|context|state.?manage|store)": [
        "react-patterns#state"
    ],
    r"(?i)(router|route|navigation|link|redirect)": [
        "react-patterns#routing"
    ],
}

# Always include these for certain contexts
CONTEXT_DEFAULTS = {
    "java": ["java-patterns#basics"],
    "test": ["java-testing#structure"],
}


def analyze_task(task: str) -> dict:
    """Analyze task and return required sections."""
    sections = set()
    reasoning_parts = []

    # Check each pattern
    for pattern, section_list in PATTERNS.items():
        if re.search(pattern, task):
            sections.update(section_list)
            # Extract what matched for reasoning
            match = re.search(pattern, task)
            if match:
                reasoning_parts.append(f"'{match.group()}' → {section_list}")

    # Add defaults if no sections matched
    if not sections:
        # Default to basics if task mentions Java-related things
        if re.search(r"(?i)(java|spring|class|method)", task):
            sections.add("java-patterns#basics")
            reasoning_parts.append("default Java patterns")

    # If testing mentioned, always include structure
    if any("testing" in s for s in sections):
        sections.add("java-testing#structure")

    # Limit to max 6 sections
    sections_list = sorted(list(sections))[:6]

    return {
        "sections": sections_list,
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No specific patterns matched",
        "tokens_estimate": len(sections_list) * 2000  # rough estimate
    }


def main():
    try:
        task = sys.stdin.read().strip()

        if not task:
            print(json.dumps({"sections": [], "reasoning": "Empty task", "tokens_estimate": 0}))
            sys.exit(0)

        result = analyze_task(task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
