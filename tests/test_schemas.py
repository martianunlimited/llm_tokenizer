"""Tests for Pydantic data schemas."""

import pytest
from pydantic import ValidationError
from src.schemas import TokenPiece, TokenizationResult, LanguageSample, CollisionPreset


def test_token_piece_valid():
    piece = TokenPiece(
        token_id=496,
        text="str",
        bytes_hex="737472",
        byte_length=3,
        is_printable=True,
        is_byte_fallback=False,
    )
    assert piece.token_id == 496
    assert piece.text == "str"
    assert piece.byte_length == 3


def test_tokenization_result_validation():
    result = TokenizationResult(
        text="strawberry",
        encoding="cl100k_base",
        token_ids=[496, 675, 15717],
        token_count=3,
        char_count=10,
        word_count=1,
        tokens_per_word=3.0,
        chars_per_token=3.33,
        pieces=[
            TokenPiece(token_id=496, text="str", bytes_hex="737472", byte_length=3),
            TokenPiece(token_id=675, text="aw", bytes_hex="6177", byte_length=2),
            TokenPiece(token_id=15717, text="berry", bytes_hex="6265727279", byte_length=5),
        ],
    )
    assert result.token_count == 3
    assert len(result.pieces) == 3


def test_language_sample_validation():
    sample = LanguageSample(
        code="en",
        name="English",
        native_name="English",
        script="Latin",
        family="Indo-European (Germanic)",
        text="All human beings are born free and equal in dignity and rights.",
        word_count=12,
        char_count=63,
        tokens_cl100k=13,
        tokens_o200k=13,
        tokens_r50k=13,
        tpw_cl100k=1.08,
        tpw_o200k=1.08,
        cost_multiplier_vs_english_cl100k=1.0,
        cost_multiplier_vs_english_o200k=1.0,
        is_minority_or_underrepresented=False,
        notes="Baseline English text",
    )
    assert sample.tokens_cl100k == 13
    assert sample.cost_multiplier_vs_english_cl100k == 1.0


def test_collision_preset_invalid_category():
    with pytest.raises(ValidationError):
        CollisionPreset(
            id="bad-preset",
            category="invalid_category_name",  # Should fail validation
            title="Bad",
            subtitle="Bad",
            explanation="Bad",
            consequence_for_llms="Bad",
            items=[],
        )
