"""
Configuration Management using pydantic-settings and PyYAML.
"""
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional
import os
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Storage settings
    duckdb_path: str = "data/discovery_engine.duckdb"
    chroma_path: str = "data/chroma_db"
    chroma_collection_name: str = "fashion_wishlist_embeddings"

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None

    # Application settings
    log_level: str = "INFO"
    env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def load_yaml_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
