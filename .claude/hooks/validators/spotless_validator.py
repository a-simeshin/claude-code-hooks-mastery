#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Spotless + Palantir format validator for Java files.
PostToolUse hook - checks formatting after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "spotless_validator.log"

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
    logger.info(f"Spotless validator called for: {file_path}")

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

    # Check if spotless plugin is configured (check current and parent poms)
    def check_spotless_in_pom_tree(root: Path) -> bool:
        """Check for spotless in pom.xml tree (including parent poms)."""
        current = root
        while current.parent != current:
            pom_file = current / "pom.xml"
            if pom_file.exists():
                content = pom_file.read_text()
                if "spotless-maven-plugin" in content:
                    return True
            current = current.parent
        return False

    if not check_spotless_in_pom_tree(project_root):
        logger.info("Spotless plugin not configured in pom tree, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running spotless:check in {project_root}")

    try:
        result = subprocess.run(
            ["mvn", "spotless:check", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("Spotless check passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            logger.warning(f"Spotless check failed: {error_output[:500]}")
            print(
                json.dumps(
                    {
                        "decision": "block",
                        "reason": f"Spotless (Palantir format) check failed:\n{error_output[:500]}\n\nRun: mvn spotless:apply",
                    }
                )
            )
    except subprocess.TimeoutExpired:
        logger.error("Spotless check timed out")
        print(json.dumps({}))  # Don't block on timeout
    except FileNotFoundError:
        logger.warning("Maven not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
