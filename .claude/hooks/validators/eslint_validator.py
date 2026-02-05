#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
ESLint validator for JavaScript/TypeScript files.
PostToolUse hook - checks linting after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "eslint_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

JS_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")


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
    logger.info(f"ESLint validator called for: {file_path}")

    # Skip non-JS/TS files
    if not file_path.endswith(JS_EXTENSIONS):
        logger.info("Skipping non-JS/TS file")
        print(json.dumps({}))
        return

    # Find Node.js project root
    project_root = find_package_root(file_path)
    if not project_root:
        logger.info("No package.json found, skipping")
        print(json.dumps({}))
        return

    # Check if ESLint is installed
    node_modules_eslint = project_root / "node_modules" / ".bin" / "eslint"
    if not node_modules_eslint.exists():
        logger.info("ESLint not installed, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running ESLint on {file_path}")

    try:
        result = subprocess.run(
            ["npx", "eslint", "--format=stylish", file_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("ESLint check passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            # Count errors vs warnings
            error_count = error_output.count(" error")
            if error_count > 0:
                logger.warning(f"ESLint found {error_count} errors")
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"ESLint errors found:\n{error_output[:500]}",
                        }
                    )
                )
            else:
                # Warnings don't block
                logger.info("ESLint passed (warnings only)")
                print(json.dumps({}))
    except subprocess.TimeoutExpired:
        logger.error("ESLint check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("npx not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
