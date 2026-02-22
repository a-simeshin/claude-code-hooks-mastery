#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Status Line v10 - Context Window Progress Bar
[Opus] # [###---] | 42.5% used | ~115k left | session_id
"""

import json
import sys

# ANSI color codes
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
DIM = "\033[90m"
RESET = "\033[0m"


def get_usage_color(percentage: float) -> str:
    if percentage < 50:
        return GREEN
    elif percentage < 75:
        return YELLOW
    elif percentage < 90:
        return RED
    return "\033[91m"


def create_progress_bar(percentage: float, width: int = 10) -> str:
    filled = int((percentage / 100) * width)
    empty = width - filled
    color = get_usage_color(percentage)
    bar = f"{color}{'#' * filled}{DIM}{'-' * empty}{RESET}"
    return f"[{bar}]"


def format_tokens(tokens: int | float | None) -> str:
    if tokens is None:
        return "0"
    if tokens < 1000:
        return str(int(tokens))
    elif tokens < 1000000:
        return f"{tokens / 1000:.0f}k"
    return f"{tokens / 1000000:.1f}M"


def generate_status_line(input_data: dict) -> str:
    model_info = input_data.get("model", {})
    model_name = model_info.get("display_name", "Claude")

    context_data = input_data.get("context_window", {})
    used_percentage = context_data.get("used_percentage", 0) or 0
    context_window_size = context_data.get("context_window_size", 200000) or 200000
    remaining_tokens = int(context_window_size * ((100 - used_percentage) / 100))

    usage_color = get_usage_color(used_percentage)

    session_id = input_data.get("session_id", "") or "--------"
    parts = [
        f"{CYAN}[{model_name}]{RESET}",
        f"{MAGENTA}#{RESET} {create_progress_bar(used_percentage, 15)}",
        f"{usage_color}{used_percentage:.1f}%{RESET} used",
        f"{BLUE}~{format_tokens(remaining_tokens)} left{RESET}",
        f"{DIM}{session_id}{RESET}",
    ]
    return " | ".join(parts)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        print(generate_status_line(input_data))
        sys.exit(0)
    except json.JSONDecodeError:
        print(f"{RED}[Claude] # Error: Invalid JSON{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[Claude] # Error: {str(e)}{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
