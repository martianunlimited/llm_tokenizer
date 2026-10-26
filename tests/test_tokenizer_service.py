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


def test_thai_tokenization_inefficiency(service):
    # Thai UDHR sentence (68 chars, 15 words) has severe token tax in cl100k and r50k
    thai_udhr = "เราทุกคนเกิดมาอย่างอิสระและมีความเท่าเทียมกันในเกียรติศักดิ์และสิทธิ"
    res_cl = service.tokenize(thai_udhr, encoding="cl100k_base")
    res_r5 = service.tokenize(thai_udhr, encoding="r50k_base")
    res_o2 = service.tokenize(thai_udhr, encoding="o200k_base")

    # In cl100k, almost 1 token per character (65 tokens for 68 characters)
    assert res_cl.token_count >= 60
    # In r50k (GPT-3), byte fallbacks cause 136 tokens (>2 tokens per character!)
    assert res_r5.token_count > 100
    # o200k has better compression but still > 30 tokens
    assert res_o2.token_count >= 30


def test_thai_word_segmentation_ambiguity(service):
    # 'ตากลม' can mean 'ตา-กลม' (round eyes) or 'ตาก-ลม' (basking in wind)
    # In cl100k it splits into 5 separate letter tokens: ต, า, ก, ล, ม
    res = service.tokenize("ตากลม", encoding="cl100k_base")
    assert res.token_count == 5
    assert res.token_ids == [40955, 21437, 26265, 32882, 27379]


def test_thai_cross_boundary_merging(service):
    # 'ไปหามเหสี' (visit queen consort) in o200k merges across word boundary into 'าม'
    res_o2 = service.tokenize("ไปหามเหสี", encoding="o200k_base")
    pieces_str = [p.text for p in res_o2.pieces]
    # 'าม' (token id 13221) is formed by combining 'า' of 'หา' + 'ม' of 'มเหสี'
    assert "าม" in pieces_str
