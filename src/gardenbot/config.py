"""Centralized configuration for Gardenbot."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    data_dir: str = field(default_factory=lambda: os.environ.get("GARDENBOT_DATA_DIR", "./data"))
    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://newstage.cliffnet:11434")
    )
    ollama_model: str = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "llama3"))
    openai_api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))


settings = Settings()
