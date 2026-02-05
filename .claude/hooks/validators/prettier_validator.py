#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Prettier format validator for JS/TS/CSS/JSON files.
PostToolUse hook - checks formatting after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "prettier_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

PRETTIER_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".json", ".md")


def find_package_root(file_path: str) -> Path | None:
    """Find Node.js project root (directory with package.json)."""
    current = Path(file_path).parent
    while current.parent != current:
        if (current / "package.json").exists():
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
    logger.info(f"Prettier validator called for: {file_path}")

    # Skip unsupported files
    if not file_path.endswith(PRETTIER_EXTENSIONS):
        logger.info("Skipping unsupported file type")
        print(json.dumps({}))
        return

    # Find Node.js project root
    project_root = find_package_root(file_path)
    if not project_root:
        logger.info("No package.json found, skipping")
        print(json.dumps({}))
        return

    # Check if Prettier is installed
    node_modules_prettier = project_root / "node_modules" / ".bin" / "prettier"
    if not node_modules_prettier.exists():
        logger.info("Prettier not installed, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running Prettier check on {file_path}")

    try:
        result = subprocess.run(
            ["npx", "prettier", "--check", file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("Prettier check passed")
            print(json.dumps({}))
        else:
            logger.warning("Prettier format check failed")
            print(
                json.dumps(
                    {
                        "decision": "block",
                        "reason": f"Prettier format check failed for {Path(file_path).name}\n\nRun: npx prettier --write {file_path}",
                    }
                )
            )
    except subprocess.TimeoutExpired:
        logger.error("Prettier check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("npx not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
