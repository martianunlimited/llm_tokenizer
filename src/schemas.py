"""Pydantic data schemas for tokenization, language equity benchmarks, and collision presets."""

from typing import Literal
from pydantic import BaseModel, Field


class TokenPiece(BaseModel):
    """Detailed breakdown of a single token."""

    token_id: int
    text: str
    bytes_hex: str
    byte_length: int
    is_printable: bool = True
    is_byte_fallback: bool = False


class TokenizationResult(BaseModel):
    """Result of tokenizing a text string with an LLM tokenizer."""

    text: str
    encoding: str
    token_ids: list[int]
    token_count: int
    char_count: int
    word_count: int
    tokens_per_word: float
    chars_per_token: float
    pieces: list[TokenPiece]


class LanguageSample(BaseModel):
    """Multi-lingual parallel corpus item for benchmarking tokenizer equity."""

    code: str
    name: str
    native_name: str
    script: str
    family: str
    text: str
    word_count: int
    char_count: int
    tokens_cl100k: int = Field(description="Token count in GPT-4 (cl100k_base)")
    tokens_o200k: int = Field(description="Token count in GPT-4o (o200k_base)")
    tokens_r50k: int = Field(description="Token count in GPT-3 (r50k_base)")
    tpw_cl100k: float = Field(description="Tokens per word in GPT-4")
    tpw_o200k: float = Field(description="Tokens per word in GPT-4o")
    cost_multiplier_vs_english_cl100k: float = Field(
        description="Economic multiplier relative to English under GPT-4"
    )
    cost_multiplier_vs_english_o200k: float = Field(
        description="Economic multiplier relative to English under GPT-4o"
    )
    is_minority_or_underrepresented: bool = False
    notes: str = ""


class ComparisonItem(BaseModel):
    """An item within a collision or quirk comparison."""

    label: str
    input_text: str
    token_ids: list[int]
    token_count: int
    tokens_str: list[str]
    meaning_or_context: str


class CollisionPreset(BaseModel):
    """Preset scenario demonstrating homographs, false friends, or tokenizer blindspots."""

    id: str
    category: Literal[
        "homograph",
        "false_friend",
        "space_shift",
        "letter_counting",
        "math_split",
        "homoglyph",
        "glitch_token",
        "scriptio_continua",
    ]
    title: str
    subtitle: str
    explanation: str
    consequence_for_llms: str
    items: list[ComparisonItem]
