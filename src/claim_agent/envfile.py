"""Load settings such as OPENROUTER_API_KEY from a local .env file (gitignored).

Variables already set in the environment win over the file. Values are never logged or printed.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, MutableMapping, Optional

DEFAULT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse KEY=VALUE lines; supports comments, blank lines, `export KEY=...` and quoted values."""
    values: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if key:
            values[key] = value
    return values


def load_env_file(path: Optional[Path] = None, environ: Optional[MutableMapping[str, str]] = None) -> Dict[str, str]:
    """Copy variables from the .env file into the environment without overriding existing, non-empty ones.

    Returns the names (not values) of the variables that were set, mapped to their source file.
    """
    path = Path(path) if path else DEFAULT_ENV_FILE
    environ = os.environ if environ is None else environ
    if not path.is_file():
        return {}
    loaded = {}
    for key, value in parse_env_file(path).items():
        if value and not environ.get(key):
            environ[key] = value
            loaded[key] = str(path)
    return loaded
