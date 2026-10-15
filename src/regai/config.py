import json
import os
from dataclasses import dataclass
from pathlib import Path

import keyring


APP_NAME = "RegAI"
KEYRING_SERVICE = "RegAI"

DEFAULT_PROVIDER = "lm_studio"

PROVIDER_DEFAULTS = {
    "lm_studio": {
        "base_url": "http://localhost:1234/v1",
        "model": "qwen/qwen3.6-35b-a3b",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-5",
    },
}


def get_settings_path() -> Path:
    """Return the path used for persistent application settings."""

    app_data = Path(
        os.getenv("APPDATA", str(Path.home()))
    )

    return app_data / APP_NAME / "settings.json"


def get_keyring_username(provider: str) -> str:
    """Return a separate credential identifier for each provider."""

    return f"ai_api_key:{provider}"


@dataclass(frozen=True)
class AIConfig:
    provider: str
    base_url: str
    model: str
    api_key: str


def load_ai_config() -> AIConfig:
    """Load saved settings, with environment variables taking priority."""

    settings_path = get_settings_path()
    saved_settings = {}

    if settings_path.exists():
        try:
            with settings_path.open("r", encoding="utf-8") as settings_file:
                saved_settings = json.load(settings_file)
        except (OSError, json.JSONDecodeError):
            saved_settings = {}

    provider = os.getenv(
        "REGAI_AI_PROVIDER",
        saved_settings.get("provider", DEFAULT_PROVIDER),
    )

    if provider not in PROVIDER_DEFAULTS:
        provider = DEFAULT_PROVIDER

    defaults = PROVIDER_DEFAULTS[provider]

    base_url = os.getenv(
        "REGAI_AI_BASE_URL",
        saved_settings.get("base_url", defaults["base_url"]),
    )

    model = os.getenv(
        "REGAI_AI_MODEL",
        saved_settings.get("model", defaults["model"]),
    )

    api_key = os.getenv("REGAI_AI_API_KEY")

    if api_key is None:
        api_key = keyring.get_password(
            KEYRING_SERVICE,
            get_keyring_username(provider),
        )

    # Support the previous LM Studio credential identifier.
    if not api_key and provider == "lm_studio":
        api_key = keyring.get_password(
            KEYRING_SERVICE,
            "ai_api_key",
        )

    if not api_key and provider == "lm_studio":
        api_key = "lm-studio"

    return AIConfig(
        provider=provider,
        base_url=base_url,
        model=model,
        api_key=api_key or "",
    )


def save_ai_config(
    provider: str,
    base_url: str,
    model: str,
    api_key: str | None = None,
) -> None:
    """Save settings and optionally update the selected provider's API key."""

    if provider not in PROVIDER_DEFAULTS:
        raise ValueError(f"Unsupported AI provider: {provider}")

    if not base_url.strip():
        raise ValueError("The API endpoint cannot be empty.")

    if not model.strip():
        raise ValueError("The model name cannot be empty.")

    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings = {
        "provider": provider,
        "base_url": base_url.strip(),
        "model": model.strip(),
    }

    temporary_path = settings_path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=2)

    temporary_path.replace(settings_path)

    # A blank API-key field means "keep the existing key".
    if api_key and api_key.strip():
        keyring.set_password(
            KEYRING_SERVICE,
            get_keyring_username(provider),
            api_key.strip(),
        )