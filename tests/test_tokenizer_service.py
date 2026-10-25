"""Tests for core TokenizerService (TDD red-green tests)."""

import pytest
from src.core.tokenizer_service import TokenizerService


@pytest.fixture
def service():
    return TokenizerService()


def test_tokenize_text_cl100k(service):
    res = service.tokenize("strawberry", encoding="cl100k_base")
    assert res.token_count == 3
    assert res.token_ids == [496, 675, 15717]
    assert [p.text for p in res.pieces] == ["str", "aw", "berry"]


def test_tokenize_text_o200k(service):
    res = service.tokenize("strawberry", encoding="o200k_base")
    assert res.encoding == "o200k_base"
    assert res.token_count > 0


def test_compare_encodings(service):
    comparisons = service.compare_encodings("Hello world!")
    assert "cl100k_base" in comparisons
    assert "o200k_base" in comparisons
    assert "r50k_base" in comparisons


def test_homograph_identical_tokens(service):
    # Both 'lead' as toxic metal and 'lead' as guide share identical token id
    metal_token = service.tokenize("lead", encoding="cl100k_base")
    guide_token = service.tokenize("lead", encoding="cl100k_base")
    assert metal_token.token_ids == guide_token.token_ids
    assert metal_token.token_ids == [27152]


def test_space_sensitivity(service):
    # ' apple' vs 'apple' have different tokens
    with_space = service.tokenize(" apple", encoding="cl100k_base")
    without_space = service.tokenize("apple", encoding="cl100k_base")
    assert with_space.token_ids != without_space.token_ids
    assert with_space.token_ids == [24149]
    assert without_space.token_ids == [23182]


def test_minority_language_token_tax(service):
    # Burmese should have significantly higher tokens than English
    en = service.tokenize("human rights", encoding="cl100k_base")
    burmese = service.tokenize("လူ့အခွင့်အရေး", encoding="cl100k_base")
    assert burmese.token_count > en.token_count * 2
