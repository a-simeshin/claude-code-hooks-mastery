#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Bandit security validator for Python files.
PostToolUse hook - checks for security issues after Write/Edit operations.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "bandit_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    try:
        hook_input = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    logger.info(f"Bandit validator called for: {file_path}")

    # Skip non-Python files
    if not file_path.endswith(".py"):
        logger.info("Skipping non-Python file")
        print(json.dumps({}))
        return

    # Skip test files (they often have intentional security issues for testing)
    if "test" in file_path.lower() or file_path.endswith("_test.py"):
        logger.info("Skipping test file")
        print(json.dumps({}))
        return

    logger.info(f"Running Bandit on {file_path}")

    try:
        result = subprocess.run(
            ["uvx", "bandit", "-f", "json", "-ll", file_path],  # -ll = medium and high severity only
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            logger.info("Bandit check passed")
            print(json.dumps({}))
        else:
            try:
                bandit_output = json.loads(result.stdout)
                issues = bandit_output.get("results", [])
                high_severity = [i for i in issues if i.get("issue_severity") == "HIGH"]

                if high_severity:
                    logger.warning(f"Bandit found {len(high_severity)} high severity issues")
                    issue_msgs = [
                        f"- {i['issue_text']} (line {i['line_number']})"
                        for i in high_severity[:5]
                    ]
                    print(
                        json.dumps(
                            {
                                "decision": "block",
                                "reason": f"Bandit security issues (HIGH severity):\n{chr(10).join(issue_msgs)}",
                            }
                        )
                    )
                else:
                    # Medium severity - warn but don't block
                    logger.info("Bandit found medium severity issues only, not blocking")
                    print(json.dumps({}))
            except json.JSONDecodeError:
                # Parse error - don't block
                logger.warning("Could not parse Bandit output")
                print(json.dumps({}))
    except subprocess.TimeoutExpired:
        logger.error("Bandit check timed out")
        print(json.dumps({}))
    except FileNotFoundError:
        logger.warning("uvx not found")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
