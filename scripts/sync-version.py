#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def extract_version() -> str:
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()

    # Match version = "x.y.z" pattern
    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)

    if not version_match:
        raise ValueError("Could not find version in pyproject.toml")

    return version_match.group(1)


def update_version_file(version: str) -> None:
    version_file_path = Path("src/payos/_version.py")

    new_content = f'# Do not update manually, this will be generate when building\n__version__ = "{version}"\n'

    # Create directory if it doesn't exist
    version_file_path.parent.mkdir(parents=True, exist_ok=True)

    version_file_path.write_text(new_content)
    print(f"Updated {version_file_path} with version {version}")


def main():
    try:
        version = extract_version()
        update_version_file(version)
        print(f"Successfully synchronized version: {version}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
