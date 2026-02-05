#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
JaCoCo coverage validator for Java projects.
PostToolUse hook - checks coverage after test runs.
Note: This is typically run during verify phase, not on every file change.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "jacoco_validator.log"

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
    logger.info(f"JaCoCo validator called for: {file_path}")

    # Only run for test files to avoid slowing down development
    if not file_path.endswith("Test.java") and not file_path.endswith("IT.java"):
        logger.info("Skipping non-test file (JaCoCo runs on test changes only)")
        print(json.dumps({}))
        return

    # Find Maven project root
    project_root = find_pom_root(file_path)
    if not project_root:
        logger.info("No pom.xml found, skipping")
        print(json.dumps({}))
        return

    # Check if JaCoCo plugin is configured
    pom_content = (project_root / "pom.xml").read_text()
    if "jacoco-maven-plugin" not in pom_content:
        logger.info("JaCoCo plugin not configured, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running mvn test jacoco:check in {project_root}")

    try:
        # Run tests with JaCoCo
        result = subprocess.run(
            ["mvn", "test", "jacoco:check", "-q"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("JaCoCo coverage check passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            # Check if it's a coverage failure
            if "Coverage checks have not been met" in error_output:
                logger.warning("Coverage below threshold")
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"JaCoCo coverage check failed:\n{error_output[:500]}\n\nIncrease test coverage to meet 80% threshold.",
                        }
                    )
                )
            else:
                logger.warning(f"JaCoCo check failed: {error_output[:500]}")
                print(json.dumps({}))  # Don't block on other failures
    except subprocess.TimeoutExpired:
        logger.error("JaCoCo check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("Maven not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
