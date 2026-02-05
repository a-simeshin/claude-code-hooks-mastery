#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
OSS Index security validator for Maven dependencies.
PostToolUse hook - checks dependencies for vulnerabilities after pom.xml changes.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "ossindex_validator.log"

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
    logger.info(f"OSS Index validator called for: {file_path}")

    # Only run for pom.xml changes
    if not file_path.endswith("pom.xml"):
        logger.info("Skipping non-pom.xml file")
        print(json.dumps({}))
        return

    # Find Maven project root
    project_root = find_pom_root(file_path)
    if not project_root:
        project_root = Path(file_path).parent

    # Check if OSS Index plugin is configured
    pom_content = Path(file_path).read_text()
    if "ossindex-maven-plugin" not in pom_content:
        logger.info("OSS Index plugin not configured, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running mvn ossindex:audit in {project_root}")

    try:
        result = subprocess.run(
            ["mvn", "ossindex:audit", "-q"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("OSS Index audit passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            # OSS Index is often configured as non-blocking
            logger.warning(f"OSS Index found vulnerabilities: {error_output[:500]}")
            # Don't block by default, just warn
            print(json.dumps({}))
    except subprocess.TimeoutExpired:
        logger.error("OSS Index audit timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("Maven not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
