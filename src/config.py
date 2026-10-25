"""Application configuration using pydantic-settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment override support."""

    model_config = SettingsConfigDict(
        env_prefix="TOKENIZER_",
        env_file=".env",
        extra="ignore",
    )

    project_root: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    lib_dir: Path = Path(__file__).resolve().parent.parent / "lib"

    default_encoding: str = "cl100k_base"
    available_encodings: list[str] = ["cl100k_base", "o200k_base", "r50k_base"]

    # Pricing per 1M input tokens (USD) for comparison calculator
    pricing_gpt4_per_million: float = 30.00
    pricing_gpt4o_per_million: float = 2.50
    pricing_gpt35_per_million: float = 0.50


settings = Settings()
