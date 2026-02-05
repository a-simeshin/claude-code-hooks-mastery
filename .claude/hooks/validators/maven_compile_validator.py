#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Maven compile validator for Java files.
PostToolUse hook - checks compilation after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "maven_compile_validator.log"

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
    logger.info(f"Maven compile validator called for: {file_path}")

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

    logger.info(f"Running mvn compile in {project_root}")

    try:
        result = subprocess.run(
            ["mvn", "compile", "-q", "-DskipTests"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("Maven compile passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            logger.warning(f"Maven compile failed: {error_output[:500]}")
            print(
                json.dumps(
                    {
                        "decision": "block",
                        "reason": f"Maven compilation failed:\n{error_output[:500]}",
                    }
                )
            )
    except subprocess.TimeoutExpired:
        logger.error("Maven compile timed out")
        print(json.dumps({}))  # Don't block on timeout
    except FileNotFoundError:
        logger.warning("Maven not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
