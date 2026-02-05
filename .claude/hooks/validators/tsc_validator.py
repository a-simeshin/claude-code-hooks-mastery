#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
TypeScript compiler validator for TS files.
PostToolUse hook - checks type errors after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "tsc_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

TS_EXTENSIONS = (".ts", ".tsx")


def find_package_root(file_path: str) -> Path | None:
    """Find Node.js project root (directory with package.json or tsconfig.json)."""
    current = Path(file_path).parent
    while current.parent != current:
        if (current / "tsconfig.json").exists() or (current / "package.json").exists():
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
    logger.info(f"TSC validator called for: {file_path}")

    # Skip non-TypeScript files
    if not file_path.endswith(TS_EXTENSIONS):
        logger.info("Skipping non-TypeScript file")
        print(json.dumps({}))
        return

    # Find project root
    project_root = find_package_root(file_path)
    if not project_root:
        logger.info("No tsconfig.json or package.json found, skipping")
        print(json.dumps({}))
        return

    # Check if tsconfig exists
    if not (project_root / "tsconfig.json").exists():
        logger.info("No tsconfig.json found, skipping")
        print(json.dumps({}))
        return

    logger.info(f"Running tsc --noEmit in {project_root}")

    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root,
        )

        if result.returncode == 0:
            logger.info("TypeScript check passed")
            print(json.dumps({}))
        else:
            error_output = result.stdout + result.stderr
            # Extract errors related to the changed file
            file_errors = [
                line
                for line in error_output.split("\n")
                if Path(file_path).name in line or "error TS" in line
            ]
            if file_errors:
                logger.warning(f"TypeScript errors: {len(file_errors)}")
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"TypeScript errors:\n{chr(10).join(file_errors[:10])}",
                        }
                    )
                )
            else:
                # Errors in other files - don't block
                logger.info("TypeScript errors in other files, not blocking")
                print(json.dumps({}))
    except subprocess.TimeoutExpired:
        logger.error("TypeScript check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("npx not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
