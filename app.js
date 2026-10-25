/**
 * LLM Tokenization Anatomy & Linguistic Bias Explorer
 * Core Application Controller
 */

// Embedded fallback datasets to ensure 100% offline functionality if browser blocks local fetch on file://
const EMBEDDED_LANGUAGES = [
  {
    "code": "en",
    "name": "English",
    "native_name": "English",
    "script": "Latin",
    "family": "Indo-European (Germanic)",
    "text": "All human beings are born free and equal in dignity and rights.",
    "word_count": 12,
    "char_count": 63,
    "tokens_cl100k": 13,
    "tokens_o200k": 13,
    "tokens_r50k": 13,
    "tpw_cl100k": 1.08,
    "tpw_o200k": 1.08,
    "cost_multiplier_vs_english_cl100k": 1.0,
    "cost_multiplier_vs_english_o200k": 1.0,
    "is_minority_or_underrepresented": false,
    "notes": "Baseline training language. High vocabulary compression (~1.08 tokens/word)."
  },
  {
    "code": "es",
    "name": "Spanish",
    "native_name": "Español",
    "script": "Latin",
    "family": "Indo-European (Romance)",
    "text": "Todos los seres humanos nacen libres e iguales en dignidad y derechos.",
    "word_count": 12,
    "char_count": 70,
    "tokens_cl100k": 19,
    "tokens_o200k": 15,
    "tokens_r50k": 22,
    "tpw_cl100k": 1.58,
    "tpw_o200k": 1.25,
    "cost_multiplier_vs_english_cl100k": 1.46,
    "cost_multiplier_vs_english_o200k": 1.15,
    "is_minority_or_underrepresented": false,
    "notes": "Latin alphabet with extensive representation in common crawl corpora."
  },
  {
    "code": "fr",
    "name": "French",
    "native_name": "Français",
    "script": "Latin",
    "family": "Indo-European (Romance)",
    "text": "Tous les êtres humains naissent libres et égaux en dignité et en droits.",
    "word_count": 13,
    "char_count": 73,
    "tokens_cl100k": 19,
    "tokens_o200k": 16,
    "tokens_r50k": 21,
    "tpw_cl100k": 1.46,
    "tpw_o200k": 1.23,
    "cost_multiplier_vs_english_cl100k": 1.46,
    "cost_multiplier_vs_english_o200k": 1.23,
    "is_minority_or_underrepresented": false,
    "notes": "Well-represented European language with moderate subword splitting for accents."
  },
  {
    "code": "de",
    "name": "German",
    "native_name": "Deutsch",
    "script": "Latin",
    "family": "Indo-European (Germanic)",
    "text": "Alle Menschen sind frei und gleich an Würde und Rechten geboren.",
    "word_count": 11,
    "char_count": 64,
    "tokens_cl100k": 16,
    "tokens_o200k": 14,
    "tokens_r50k": 18,
    "tpw_cl100k": 1.45,
    "tpw_o200k": 1.27,
    "cost_multiplier_vs_english_cl100k": 1.23,
    "cost_multiplier_vs_english_o200k": 1.08,
    "is_minority_or_underrepresented": false,
    "notes": "Compound words occasionally split into 2-3 morphemes, but basic vocabulary is dense."
  },
  {
    "code": "mi",
    "name": "Māori",
    "native_name": "Te Reo Māori",
    "script": "Latin (with macrons)",
    "family": "Austronesian (Polynesian)",
    "text": "Ko te katoa o nga tangata i whanau mai i runga i te rangatiratanga me nga mana orite.",
    "word_count": 18,
    "char_count": 85,
    "tokens_cl100k": 31,
    "tokens_o200k": 24,
    "tokens_r50k": 33,
    "tpw_cl100k": 1.72,
    "tpw_o200k": 1.33,
    "cost_multiplier_vs_english_cl100k": 2.38,
    "cost_multiplier_vs_english_o200k": 1.85,
    "is_minority_or_underrepresented": true,
    "notes": "Indigenous language of Aotearoa New Zealand. Uses Latin characters but lower web frequency."
  },
  {
    "code": "sw",
    "name": "Swahili",
    "native_name": "Kiswahili",
    "script": "Latin",
    "family": "Niger-Congo (Bantu)",
    "text": "Watu wote wamezaliwa huru, hadhi na haki zao ni sawa.",
    "word_count": 10,
    "char_count": 53,
    "tokens_cl100k": 23,
    "tokens_o200k": 17,
    "tokens_r50k": 25,
    "tpw_cl100k": 2.30,
    "tpw_o200k": 1.70,
    "cost_multiplier_vs_english_cl100k": 1.77,
    "cost_multiplier_vs_english_o200k": 1.31,
    "is_minority_or_underrepresented": true,
    "notes": "Major East African lingua franca. Agglutinative morphology leads to subword fragmentation."
  },
  {
    "code": "ru",
    "name": "Russian",
    "native_name": "Русский",
    "script": "Cyrillic",
    "family": "Indo-European (Slavic)",
    "text": "Все люди рождаются свободными и равными в своем достоинстве и правах.",
    "word_count": 10,
    "char_count": 68,
    "tokens_cl100k": 28,
    "tokens_o200k": 19,
    "tokens_r50k": 35,
    "tpw_cl100k": 2.80,
    "tpw_o200k": 1.90,
    "cost_multiplier_vs_english_cl100k": 2.15,
    "cost_multiplier_vs_english_o200k": 1.46,
    "is_minority_or_underrepresented": false,
    "notes": "Non-Latin script with large web presence. Cyrillic tokens exist in GPT-4 vocab."
  },
  {
    "code": "ar",
    "name": "Arabic",
    "native_name": "العربية",
    "script": "Arabic",
    "family": "Afroasiatic (Semitic)",
    "text": "يولد جميع الناس أحراراً متساوين في الكرامة والحقوق.",
    "word_count": 8,
    "char_count": 51,
    "tokens_cl100k": 37,
    "tokens_o200k": 18,
    "tokens_r50k": 42,
    "tpw_cl100k": 4.62,
    "tpw_o200k": 2.25,
    "cost_multiplier_vs_english_cl100k": 2.85,
    "cost_multiplier_vs_english_o200k": 1.38,
    "is_minority_or_underrepresented": false,
    "notes": "Abjad script with rich morphology. Highly impacted in older tokenizers."
  },
  {
    "code": "hi",
    "name": "Hindi",
    "native_name": "हिन्दी",
    "script": "Devanagari",
    "family": "Indo-European (Indo-Aryan)",
    "text": "सभी मनुष्यों को गौरव और अधिकारों के मामले में जन्मजात स्वतन्त्रता और समानता प्राप्त है।",
    "word_count": 15,
    "char_count": 87,
    "tokens_cl100k": 84,
    "tokens_o200k": 25,
    "tokens_r50k": 92,
    "tpw_cl100k": 5.60,
    "tpw_o200k": 1.67,
    "cost_multiplier_vs_english_cl100k": 6.46,
    "cost_multiplier_vs_english_o200k": 1.92,
    "is_minority_or_underrepresented": true,
    "notes": "600M+ speakers worldwide, yet heavily penalized (~5.6 t/w in GPT-4, 6.5x more expensive than English!)."
  },
  {
    "code": "bn",
    "name": "Bengali",
    "native_name": "বাংলা",
    "script": "Bengali",
    "family": "Indo-European (Indo-Aryan)",
    "text": "সমস্ত মানুষ স্বাধীনভাবে সমান মর্যাদা এবং অধিকার নিয়ে জন্মগ্রহণ করে।",
    "word_count": 10,
    "char_count": 67,
    "tokens_cl100k": 68,
    "tokens_o200k": 23,
    "tokens_r50k": 76,
    "tpw_cl100k": 6.80,
    "tpw_o200k": 2.30,
    "cost_multiplier_vs_english_cl100k": 5.23,
    "cost_multiplier_vs_english_o200k": 1.77,
    "is_minority_or_underrepresented": true,
    "notes": "300M+ native speakers; complex conjunct characters split into multiple UTF-8 bytes."
  },
  {
    "code": "zh",
    "name": "Chinese",
    "native_name": "简体中文",
    "script": "Hanzi (Ideographic)",
    "family": "Sino-Tibetan",
    "text": "人人生而自由，在尊严和权利上一律平等。",
    "word_count": 1,
    "char_count": 19,
    "tokens_cl100k": 17,
    "tokens_o200k": 12,
    "tokens_r50k": 24,
    "tpw_cl100k": 17.0,
    "tpw_o200k": 12.0,
    "cost_multiplier_vs_english_cl100k": 1.31,
    "cost_multiplier_vs_english_o200k": 0.92,
    "is_minority_or_underrepresented": false,
    "notes": "Characters are mostly single tokens in cl100k/o200k, with high semantic density per token."
  },
  {
    "code": "ja",
    "name": "Japanese",
    "native_name": "日本語",
    "script": "Kanji / Kana",
    "family": "Japonic",
    "text": "すべての人間は、生まれながらにして自由であり、かつ、尊厳と権利とについて平等である。",
    "word_count": 1,
    "char_count": 47,
    "tokens_cl100k": 36,
    "tokens_o200k": 24,
    "tokens_r50k": 45,
    "tpw_cl100k": 36.0,
    "tpw_o200k": 24.0,
    "cost_multiplier_vs_english_cl100k": 2.77,
    "cost_multiplier_vs_english_o200k": 1.85,
    "is_minority_or_underrepresented": false,
    "notes": "Kanji is well-compressed while grammatical particles and hiragana split."
  },
  {
    "code": "am",
    "name": "Amharic",
    "native_name": "አማርኛ",
    "script": "Ge'ez (Ethiopic)",
    "family": "Afroasiatic (Semitic)",
    "text": "የሰው ልጆች ሁሉ ሲወለዱ ነፃና በክብርና በመብቶችም እኩል ሆነው የተወለዱ ናቸው።",
    "word_count": 11,
    "char_count": 51,
    "tokens_cl100k": 122,
    "tokens_o200k": 92,
    "tokens_r50k": 130,
    "tpw_cl100k": 11.09,
    "tpw_o200k": 8.36,
    "cost_multiplier_vs_english_cl100k": 9.38,
    "cost_multiplier_vs_english_o200k": 7.08,
    "is_minority_or_underrepresented": true,
    "notes": "Official language of Ethiopia (~32M speakers). Abugida script; severe token fragmentation (~11 t/w, 9.4x English cost!)."
  },
  {
    "code": "my",
    "name": "Burmese",
    "native_name": "မြန်မာစာ",
    "script": "Myanmar",
    "family": "Sino-Tibetan",
    "text": "လူတိုင်းသည် လွတ်လပ်စွာ မွေးဖွားလာကြပြီး ဂုဏ်သိက္ခာနှင့် အခွင့်အရေးများတွင် တန်းတူညီမျှကြသည်။",
    "word_count": 6,
    "char_count": 92,
    "tokens_cl100k": 180,
    "tokens_o200k": 53,
    "tokens_r50k": 195,
    "tpw_cl100k": 30.00,
    "tpw_o200k": 8.83,
    "cost_multiplier_vs_english_cl100k": 13.85,
    "cost_multiplier_vs_english_o200k": 4.08,
    "is_minority_or_underrepresented": true,
    "notes": "Extreme token tax: 30.0 tokens/word in GPT-4 (13.8x more expensive than English!)."
  },
  {
    "code": "chr",
    "name": "Cherokee",
    "native_name": "ᏣᎳᎩ",
    "script": "Cherokee Syllabary",
    "family": "Iroquoian",
    "text": "ᏂᎦᏛ ᎠᏂᏴᏫ ᏂᎨᎫᏓᎸᎾ ᎠᎴ ᎤᏂᏠᏱ ᎤᎾᏕᎿ ᏚᏳᎧᏛ ᎢᏳᎾᏛᏁᎵᏓᏍᏗ.",
    "word_count": 6,
    "char_count": 51,
    "tokens_cl100k": 88,
    "tokens_o200k": 62,
    "tokens_r50k": 95,
    "tpw_cl100k": 14.67,
    "tpw_o200k": 10.33,
    "cost_multiplier_vs_english_cl100k": 6.77,
    "cost_multiplier_vs_english_o200k": 4.77,
    "is_minority_or_underrepresented": true,
    "notes": "Indigenous North American language. Almost every syllable splits into 3-4 raw fallback bytes."
  }
];

const EMBEDDED_PRESETS = [
  {
    "id": "homographs-lead",
    "category": "homograph",
    "title": "Homograph Blindspot: 'lead' (Metal vs Guide)",
    "subtitle": "Identical Token ID 27152 for two fundamentally distinct words",
    "explanation": "In English, 'lead' (/lɛd/, heavy toxic metal element Pb) and 'lead' (/liːd/, verb to guide or be in first place) have completely different pronunciations, origins, and meanings. Because BPE operates purely on character sequences, both words receive the EXACT SAME token ID: 27152. At the transformer's input embedding layer, there is only a single static vector for both concepts.",
    "consequence_for_llms": "In low-context or ambiguous prompts (e.g. 'Can lead be dissolved?'), the LLM has no initial semantic clue whether you mean chemistry or team management and must infer it purely from surrounding tokens. If context is missing, it easily hallucinates or conflates the two meanings.",
    "items": [
      {
        "label": "Metal (Pb)",
        "input_text": "lead",
        "token_ids": [27152],
        "token_count": 1,
        "tokens_str": ["lead"],
        "meaning_or_context": "Heavy toxic metal element, chemical symbol Pb (/lɛd/)"
      },
      {
        "label": "Guide / Front",
        "input_text": "lead",
        "token_ids": [27152],
        "token_count": 1,
        "tokens_str": ["lead"],
        "meaning_or_context": "Verb meaning to guide, direct, or hold first place (/liːd/)"
      }
    ]
  },
  {
    "id": "false-friends-gift",
    "category": "false_friend",
    "title": "Cross-Lingual False Friend: 'gift' (EN: Present vs DE: Poison)",
    "subtitle": "Identical Token ID 53430 shared across two languages with opposite meanings",
    "explanation": "In English, 'gift' means a kind present or offering. In German, 'Gift' (or lowercased 'gift') means DEADLY POISON! Because subword vocabularies are language-agnostic, the string 'gift' is assigned token ID 53430 in GPT-4 regardless of which language is being spoken.",
    "consequence_for_llms": "In multilingual or code-switched contexts, LLMs can commit hilarious and dangerous blunders: e.g. translating 'Er hat mir ein Gift gegeben' as 'He gave me a present' or warning English readers that a birthday gift is lethal.",
    "items": [
      {
        "label": "English 'gift'",
        "input_text": "gift",
        "token_ids": [53430],
        "token_count": 1,
        "tokens_str": ["gift"],
        "meaning_or_context": "A thoughtful present, offering, or blessing"
      },
      {
        "label": "German 'gift'",
        "input_text": "gift",
        "token_ids": [53430],
        "token_count": 1,
        "tokens_str": ["gift"],
        "meaning_or_context": "Deadly poison or venom (das Gift)"
      }
    ]
  },
  {
    "id": "false-friends-pain",
    "category": "false_friend",
    "title": "Cross-Lingual False Friend: 'pain' (EN: Agony vs FR: Bread)",
    "subtitle": "Identical Token ID 92724 shared between English suffering and French food",
    "explanation": "In French, 'pain' is bread (a staple food like a baguette). In English, 'pain' is intense physical or emotional agony. The tokenizer produces the exact token ID 92724 for both.",
    "consequence_for_llms": "Bilingual prompts such as 'I eat pain every morning' cause language models to struggle with metaphor vs literal translation, often generating confusion or safety flags about self-harm.",
    "items": [
      {
        "label": "English 'pain'",
        "input_text": "pain",
        "token_ids": [92724],
        "token_count": 1,
        "tokens_str": ["pain"],
        "meaning_or_context": "Physical suffering, ache, or hurt"
      },
      {
        "label": "French 'pain'",
        "input_text": "pain",
        "token_ids": [92724],
        "token_count": 1,
        "tokens_str": ["pain"],
        "meaning_or_context": "Bread, baguette, or loaf (staple food)"
      }
    ]
  },
  {
    "id": "false-friends-chat",
    "category": "false_friend",
    "title": "Cross-Lingual False Friend: 'chat' (EN: Talk vs FR: Cat)",
    "subtitle": "Identical Token ID 9884 shared between talking and a feline pet",
    "explanation": "In English, 'chat' is an informal conversation. In French, 'chat' is a feline animal (a cat). Both strings produce token ID 9884 in GPT-4.",
    "consequence_for_llms": "Prompts like 'Let us have a chat' or 'Regarde ce chat' can cross-contaminate semantic embeddings in bilingual dialogues, causing the model to interpret 'chatting' as handling an animal.",
    "items": [
      {
        "label": "English 'chat'",
        "input_text": "chat",
        "token_ids": [9884],
        "token_count": 1,
        "tokens_str": ["chat"],
        "meaning_or_context": "Casual, friendly conversation"
      },
      {
        "label": "French 'chat'",
        "input_text": "chat",
        "token_ids": [9884],
        "token_count": 1,
        "tokens_str": ["chat"],
        "meaning_or_context": "A cat, feline pet (le chat)"
      }
    ]
  },
  {
    "id": "space-shifts-apple",
    "category": "space_shift",
    "title": "The Leading Space & Capitalization Trap",
    "subtitle": "The same semantic word 'apple' splits into 5 completely disjoint token IDs!",
    "explanation": "To human readers, ' apple', 'apple', 'Apple', ' Apple', and 'APPLE' are all the exact same fruit. To an LLM tokenizer, byte-pair encoding treats leading whitespace and capitalization as entirely different strings! ' apple' is 24149, 'apple' is 23182, ' Apple' is 8325, 'Apple' is 27665, and 'APPLE' is 47285.",
    "consequence_for_llms": "Because each token ID has a completely independent weight vector in the transformer, minor formatting changes (e.g. an extra trailing space at the end of a prompt) can dramatically alter the model's next-token probabilities, causing prompt brittleness and unexpected answer flips.",
    "items": [
      {
        "label": " apple (leading space)",
        "input_text": " apple",
        "token_ids": [24149],
        "token_count": 1,
        "tokens_str": [" apple"],
        "meaning_or_context": "Standard word with leading space in sentence"
      },
      {
        "label": "apple (no space)",
        "input_text": "apple",
        "token_ids": [23182],
        "token_count": 1,
        "tokens_str": ["apple"],
        "meaning_or_context": "Isolated word without space"
      },
      {
        "label": " Apple (cap + space)",
        "input_text": " Apple",
        "token_ids": [8325],
        "token_count": 1,
        "tokens_str": [" Apple"],
        "meaning_or_context": "Capitalized with leading space"
      },
      {
        "label": "Apple (cap no space)",
        "input_text": "Apple",
        "token_ids": [27665],
        "token_count": 1,
        "tokens_str": ["Apple"],
        "meaning_or_context": "Capitalized isolated word"
      },
      {
        "label": "APPLE (all caps)",
        "input_text": "APPLE",
        "token_ids": [47285],
        "token_count": 1,
        "tokens_str": ["APPLE"],
        "meaning_or_context": "Uppercase acronym or shouting"
      }
    ]
  },
  {
    "id": "strawberry-counting",
    "category": "letter_counting",
    "title": "The 'Strawberry' Paradox: Why LLMs Cannot Count Letters",
    "subtitle": "'strawberry' is parsed as ['str', 'aw', 'berry'] - the model never sees individual letters!",
    "explanation": "The notorious failure where GPT-4 insists that 'strawberry' has only two 'r's (or cannot reverse words) is directly caused by tokenization. To the model, 'strawberry' is compressed into tokens 496 ('str'), 675 ('aw'), and 15717 ('berry'). The individual characters 's-t-r-a-w-b-e-r-r-y' DO NOT EXIST in the transformer's input!",
    "consequence_for_llms": "To count letters, the LLM must indirectly hallucinate an internal character-by-character spelling representation. Whenever a word is absorbed into a single subword token, character-level tasks like spelling, letter counting, anagrams, and word reversals become prone to failure.",
    "items": [
      {
        "label": "strawberry (standard)",
        "input_text": "strawberry",
        "token_ids": [496, 675, 15717],
        "token_count": 3,
        "tokens_str": ["str", "aw", "berry"],
        "meaning_or_context": "Model sees 3 subwords, zero individual characters"
      },
      {
        "label": "Strawberry (capitalized)",
        "input_text": "Strawberry",
        "token_ids": [2645, 675, 15717],
        "token_count": 3,
        "tokens_str": ["Str", "aw", "berry"],
        "meaning_or_context": "Token 2645 replaces 496"
      },
      {
        "label": "s-t-r-a-w-b-e-r-r-y",
        "input_text": "s-t-r-a-w-b-e-r-r-y",
        "token_ids": [82, 12, 83, 12, 81, 12, 64, 12, 86, 12, 65, 12, 68, 12, 81, 12, 81, 12, 88],
        "token_count": 19,
        "tokens_str": ["s", "-", "t", "-", "r", "-", "a", "-", "w", "-", "b", "-", "e", "-", "r", "-", "r", "-", "y"],
        "meaning_or_context": "Hyphenation forces 1 token per letter, allowing LLMs to count accurately!"
      }
    ]
  },
  {
    "id": "decimal-math-911",
    "category": "math_split",
    "title": "The Decimal Math Trap: 'Is 9.11 bigger than 9.9?'",
    "subtitle": "Arbitrary number tokenization creates deceptive numerical illusions",
    "explanation": "Why do LLMs notoriously claim that 9.11 is larger than 9.9? Look at the token splits: '9.11' is split into ['9', '.', '11'] (tokens 24, 13, 806). '9.9' is split into ['9', '.', '9'] (tokens 24, 13, 24). The model compares the subword token '11' with '9'. In integers, 11 > 9, so the model's pattern matching trips!",
    "consequence_for_llms": "Tokenizers chunk numbers unpredictably based on byte frequency rather than place value (ones, tens, hundreds). This causes catastrophic errors in arithmetic, decimal comparisons, and financial modeling.",
    "items": [
      {
        "label": "9.11",
        "input_text": "9.11",
        "token_ids": [24, 13, 806],
        "token_count": 3,
        "tokens_str": ["9", ".", "11"],
        "meaning_or_context": "Parsed as subwords 9, point, and ELEVEN"
      },
      {
        "label": "9.9",
        "input_text": "9.9",
        "token_ids": [24, 13, 24],
        "token_count": 3,
        "tokens_str": ["9", ".", "9"],
        "meaning_or_context": "Parsed as subwords 9, point, and NINE"
      },
      {
        "label": "9.90",
        "input_text": "9.90",
        "token_ids": [24, 13, 90],
        "token_count": 3,
        "tokens_str": ["9", ".", "90"],
        "meaning_or_context": "Adding trailing zero turns token into NINETY"
      }
    ]
  },
  {
    "id": "homoglyph-attack",
    "category": "homoglyph",
    "title": "The Homoglyph Disguise: Latin 'apple' vs Cyrillic 'аpple'",
    "subtitle": "Visually identical to humans, completely different token streams to LLMs",
    "explanation": "Type Latin 'apple' (ASCII 'a', code 97). Now type Cyrillic 'аpple' (Cyrillic 'а', Unicode U+0430). On screen, both strings look 100% IDENTICAL. But in the tokenizer, Latin 'apple' is a single word token (23182), while Cyrillic 'аpple' explodes into 3 tokens: [1506, 604, 273] because the Cyrillic byte sequence triggers subword breakdown!",
    "consequence_for_llms": "Adversaries exploit this for prompt injection and bypassing LLM guardrails: a banned word or brand name can be rendered with a Cyrillic homoglyph, slipping past keyword filters and embedding classifiers while remaining completely readable to human victims.",
    "items": [
      {
        "label": "Latin 'apple'",
        "input_text": "apple",
        "token_ids": [23182],
        "token_count": 1,
        "tokens_str": ["apple"],
        "meaning_or_context": "Standard English word (1 token: 23182)"
      },
      {
        "label": "Cyrillic 'аpple'",
        "input_text": "аpple",
        "token_ids": [1506, 604, 273],
        "token_count": 3,
        "tokens_str": ["\\xd0\\xb0", "pp", "le"],
        "meaning_or_context": "Cyrillic 'а' causes byte fallback split into 3 tokens"
      }
    ]
  }
];

// App State
const state = {
  activeEncoding: "cl100k_base",
  currentText: "All human beings are born free and equal in dignity and rights.",
  languages: EMBEDDED_LANGUAGES,
  presets: EMBEDDED_PRESETS,
  activeFilter: "all",
  activePresetCategory: "homograph",
  activePresetId: "homographs-lead",
  selectedToken: null,
  calcWords: 50000,
  calcCostPerMillion: 30.00
};

// Real Tokenizer Wrappers (resolved from window or fallback)
function getActiveTokenizer() {
  if (state.activeEncoding === "cl100k_base" && window.GPTTokenizer_cl100k_base) {
    return window.GPTTokenizer_cl100k_base;
  }
  if (state.activeEncoding === "o200k_base" && window.GPTTokenizer_o200k_base) {
    return window.GPTTokenizer_o200k_base;
  }
  if (state.activeEncoding === "r50k_base" && window.GPTTokenizer_r50k_base) {
    return window.GPTTokenizer_r50k_base;
  }
  // Fallback to whichever is loaded
  return window.GPTTokenizer_cl100k_base || window.GPTTokenizer_o200k_base || window.GPTTokenizer_r50k_base || null;
}

// Generate deterministic HSL color for token chips based on token ID
function getTokenColor(tokenId, idx) {
  // Use golden ratio hash for pleasing vibrant hues
  const goldenRatio = 0.618033988749895;
  const hue = Math.floor(((tokenId * goldenRatio) % 1) * 360);
  return {
    bg: `hsla(${hue}, 70%, 20%, 0.65)`,
    border: `hsla(${hue}, 80%, 65%, 0.45)`,
    text: `hsla(${hue}, 85%, 85%, 1)`
  };
}

// Format token text for display (render whitespace symbols)
function formatTokenText(text) {
  if (text === " ") return "␣ (space)";
  if (text === "\n") return "↵ (newline)";
  if (text === "\t") return "⇥ (tab)";
  if (text === "") return "⟨empty/byte⟩";
  
  // Replace leading/trailing spaces for visibility
  return text
    .replace(/^ /, "␣")
    .replace(/ $/, "␣")
    .replace(/\n/g, "↵\n");
}

// String to Hex Bytes
function stringToHexBytes(str) {
  try {
    const encoder = new TextEncoder();
    const bytes = encoder.encode(str);
    return Array.from(bytes).map(b => "0x" + b.toString(16).padStart(2, "0").toUpperCase()).join(" ");
  } catch (e) {
    return "N/A";
  }
}

// Core Tokenization Runner
function runTokenization() {
  const text = state.currentText || "";
  const tok = getActiveTokenizer();

  let tokenIds = [];
  let pieces = [];

  if (tok && typeof tok.encode === "function") {
    try {
      tokenIds = tok.encode(text);
      pieces = tokenIds.map(id => {
        let pieceText = "";
        try {
          pieceText = tok.decode([id]);
        } catch (e) {
          pieceText = `[ID ${id}]`;
        }
        return {
          id: id,
          text: pieceText,
          hex: stringToHexBytes(pieceText),
          byteLength: new TextEncoder().encode(pieceText).length,
          isWhitespace: /^\s+$/.test(pieceText)
        };
      });
    } catch (err) {
      console.warn("Tokenizer error:", err);
    }
  }

  // Fallback if bundle not ready: approximate tokenization for graceful degradation
  if (tokenIds.length === 0 && text.length > 0) {
    const words = text.split(/(\s+)/);
    let mockId = 1000;
    words.forEach(w => {
      if (w.length > 0) {
        tokenIds.push(mockId);
        pieces.push({
          id: mockId++,
          text: w,
          hex: stringToHexBytes(w),
          byteLength: new TextEncoder().encode(w).length,
          isWhitespace: /^\s+$/.test(w)
        });
      }
    });
  }

  updateStudioUI(text, tokenIds, pieces);
}

// Update Studio UI elements
function updateStudioUI(text, tokenIds, pieces) {
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const chars = text.length;
  const count = tokenIds.length;
  const tpw = words > 0 ? (count / words).toFixed(2) : "0.00";
  const cpt = count > 0 ? (chars / count).toFixed(2) : "0.00";

  // Update Stats
  document.getElementById("stat-tokens").textContent = count;
  document.getElementById("stat-words").textContent = words;
  document.getElementById("stat-chars").textContent = chars;
  document.getElementById("stat-tpw").textContent = tpw;
  document.getElementById("stat-cpt").textContent = cpt;

  // Estimated cost for this text (GPT-4)
  const gpt4Cost = ((count / 1_000_000) * 30.00).toFixed(6);
  document.getElementById("stat-cost").textContent = `$${gpt4Cost}`;

  // Render Token Ribbon
  const ribbon = document.getElementById("token-ribbon");
  ribbon.innerHTML = "";

  if (pieces.length === 0) {
    ribbon.innerHTML = `<span style="color: var(--text-muted); font-size: 0.9rem; margin: auto;">Type or paste text above to see token breakdown...</span>`;
    return;
  }

  pieces.forEach((piece, idx) => {
    const chip = document.createElement("div");
    chip.className = `token-chip ${piece.isWhitespace ? 'whitespace' : ''}`;
    
    const colors = getTokenColor(piece.id, idx);
    chip.style.backgroundColor = colors.bg;
    chip.style.borderColor = colors.border;
    chip.style.color = colors.text;

    chip.innerHTML = `
      <span class="token-piece-text">${escapeHtml(formatTokenText(piece.text))}</span>
      <span class="token-piece-id">#${piece.id}</span>
    `;

    chip.addEventListener("click", () => inspectToken(piece, idx));
    ribbon.appendChild(chip);
  });
}

// Token Inspector Details
function inspectToken(piece, idx) {
  const panel = document.getElementById("inspector-panel");
  panel.classList.add("active");

  document.getElementById("insp-idx").textContent = idx;
  document.getElementById("insp-id").textContent = piece.id;
  document.getElementById("insp-str").textContent = JSON.stringify(piece.text);
  document.getElementById("insp-bytes").textContent = piece.hex || "N/A";
  document.getElementById("insp-len").textContent = `${piece.byteLength} bytes`;

  // Unicode codepoints
  const codepoints = Array.from(piece.text).map(c => "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")).join(", ");
  document.getElementById("insp-unicode").textContent = codepoints || "None";
}

// Close Inspector
function closeInspector() {
  document.getElementById("inspector-panel").classList.remove("active");
}

// Render Section 2 Language Comparison Table
function renderLanguageTable() {
  const tbody = document.getElementById("language-table-body");
  tbody.innerHTML = "";

  const filter = state.activeFilter;
  const filtered = state.languages.filter(lang => {
    if (filter === "minority") return lang.is_minority_or_underrepresented;
    if (filter === "non-latin") return !lang.script.includes("Latin");
    if (filter === "european") return lang.family.includes("Indo-European") && !lang.is_minority_or_underrepresented;
    return true;
  });

  filtered.forEach(lang => {
    const tr = document.createElement("tr");

    let tpwClass = "tpw-low";
    if (lang.tpw_cl100k > 15) tpwClass = "tpw-extreme";
    else if (lang.tpw_cl100k > 4) tpwClass = "tpw-high";
    else if (lang.tpw_cl100k > 1.8) tpwClass = "tpw-med";

    let costClass = "cost-1x";
    if (lang.cost_multiplier_vs_english_cl100k >= 6.0) costClass = "cost-extreme";
    else if (lang.cost_multiplier_vs_english_cl100k >= 2.0) costClass = "cost-high";

    tr.innerHTML = `
      <td>
        <div class="lang-cell">
          <span class="lang-name-bold">${lang.name}</span>
          <span class="lang-native">${lang.native_name}</span>
        </div>
      </td>
      <td><span class="script-badge">${lang.script}</span></td>
      <td><strong>${lang.tokens_cl100k}</strong> <small style="color:var(--text-muted)">(${lang.tokens_o200k} in 4o)</small></td>
      <td>${lang.word_count}</td>
      <td><span class="tpw-pill ${tpwClass}">${lang.tpw_cl100k} t/w</span></td>
      <td><span class="cost-badge ${costClass}">${lang.cost_multiplier_vs_english_cl100k}x</span></td>
      <td>
        <button class="btn-inspect-sample" onclick="loadLanguageIntoStudio('${lang.code}')">
          Try in Studio ➔
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Load a language sample into the studio
window.loadLanguageIntoStudio = function(code) {
  const sample = state.languages.find(l => l.code === code);
  if (!sample) return;

  const textarea = document.getElementById("studio-input");
  textarea.value = sample.text;
  state.currentText = sample.text;
  runTokenization();

  // Smooth scroll up to studio
  document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
};

// Render Section 3 Collision Presets
function renderCollisionPresets() {
  const nav = document.getElementById("collision-tabs-nav");
  nav.innerHTML = "";

  state.presets.forEach(preset => {
    const btn = document.createElement("button");
    btn.className = `collision-tab-btn ${preset.id === state.activePresetId ? 'active' : ''}`;
    btn.textContent = preset.title.split(":")[0];
    btn.addEventListener("click", () => {
      state.activePresetId = preset.id;
      renderCollisionPresets();
    });
    nav.appendChild(btn);
  });

  const active = state.presets.find(p => p.id === state.activePresetId) || state.presets[0];
  const container = document.getElementById("collision-display-card");

  container.innerHTML = `
    <div class="collision-header-info">
      <span class="collision-badge">${active.category.replace('_', ' ')}</span>
      <h3 class="collision-title">${active.title}</h3>
      <p class="collision-subtitle">${active.subtitle}</p>
      <p class="collision-explanation">${active.explanation}</p>
      <div class="collision-consequence-alert">
        <strong>⚠️ LLM Blunder Consequence:</strong> ${active.consequence_for_llms}
      </div>
    </div>
    <div class="collision-items-grid">
      ${active.items.map(item => `
        <div class="collision-item-box">
          <span class="collision-item-label">${item.label}</span>
          <div class="collision-token-display">
            <span class="shared-token-badge">Token ID: ${item.token_ids.join(', ')}</span>
            <small style="color:var(--text-muted); font-family:var(--font-mono)">(${item.tokens_str.map(s => JSON.stringify(s)).join(', ')})</small>
          </div>
          <p class="collision-meaning">${item.meaning_or_context}</p>
          <button class="btn-inspect-sample" style="align-self: flex-start; margin-top: auto;" onclick="loadTextIntoStudio('${escapeForInline(item.input_text)}')">
            Inspect in Studio ➔
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

window.loadTextIntoStudio = function(text) {
  const textarea = document.getElementById("studio-input");
  textarea.value = text;
  state.currentText = text;
  runTokenization();
  document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
};

// Economic Calculator Logic
function updateCalculator() {
  const words = parseInt(document.getElementById("calc-words-slider").value, 10);
  state.calcWords = words;
  document.getElementById("calc-words-display").textContent = words.toLocaleString() + " words";

  // GPT-4 pricing: $30 per million input tokens
  const pricePerM = 30.00;

  // Language multipliers
  const enTokens = Math.round(words * 1.08);
  const hiTokens = Math.round(words * 5.60);
  const amTokens = Math.round(words * 11.09);
  const myTokens = Math.round(words * 30.00);

  const enCost = (enTokens / 1_000_000) * pricePerM;
  const hiCost = (hiTokens / 1_000_000) * pricePerM;
  const amCost = (amTokens / 1_000_000) * pricePerM;
  const myCost = (myTokens / 1_000_000) * pricePerM;

  document.getElementById("cost-en-val").textContent = `$${enCost.toFixed(2)} (${enTokens.toLocaleString()} tokens)`;
  document.getElementById("cost-hi-val").textContent = `$${hiCost.toFixed(2)} (${hiTokens.toLocaleString()} tokens)`;
  document.getElementById("cost-am-val").textContent = `$${amCost.toFixed(2)} (${amTokens.toLocaleString()} tokens)`;
  document.getElementById("cost-my-val").textContent = `$${myCost.toFixed(2)} (${myTokens.toLocaleString()} tokens)`;

  // Percentage widths (scaled to Burmese max)
  document.getElementById("bar-en").style.width = `${Math.max(5, (enTokens / myTokens) * 100)}%`;
  document.getElementById("bar-hi").style.width = `${(hiTokens / myTokens) * 100}%`;
  document.getElementById("bar-am").style.width = `${(amTokens / myTokens) * 100}%`;
  document.getElementById("bar-my").style.width = `100%`;

  document.getElementById("bar-en").textContent = "1.0x";
  document.getElementById("bar-hi").textContent = "5.2x";
  document.getElementById("bar-am").textContent = "10.3x";
  document.getElementById("bar-my").textContent = "27.8x";
}

// Helpers
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeForInline(str) {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// Copy Code to Clipboard
window.copyDeployCode = function() {
  const code = document.getElementById("deploy-code-snippet").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById("btn-copy-code");
    btn.textContent = "Copied! ✓";
    setTimeout(() => { btn.textContent = "Copy"; }, 2000);
  });
};

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("studio-input");
  textarea.value = state.currentText;

  // Debounced input listener
  let debounceTimer;
  textarea.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      state.currentText = e.target.value;
      runTokenization();
    }, 100);
  });

  // Model Selector Buttons
  document.querySelectorAll(".model-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".model-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.activeEncoding = btn.dataset.model;
      runTokenization();
    });
  });

  // Preset Chips
  document.querySelectorAll(".preset-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      textarea.value = chip.dataset.text;
      state.currentText = chip.dataset.text;
      runTokenization();
    });
  });

  // Language Filter Buttons
  document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.activeFilter = btn.dataset.filter;
      renderLanguageTable();
    });
  });

  // Calculator Slider
  const slider = document.getElementById("calc-words-slider");
  if (slider) {
    slider.addEventListener("input", updateCalculator);
  }

  // Initial runs
  runTokenization();
  renderLanguageTable();
  renderCollisionPresets();
  updateCalculator();
});
