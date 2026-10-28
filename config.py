"""Configuration for Political Arena.

All settings come from environment variables or the local `.env` file.
Nothing secret is ever written in the source code.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

from dotenv import dotenv_values

# Debate limits required by the assignment.
MIN_ROUNDS = 1
MAX_ROUNDS = 10

# Default Groq models. They can be changed in `.env` because Groq's
# model list changes over time.
DEFAULT_GOVERNMENT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPPOSITION_MODEL = "llama-3.1-8b-instant"

# Request settings (kept small so free-tier rate limits are respected).
REQUEST_TIMEOUT_SECONDS = 45.0
MAX_TOKENS_PER_RESPONSE = 700
TEMPERATURE = 0.6

ENV_FILE = Path(__file__).resolve().parent / ".env"


@dataclass(frozen=True)
class Settings:
    """Runtime settings. The API key is hidden from repr() on purpose."""

    groq_api_key: str = field(default="", repr=False)
    government_model: str = DEFAULT_GOVERNMENT_MODEL
    opposition_model: str = DEFAULT_OPPOSITION_MODEL

    @property
    def has_api_key(self) -> bool:
        return bool(self.groq_api_key)


def _clean(value: Optional[str]) -> str:
    """Trim spaces and accidental surrounding quotes."""
    return (value or "").strip().strip("\"'").strip()


def load_settings(env: Optional[Mapping[str, str]] = None) -> Settings:
    """Read settings.

    Order of priority for each value:
      1. A non-empty value in the `.env` file
      2. A non-empty value in the real environment variables
      3. The built-in default (models only)

    Pass `env` (a dict) in tests to avoid touching the real environment.
    """
    if env is None:
        file_values = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
        os_values = os.environ
    else:
        file_values = {}
        os_values = env

    def get(name: str) -> str:
        return _clean(file_values.get(name)) or _clean(os_values.get(name))

    return Settings(
        groq_api_key=get("GROQ_API_KEY"),
        government_model=get("GOVERNMENT_MODEL") or DEFAULT_GOVERNMENT_MODEL,
        opposition_model=get("OPPOSITION_MODEL") or DEFAULT_OPPOSITION_MODEL,
    )
