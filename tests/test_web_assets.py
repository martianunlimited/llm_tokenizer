"""Tests verifying web assets, bundled tokenizers, and dataset integrity."""

import json
from src.config import settings


def test_bundled_tokenizer_libraries_exist():
    """Verify that all three real LLM tokenizer client-side bundles exist in lib/."""
    lib_dir = settings.lib_dir
    cl100k = lib_dir / "cl100k_base.js"
    o200k = lib_dir / "o200k_base.js"
    r50k = lib_dir / "r50k_base.js"

    assert cl100k.exists(), "cl100k_base.js (GPT-4) must exist in lib/"
    assert o200k.exists(), "o200k_base.js (GPT-4o) must exist in lib/"
    assert r50k.exists(), "r50k_base.js (GPT-3) must exist in lib/"

    assert cl100k.stat().st_size > 100_000, "cl100k_base.js should be substantial bundle"
    assert o200k.stat().st_size > 100_000, "o200k_base.js should be substantial bundle"
    assert r50k.stat().st_size > 50_000, "r50k_base.js should be substantial bundle"


def test_language_dataset_integrity():
    """Verify data/languages.json has required fields and minority languages."""
    lang_file = settings.data_dir / "languages.json"
    assert lang_file.exists(), "languages.json must exist"

    with open(lang_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) >= 12, "Should have at least 12 representative languages"

    codes = {item["code"] for item in data}
    assert "en" in codes, "Must include English baseline"
    assert "my" in codes, "Must include Burmese (extreme minority tax)"
    assert "hi" in codes, "Must include Hindi"
    assert "am" in codes, "Must include Amharic"
    assert "mi" in codes, "Must include Māori"
    assert "th" in codes, "Must include Thai (scriptio continua inefficiency)"

    # Thai token count should be significantly higher than English
    en_sample = next(item for item in data if item["code"] == "en")
    th_sample = next(item for item in data if item["code"] == "th")

    assert th_sample["tokens_cl100k"] > en_sample["tokens_cl100k"] * 4
    assert th_sample["cost_multiplier_vs_english_cl100k"] >= 4.0


def test_collision_presets_integrity():
    """Verify data/collision_presets.json includes all requested categories."""
    preset_file = settings.data_dir / "collision_presets.json"
    assert preset_file.exists(), "collision_presets.json must exist"

    with open(preset_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    categories = {item["category"] for item in data}
    expected_categories = {
        "homograph",
        "false_friend",
        "space_shift",
        "letter_counting",
        "math_split",
        "homoglyph",
        "scriptio_continua",
    }
    assert expected_categories.issubset(categories), (
        f"Missing categories: {expected_categories - categories}"
    )
