"""Data generator module to construct and validate benchmark datasets and collision presets."""

import json
import logging
from pathlib import Path
from src.config import settings
from src.core.tokenizer_service import TokenizerService
from src.schemas import LanguageSample, CollisionPreset, ComparisonItem

logger = logging.getLogger(__name__)


RAW_LANGUAGE_SAMPLES: list[dict] = [
    {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "script": "Latin",
        "family": "Indo-European (Germanic)",
        "text": "All human beings are born free and equal in dignity and rights.",
        "is_minority_or_underrepresented": False,
        "notes": "Baseline training language. High vocabulary compression (~1.08 tokens/word).",
    },
    {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "script": "Latin",
        "family": "Indo-European (Romance)",
        "text": "Todos los seres humanos nacen libres e iguales en dignidad y derechos.",
        "is_minority_or_underrepresented": False,
        "notes": "Latin alphabet with extensive representation in common crawl corpora.",
    },
    {
        "code": "fr",
        "name": "French",
        "native_name": "Français",
        "script": "Latin",
        "family": "Indo-European (Romance)",
        "text": "Tous les êtres humains naissent libres et égaux en dignité et en droits.",
        "is_minority_or_underrepresented": False,
        "notes": "Well-represented European language with moderate subword splitting for accents.",
    },
    {
        "code": "de",
        "name": "German",
        "native_name": "Deutsch",
        "script": "Latin",
        "family": "Indo-European (Germanic)",
        "text": "Alle Menschen sind frei und gleich an Würde und Rechten geboren.",
        "is_minority_or_underrepresented": False,
        "notes": "Compound words occasionally split into 2-3 morphemes, but basic vocabulary is dense.",
    },
    {
        "code": "mi",
        "name": "Māori",
        "native_name": "Te Reo Māori",
        "script": "Latin (with macrons)",
        "family": "Austronesian (Polynesian)",
        "text": "Ko te katoa o nga tangata i whanau mai i runga i te rangatiratanga me nga mana orite.",
        "is_minority_or_underrepresented": True,
        "notes": "Indigenous language of Aotearoa New Zealand. Uses Latin characters but low web frequency.",
    },
    {
        "code": "sw",
        "name": "Swahili",
        "native_name": "Kiswahili",
        "script": "Latin",
        "family": "Niger-Congo (Bantu)",
        "text": "Watu wote wamezaliwa huru, hadhi na haki zao ni sawa.",
        "is_minority_or_underrepresented": True,
        "notes": "Major East African lingua franca. Agglutinative morphology leads to subword fragmentation.",
    },
    {
        "code": "ru",
        "name": "Russian",
        "native_name": "Русский",
        "script": "Cyrillic",
        "family": "Indo-European (Slavic)",
        "text": "Все люди рождаются свободными и равными в своем достоинстве и правах.",
        "is_minority_or_underrepresented": False,
        "notes": "Non-Latin script with large web presence. Cyrillic tokens exist in GPT-4 vocab.",
    },
    {
        "code": "ar",
        "name": "Arabic",
        "native_name": "العربية",
        "script": "Arabic",
        "family": "Afroasiatic (Semitic)",
        "text": "يولد جميع الناس أحراراً متساوين في الكرامة والحقوق.",
        "is_minority_or_underrepresented": False,
        "notes": "Abjad script with rich morphology. Highly impacted in older tokenizers.",
    },
    {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "script": "Devanagari",
        "family": "Indo-European (Indo-Aryan)",
        "text": "सभी मनुष्यों को गौरव और अधिकारों के मामले में जन्मजात स्वतन्त्रता और समानता प्राप्त है।",
        "is_minority_or_underrepresented": True,
        "notes": "600M+ speakers worldwide, yet heavily penalized (~5.6 t/w in GPT-4, 5x more tokens than English).",
    },
    {
        "code": "bn",
        "name": "Bengali",
        "native_name": "বাংলা",
        "script": "Bengali",
        "family": "Indo-European (Indo-Aryan)",
        "text": "সমস্ত মানুষ স্বাধীনভাবে সমান মর্যাদা এবং অধিকার নিয়ে জন্মগ্রহণ করে।",
        "is_minority_or_underrepresented": True,
        "notes": "300M+ native speakers; complex conjunct characters split into multiple UTF-8 bytes.",
    },
    {
        "code": "zh",
        "name": "Chinese (Simplified)",
        "native_name": "简体中文",
        "script": "Hanzi (Ideographic)",
        "family": "Sino-Tibetan",
        "text": "人人生而自由，在尊严和权利上一律平等。",
        "is_minority_or_underrepresented": False,
        "notes": "Most characters are single tokens in cl100k/o200k, but character-to-word ratio differs.",
    },
    {
        "code": "ja",
        "name": "Japanese",
        "native_name": "日本語",
        "script": "Kanji / Hiragana / Katakana",
        "family": "Japonic",
        "text": "すべての人間は、生まれながらにして自由であり、かつ、尊厳と権利とについて平等である。",
        "is_minority_or_underrepresented": False,
        "notes": "Mixed scripts; Kanji characters are usually preserved while hiragana/particles split.",
    },
    {
        "code": "am",
        "name": "Amharic",
        "native_name": "አማርኛ",
        "script": "Ge'ez (Ethiopic)",
        "family": "Afroasiatic (Semitic)",
        "text": "የሰው ልጆች ሁሉ ሲወለዱ ነፃና በክብርና በመብቶችም እኩል ሆነው የተወለዱ ናቸው።",
        "is_minority_or_underrepresented": True,
        "notes": "Official language of Ethiopia (~32M speakers). Abugida script; severe token fragmentation (~11 t/w).",
    },
    {
        "code": "my",
        "name": "Burmese",
        "native_name": "မြန်မာစာ",
        "script": "Myanmar",
        "family": "Sino-Tibetan",
        "text": "လူတိုင်းသည် လွတ်လပ်စွာ မွေးဖွားလာကြပြီး ဂုဏ်သိက္ခာနှင့် အခွင့်အရေးများတွင် တန်းတူညီမျှကြသည်။",
        "is_minority_or_underrepresented": True,
        "notes": "Extreme token tax: 30.0 tokens/word in GPT-4 (~14x more expensive than English!).",
    },
    {
        "code": "chr",
        "name": "Cherokee",
        "native_name": "ᏣᎳᎩ",
        "script": "Cherokee Syllabary",
        "family": "Iroquoian",
        "text": "ᏂᎦᏛ ᎠᏂᏴᏫ ᏂᎨᎫᏓᎸᎾ ᎠᎴ ᎤᏂᏠᏱ ᎤᎾᏕᎿ ᏚᏳᎧᏛ ᎢᏳᎾᏛᏁᎵᏓᏍᏗ.",
        "is_minority_or_underrepresented": True,
        "notes": "Indigenous North American language. Almost every syllable splits into 3-4 raw fallback bytes.",
    },
    {
        "code": "th",
        "name": "Thai",
        "native_name": "ภาษาไทย",
        "script": "Thai (Scriptio Continua)",
        "family": "Kra-Dai",
        "text": "เราทุกคนเกิดมาอย่างอิสระและมีความเท่าเทียมกันในเกียรติศักดิ์และสิทธิ",
        "word_count": 15,
        "is_minority_or_underrepresented": True,
        "notes": "Written without spaces (scriptio continua) using 3-byte UTF-8 chars. A 15-word sentence explodes into 65 tokens in GPT-4 (5.0x English) and 136 tokens in GPT-3 (10.5x English) due to single-letter fragmentation and byte fallbacks.",
    },
]


def generate_language_dataset(service: TokenizerService | None = None) -> list[LanguageSample]:
    """Generate verified multi-language benchmark dataset."""
    svc = service or TokenizerService()
    samples: list[LanguageSample] = []

    # English baseline tokens
    en_raw = next(s for s in RAW_LANGUAGE_SAMPLES if s["code"] == "en")
    en_res_cl = svc.tokenize(en_raw["text"], encoding="cl100k_base")
    en_res_o2 = svc.tokenize(en_raw["text"], encoding="o200k_base")
    en_tokens_cl = en_res_cl.token_count
    en_tokens_o2 = en_res_o2.token_count

    for raw in RAW_LANGUAGE_SAMPLES:
        res_cl = svc.tokenize(raw["text"], encoding="cl100k_base")
        res_o2 = svc.tokenize(raw["text"], encoding="o200k_base")
        res_r5 = svc.tokenize(raw["text"], encoding="r50k_base")

        words = raw.get("word_count") or len(raw["text"].split())
        word_count = words if words > 0 else 1

        tpw_cl = round(res_cl.token_count / word_count, 2)
        tpw_o2 = round(res_o2.token_count / word_count, 2)

        mult_cl = round(res_cl.token_count / en_tokens_cl, 2)
        mult_o2 = round(res_o2.token_count / en_tokens_o2, 2)

        sample = LanguageSample(
            code=raw["code"],
            name=raw["name"],
            native_name=raw["native_name"],
            script=raw["script"],
            family=raw["family"],
            text=raw["text"],
            word_count=word_count,
            char_count=len(raw["text"]),
            tokens_cl100k=res_cl.token_count,
            tokens_o200k=res_o2.token_count,
            tokens_r50k=res_r5.token_count,
            tpw_cl100k=tpw_cl,
            tpw_o200k=tpw_o2,
            cost_multiplier_vs_english_cl100k=mult_cl,
            cost_multiplier_vs_english_o200k=mult_o2,
            is_minority_or_underrepresented=raw["is_minority_or_underrepresented"],
            notes=raw["notes"],
        )
        samples.append(sample)

    return samples


def generate_collision_presets(service: TokenizerService | None = None) -> list[CollisionPreset]:
    """Generate verified collision and quirk presets."""
    svc = service or TokenizerService()

    def make_items(pairs: list[tuple[str, str, str]]) -> list[ComparisonItem]:
        items: list[ComparisonItem] = []
        for label, text, meaning in pairs:
            res = svc.tokenize(text, encoding="cl100k_base")
            items.append(
                ComparisonItem(
                    label=label,
                    input_text=text,
                    token_ids=res.token_ids,
                    token_count=res.token_count,
                    tokens_str=[p.text for p in res.pieces],
                    meaning_or_context=meaning,
                )
            )
        return items

    presets: list[CollisionPreset] = [
        CollisionPreset(
            id="homographs-lead",
            category="homograph",
            title="Homograph Blindspot: 'lead' (Metal vs Guide)",
            subtitle="Identical Token ID 27152 for two fundamentally distinct words",
            explanation=(
                "In English, 'lead' (/lɛd/, heavy toxic metal element Pb) and 'lead' (/liːd/, verb to guide or "
                "be in first place) have completely different pronunciations, origins, and meanings. "
                "Because BPE operates purely on character sequences, both words receive the EXACT SAME token ID: 27152. "
                "At the transformer's input embedding layer, there is only a single static vector for both concepts."
            ),
            consequence_for_llms=(
                "In low-context or ambiguous prompts (e.g. 'Can lead be dissolved?'), the LLM has no initial "
                "semantic clue whether you mean chemistry or team management and must infer it purely from surrounding "
                "tokens. If context is missing, it easily hallucinates or conflates the two meanings."
            ),
            items=make_items(
                [
                    ("Metal (Pb)", "lead", "Heavy toxic metal element, chemical symbol Pb"),
                    ("Guide / Front", "lead", "Verb meaning to guide, direct, or hold first place"),
                ]
            ),
        ),
        CollisionPreset(
            id="false-friends-gift",
            category="false_friend",
            title="Cross-Lingual False Friend: 'gift' (EN: Present vs DE: Poison)",
            subtitle="Identical Token ID 53430 shared across two languages with opposite meanings",
            explanation=(
                "In English, 'gift' means a kind present or offering. In German, 'Gift' (or lowercased 'gift') "
                "means DEADLY POISON! Because subword vocabularies are language-agnostic, the string 'gift' is "
                "assigned token ID 53430 in GPT-4 regardless of which language is being spoken."
            ),
            consequence_for_llms=(
                "In multilingual or code-switched contexts, LLMs can commit hilarious and dangerous blunders: "
                "e.g. translating 'Er hat mir ein Gift gegeben' as 'He gave me a present' or warning English readers "
                "that a birthday gift is lethal."
            ),
            items=make_items(
                [
                    ("English 'gift'", "gift", "A kind present or blessing"),
                    ("German 'gift'", "gift", "Deadly poison or venom (das Gift)"),
                ]
            ),
        ),
        CollisionPreset(
            id="false-friends-pain",
            category="false_friend",
            title="Cross-Lingual False Friend: 'pain' (EN: Agony vs FR: Bread)",
            subtitle="Identical Token ID 92724 shared between English suffering and French food",
            explanation=(
                "In French, 'pain' is bread (a staple food like a baguette). In English, 'pain' is intense physical "
                "or emotional agony. The tokenizer produces the exact token ID 92724 for both."
            ),
            consequence_for_llms=(
                "Bilingual prompts such as 'I eat pain every morning' cause language models to struggle with "
                "metaphor vs literal translation, often generating confusion or safety flags about self-harm."
            ),
            items=make_items(
                [
                    ("English 'pain'", "pain", "Physical suffering, hurt, or ache"),
                    ("French 'pain'", "pain", "Bread, baguette, or loaf (staple food)"),
                ]
            ),
        ),
        CollisionPreset(
            id="false-friends-chat",
            category="false_friend",
            title="Cross-Lingual False Friend: 'chat' (EN: Talk vs FR: Cat)",
            subtitle="Identical Token ID 9884 shared between talking and a feline pet",
            explanation=(
                "In English, 'chat' is an informal conversation. In French, 'chat' is a feline animal (a cat). "
                "Both strings produce token ID 9884 in GPT-4."
            ),
            consequence_for_llms=(
                "Prompts like 'Let us have a chat' or 'Regarde ce chat' can cross-contaminate semantic embeddings "
                "in bilingual dialogues, causing the model to interpret 'chatting' as handling an animal."
            ),
            items=make_items(
                [
                    ("English 'chat'", "chat", "Casual, friendly conversation"),
                    ("French 'chat'", "chat", "A cat, feline pet (le chat)"),
                ]
            ),
        ),
        CollisionPreset(
            id="space-shifts-apple",
            category="space_shift",
            title="The Leading Space & Capitalization Trap",
            subtitle="The same semantic word 'apple' splits into 5 completely disjoint token IDs!",
            explanation=(
                "To human readers, ' apple', 'apple', 'Apple', ' Apple', and 'APPLE' are all the exact same fruit. "
                "To an LLM tokenizer, byte-pair encoding treats leading whitespace and capitalization as entirely "
                "different strings! ' apple' is 24149, 'apple' is 23182, ' Apple' is 8325, 'Apple' is 27665, and 'APPLE' is 47285."
            ),
            consequence_for_llms=(
                "Because each token ID has a completely independent weight vector in the transformer, minor formatting "
                "changes (e.g. an extra trailing space at the end of a prompt) can dramatically alter the model's next-token "
                "probabilities, causing prompt brittleness and unexpected answer flips."
            ),
            items=make_items(
                [
                    (
                        " apple (with space)",
                        " apple",
                        "Leading whitespace token (standard in sentences)",
                    ),
                    ("apple (no space)", "apple", "Isolated word without leading whitespace"),
                    (" Apple (cap + space)", " Apple", "Capitalized with leading space"),
                    ("Apple (cap no space)", "Apple", "Capitalized isolated word"),
                    ("APPLE (all caps)", "APPLE", "All caps uppercase token"),
                ]
            ),
        ),
        CollisionPreset(
            id="strawberry-counting",
            category="letter_counting",
            title="The 'Strawberry' Paradox: Why LLMs Cannot Count Letters",
            subtitle="'strawberry' is parsed as ['str', 'aw', 'berry'] - the model never sees individual letters!",
            explanation=(
                "The notorious failure where GPT-4 insists that 'strawberry' has only two 'r's (or cannot reverse words) "
                "is directly caused by tokenization. To the model, 'strawberry' is compressed into tokens 496 ('str'), "
                "675 ('aw'), and 15717 ('berry'). The individual characters 's-t-r-a-w-b-e-r-r-y' DO NOT EXIST in the transformer's input!"
            ),
            consequence_for_llms=(
                "To count letters, the LLM must indirectly hallucinate an internal character-by-character spelling representation. "
                "Whenever a word is absorbed into a single subword token, character-level tasks like spelling, letter counting, "
                "anagrams, and word reversals become prone to failure."
            ),
            items=make_items(
                [
                    ("strawberry", "strawberry", "Tokenized as 3 chunks: ['str', 'aw', 'berry']"),
                    ("Strawberry", "Strawberry", "Tokenized as: ['Str', 'aw', 'berry']"),
                    (
                        "s-t-r-a-w-b-e-r-r-y",
                        "s-t-r-a-w-b-e-r-r-y",
                        "Hyphenated characters: model finally sees letters!",
                    ),
                ]
            ),
        ),
        CollisionPreset(
            id="decimal-math-911",
            category="math_split",
            title="The Decimal Math Trap: 'Is 9.11 bigger than 9.9?'",
            subtitle="Arbitrary number tokenization creates deceptive numerical illusions",
            explanation=(
                "Why do LLMs notoriously claim that 9.11 is larger than 9.9? Look at the token splits: "
                "'9.11' is split into ['9', '.', '11'] (tokens 24, 13, 806). "
                "'9.9' is split into ['9', '.', '9'] (tokens 24, 13, 24). "
                "The model compares the subword token '11' with '9'. In integers, 11 > 9, so the model's pattern matching trips!"
            ),
            consequence_for_llms=(
                "Tokenizers chunk numbers unpredictably based on byte frequency rather than place value (ones, tens, hundreds). "
                "This causes catastrophic errors in arithmetic, decimal comparisons, and financial modeling."
            ),
            items=make_items(
                [
                    (
                        "9.11",
                        "9.11",
                        "Tokenized as ['9', '.', '11'] -> Token 11 is mathematically deceptive",
                    ),
                    ("9.9", "9.9", "Tokenized as ['9', '.', '9'] -> Token 9"),
                    ("9.90", "9.90", "Normalized with trailing zero: ['9', '.', '90']"),
                ]
            ),
        ),
        CollisionPreset(
            id="homoglyph-attack",
            category="homoglyph",
            title="The Homoglyph Disguise: Latin 'apple' vs Cyrillic 'аpple'",
            subtitle="Visually identical to humans, completely different token streams to LLMs",
            explanation=(
                "Type Latin 'apple' (ASCII 'a', code 97). Now type Cyrillic 'аpple' (Cyrillic 'а', Unicode U+0430). "
                "On screen, both strings look 100% IDENTICAL. But in the tokenizer, Latin 'apple' is a single word token (23182), "
                "while Cyrillic 'аpple' explodes into 3 tokens: [1506, 604, 273] because the Cyrillic byte sequence triggers subword breakdown!"
            ),
            consequence_for_llms=(
                "Adversaries exploit this for prompt injection and bypassing LLM guardrails: "
                "a banned word or brand name can be rendered with a Cyrillic homoglyph, slipping past keyword filters and embedding classifiers "
                "while remaining completely readable to human victims."
            ),
            items=make_items(
                [
                    ("Latin 'apple'", "apple", "Standard English word (1 token: 23182)"),
                    ("Cyrillic 'аpple'", "аpple", "Cyrillic 'а' (3 tokens: 1506, 604, 273)"),
                ]
            ),
        ),
        CollisionPreset(
            id="thai-scriptio-continua-ambiguity",
            category="scriptio_continua",
            title="Thai Scriptio Continua: Cross-Boundary Token Merges & Ambiguities",
            subtitle="Lack of word spaces causes BPE to merge across word borders and confuse fundamental concepts",
            explanation=(
                "Thai is written without spaces between words (scriptio continua). Because standard LLM tokenizers "
                "rely on greedy byte frequencies rather than morphological word boundaries, Thai text suffers from "
                "two critical failures: (1) Cross-Boundary Merging: BPE merges the tail of one word with the head of the "
                "next word into an unintended subword (e.g. 'หา' [visit] + 'มเหสี' [queen consort] merges into 'หาม' [stretcher/taboo]), "
                "scrambling the model's semantic interpretation. (2) Word Segmentation Ambiguity: A string like 'ตากลม' "
                "can mean either 'ตา-กลม' (round eyes) or 'ตาก-ลม' (basking in the wind). In cl100k it shatters into 5 individual letters; "
                "in o200k, BPE binds 'ต' + 'าก' into 'ตาก' (bask), locking the model into one interpretation and blinding it to 'round eyes'."
            ),
            consequence_for_llms=(
                "LLMs frequently misinterpret Thai questions, hallucinate incorrect translations (e.g., mistaking visiting royalty for "
                "carrying corpses on a stretcher), and conflate tonal concepts (like ขาว [white], ข่าว [news], and ข้าว [rice]) "
                "because tone marks and combining vowels get detached into isolated byte tokens."
            ),
            items=make_items(
                [
                    (
                        "ตา-กลม (Round Eyes vs Wind)",
                        "ตากลม",
                        "Ambiguous segmentation: 'ตา-กลม' (round eyes: ตา=eye, กลม=round) vs 'ตาก-ลม' (bask in wind: ตาก=air out, ลม=wind)",
                    ),
                    (
                        "ไป-หา-มเหสี (Visit Queen Consort)",
                        "ไปหามเหสี",
                        "Tokenizer merges 'า' + 'ม' into 'าม', forming 'หาม' (stretcher/taboo) and destroying the concept of 'มเหสี' (queen consort)",
                    ),
                    (
                        "ขาว / ข่าว / ข้าว (Tone Confusion)",
                        "ขาว ข่าว ข้าว",
                        "Tonal shift: 'ขาว' (white) vs 'ข่าว' (news) vs 'ข้าว' (rice) - separated tone marks trigger conceptual hallucination",
                    ),
                ]
            ),
        ),
    ]

    return presets


def export_all_datasets(output_dir: Path | None = None) -> None:
    """Generate and export verified JSON datasets for web app."""
    target_dir = output_dir or settings.data_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    svc = TokenizerService()

    # 1. Languages
    languages = generate_language_dataset(svc)
    lang_file = target_dir / "languages.json"
    with open(lang_file, "w", encoding="utf-8") as f:
        json.dump([lang.model_dump() for lang in languages], f, ensure_ascii=False, indent=2)

    # 2. Collisions
    presets = generate_collision_presets(svc)
    preset_file = target_dir / "collision_presets.json"
    with open(preset_file, "w", encoding="utf-8") as f:
        json.dump([p.model_dump() for p in presets], f, ensure_ascii=False, indent=2)

    logger.info("Successfully exported datasets to %s", target_dir)


if __name__ == "__main__":
    export_all_datasets()
