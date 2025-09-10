import os
from typing import Optional


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable value."""
    return os.environ.get(name, default)
