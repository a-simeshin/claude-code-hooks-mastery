#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Section Loader - Loads specific sections from markdown reference files.

Usage:
    echo '{"sections": ["java-patterns#basics", "java-testing#integration"]}' | python section_loader.py

Sections are marked in files with HTML comments:
    <!-- section:basics -->
    ... content ...
    <!-- /section:basics -->
"""

import json
import re
import sys
from pathlib import Path


REFS_DIR = Path(__file__).parent.parent / "refs"


def parse_sections(content: str) -> dict[str, str]:
    """Parse markdown file and extract sections marked with HTML comments."""
    sections = {}

    # Pattern: <!-- section:name --> ... <!-- /section:name -->
    # Allow whitespace/newlines between marker and content
    pattern = r'<!-- section:(\w+) -->\s*(.*?)\s*<!-- /section:\1 -->'

    for match in re.finditer(pattern, content, re.DOTALL):
        section_name = match.group(1)
        section_content = match.group(2).strip()
        # Concatenate if section appears multiple times
        if section_name in sections:
            sections[section_name] += "\n\n" + section_content
        else:
            sections[section_name] = section_content

    return sections


def load_section(ref_file: str, section_name: str) -> str | None:
    """Load a specific section from a reference file."""
    file_path = REFS_DIR / f"{ref_file}.md"

    if not file_path.exists():
        return None

    content = file_path.read_text()
    sections = parse_sections(content)

    return sections.get(section_name)


def load_sections(section_specs: list[str]) -> dict[str, str]:
    """
    Load multiple sections from reference files.

    Args:
        section_specs: List of "file#section" strings, e.g., ["java-patterns#basics"]

    Returns:
        Dict mapping section spec to content
    """
    result = {}

    for spec in section_specs:
        if "#" not in spec:
            continue

        ref_file, section_name = spec.split("#", 1)
        content = load_section(ref_file, section_name)

        if content:
            result[spec] = content

    return result


def format_context(sections: dict[str, str]) -> str:
    """Format loaded sections as markdown context."""
    if not sections:
        return "No sections loaded."

    parts = []
    for spec, content in sections.items():
        ref_file, section_name = spec.split("#", 1)
        parts.append(f"## Reference: {ref_file} / {section_name}\n\n{content}")

    return "\n\n---\n\n".join(parts)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        section_specs = input_data.get("sections", [])

        if not section_specs:
            print("No sections requested.")
            sys.exit(0)

        sections = load_sections(section_specs)
        context = format_context(sections)

        # Output stats
        total_chars = sum(len(c) for c in sections.values())
        loaded_count = len(sections)
        requested_count = len(section_specs)

        print(f"<!-- Loaded {loaded_count}/{requested_count} sections, ~{total_chars // 4} tokens -->")
        print()
        print(context)

        sys.exit(0)

    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
