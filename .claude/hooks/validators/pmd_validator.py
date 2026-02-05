#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
PMD static analysis validator for Java files.
PostToolUse hook - checks code quality after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "pmd_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def find_pom_root(file_path: str) -> Path | None:
    """Find Maven project root (directory with pom.xml)."""
    current = Path(file_path).parent
    while current.parent != current:
        if (current / "pom.xml").exists():
            return current
        current = current.parent
    return None


def main():
    try:
        hook_input = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    logger.info(f"PMD validator called for: {file_path}")

    # Skip non-Java files
    if not file_path.endswith(".java"):
        logger.info("Skipping non-Java file")
        print(json.dumps({}))
        return

    # Find Maven project root
    project_root = find_pom_root(file_path)
    if not project_root:
        logger.info("No pom.xml found, skipping")
        print(json.dumps({}))
        return

    # Check if PMD plugin is configured
    pom_content = (project_root / "pom.xml").read_text()
    if "maven-pmd-plugin" not in pom_content:
        logger.info("PMD plugin not configured, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running mvn pmd:check in {project_root}")

    try:
        result = subprocess.run(
            ["mvn", "pmd:check", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("PMD check passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            # PMD is often configured as non-blocking, so log but don't block
            logger.warning(f"PMD check found issues: {error_output[:500]}")
            # Only block if failOnViolation is true
            if "You have" in error_output and "PMD violation" in error_output:
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"PMD violations found:\n{error_output[:500]}",
                        }
                    )
                )
            else:
                print(json.dumps({}))
    except subprocess.TimeoutExpired:
        logger.error("PMD check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("Maven not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
