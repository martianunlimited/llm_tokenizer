# LLM Tokenization Anatomy & Linguistic Bias Explorer

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages Ready](https://img.shields.io/badge/GitHub_Pages-Ready-brightgreen.svg)](#-how-to-host-on-github-pages-in-30-seconds)
[![Tests Passing](https://img.shields.io/badge/Tests-13%20Passed-emerald.svg)](#-local-verification--testing)

An interactive, zero-backend, client-side web application designed to be hosted directly on **GitHub Pages**. It runs **real production Byte-Pair Encoding (BPE) tokenizers used in state-of-the-art LLMs** (OpenAI GPT-4 `cl100k_base`, GPT-4o `o200k_base`, and GPT-3 `r50k_base`) directly inside the visitor's browser.

The demo visually and mathematically demonstrates:
1. **The English Monopoly & The Token Tax**: Why BPE disproportionately favors English and severely penalizes non-Latin and indigenous minority languages (imposing up to a **14x financial and context tax**).
2. **Identical Tokenization & Semantic Ambiguity**: How two completely different words or concepts are assigned the **exact same token ID**, blinding the LLM at the input layer before attention runs.
3. **The Silly Mistake Laboratory**: Why LLMs fail at basic tasks like letter counting (`strawberry`), decimal math (`9.11 > 9.9`), leading spaces, word reversals, and homoglyphs.

---

## 🚀 How to Host on GitHub Pages in 30 Seconds

This project is 100% static (HTML, CSS, JS, bundled tokenizer tables) and requires **no build step, no Node server, and no Python backend**.

### Step 1: Initialize Git and Push to GitHub
Run the following in your terminal:
```bash
cd llm_tokenization_demo
git init
git add .
git commit -m "Initial commit of LLM tokenization demo"

# Link to your repository on GitHub:
git branch -M main
git remote add origin https://github.com/martianunlimited/llm_tokenizer.git
git push -u origin main
```

### Step 2: Turn on GitHub Pages
1. Go to your repository on GitHub (`https://github.com/martianunlimited/llm_tokenizer`).
2. Click **Settings** (gear icon) → **Pages** (in the left sidebar).
3. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main` (or `gh-pages`) and folder `/(root)`.
4. Click **Save**.

Your interactive demo will be live at:
```
https://martianunlimited.github.io/llm_tokenizer/
```

*(Note: The `.nojekyll` file is already included in the repository root to ensure all asset files and subdirectories are served without Jekyll processing).*

---

## 🧠 Educational Core: Key Concepts Explained

### 1. The "Token Tax" on Minority & Non-Latin Languages

LLM tokenizers (BPE / SentencePiece) are trained by greedily merging the most frequent character pairs in internet corpora. Because the pre-training datasets are overwhelmingly English (Common Crawl, Wikipedia, Reddit), subwords representing common English syllables and words are merged into single token integers.

When a sentence from the *Universal Declaration of Human Rights (Article 1)* is tokenized across languages, the disparity is stark:

| Language | Script | Words | GPT-4 Tokens (`cl100k`) | Tokens / Word | Cost Multiplier vs English |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **English** | Latin | 12 | **13** | **1.08 t/w** | **1.0x (Baseline)** |
| **Spanish** | Latin | 12 | 19 | 1.58 t/w | 1.46x |
| **German** | Latin | 11 | 16 | 1.45 t/w | 1.23x |
| **Māori (Te Reo)** | Latin | 18 | 31 | 1.72 t/w | 2.38x |
| **Russian** | Cyrillic | 10 | 28 | 2.80 t/w | 2.15x |
| **Arabic** | Arabic | 8 | 37 | 4.62 t/w | 2.85x |
| **Hindi** | Devanagari | 15 | 84 | 5.60 t/w | **6.46x** |
| **Amharic** | Ge'ez | 11 | 122 | 11.09 t/w | **9.38x** |
| **Burmese** | Myanmar | 6 | **180** | **30.00 t/w** | **13.85x** |

#### The 4 Punishments of the Token Tax:
1. **Economic Inequity**: Commercial LLM APIs charge strictly per token. A developer querying an LLM in Burmese or Amharic pays **10x to 14x more money** than an English developer for the identical semantic content.
2. **Context Shrinkage**: A 128k context window holds ~100,000 English words, but is completely exhausted in under 10,000 words of Burmese.
3. **Latency Inflation**: LLMs generate text token-by-token (one forward pass per token). Generating a Burmese sentence requires **5x to 14x more compute time**.
4. **Attention / Reasoning Degradation**: Transformers use self-attention across tokens. When a single word is fragmented into 6 raw UTF-8 fallback bytes (`\xe1\x80...`), attention heads must waste representational capacity reconstructing letters rather than performing higher-order semantic reasoning.

---

### 2. Identical Tokenization & The False Friend Trap

What happens when two completely different words or concepts share the **exact same token ID**?

At the transformer's input embedding matrix ($W_e$), each unique token integer maps to a **single static vector**. Before attention layers process context, the model starts 100% blind to any distinction:

#### A. Homographs (Single Language)
- **`lead`** (heavy toxic metal element Pb, `/lɛd/`) vs **`lead`** (verb to guide a team, `/liːd/`):
  - **Shared Token ID**: `[27152]` in GPT-4.
  - In short, ambiguous prompts (e.g., *"Is lead dangerous?"*), the model has only a single embedding vector and must guess based on pre-training frequency.
- **`bass`** (freshwater fish) vs **`bass`** (low musical frequency):
  - **Shared Token ID**: `[8106]`.

#### B. Cross-Lingual False Friends (Semantic Clashes)
Because tokenizers are language-agnostic, words with identical spelling in different languages share the exact same token:
- **`gift`** in English (a thoughtful present) vs **`gift`** in German (*das Gift* = **deadly poison**):
  - **Shared Token ID**: `[53430]`.
  - Prompts in German or bilingual text can confuse the model into translating "He gave me a gift" as "He gave me poison".
- **`pain`** in French (delicious baguette / bread) vs **`pain`** in English (physical suffering / agony):
  - **Shared Token ID**: `[92724]`.
- **`chat`** in French (a cat / feline) vs **`chat`** in English (informal conversation):
  - **Shared Token ID**: `[9884]`.
- **`die`** in German (the / feminine article) vs **`die`** in English (perish / cease living):
  - **Shared Token ID**: `[998]`.

---

### 3. The Silly Mistake Laboratory: Why LLMs Fail

1. **The "Strawberry" Dilemma (Letter Counting)**:
   - Why does GPT-4 fail to count the three 'r's in "strawberry"?
   - Because "strawberry" is tokenized into `['str', 'aw', 'berry']` (Tokens `496`, `675`, `15717`). The individual letters 's-t-r-a-w-b-e-r-r-y' **do not exist** in the transformer's input!
   - *Fix demonstrated in the app*: Hyphenating (`s-t-r-a-w-b-e-r-r-y`) forces 1 token per letter, allowing the model to count effortlessly.

2. **The "9.11 > 9.9" Math Trap**:
   - `9.11` is split into `['9', '.', '11']` (Tokens `24`, `13`, `806`).
   - `9.9` is split into `['9', '.', '9']` (Tokens `24`, `13`, `24`).
   - The model compares subword token `11` with token `9`. Since $11 > 9$, pattern matching fails!

3. **The Leading Space Paradox**:
   - `" apple"` (Token `24149`) vs `"apple"` (Token `23182`) vs `"Apple"` (Token `27665`) vs `" Apple"` (Token `8325`).
   - To an LLM, these are four completely distinct integers with independent weights. Adding an accidental trailing space at the end of a prompt frequently breaks formatting or flips output classifications.

4. **Homoglyph Security Attacks (Latin vs Cyrillic)**:
   - Latin `"apple"` (ASCII 'a', code 97) = 1 token (`[23182]`).
   - Cyrillic `"аpple"` (Cyrillic 'а', Unicode U+0430) = 3 tokens (`[1506, 604, 273]`).
   - To humans, they look 100% identical. To an LLM, the Cyrillic string completely bypasses prompt injection filters, content moderation blocklists, and embedding classifiers.

5. **Glitch Tokens (`SolidGoldMagikarp`)**:
   - In GPT-3 (`r50k_base`), `" SolidGoldMagikarp"` is single Token ID `#43453`. It was scraped from Reddit during tokenizer construction, but never appeared in text pretraining. Querying it causes the model to loop, hallucinate, or crash.

---

## 🛠️ Project Architecture

```
llm_tokenization_demo/
├── .nojekyll                   # Ensures GitHub Pages serves all static files
├── index.html                  # Accessible, responsive, modern web app
├── style.css                   # Glassmorphism design system & token chip palette
├── app.js                      # Core frontend application & interactive controllers
├── data/
│   ├── languages.json          # Verified benchmark metrics across 15+ languages
│   └── collision_presets.json  # Curated presets: Homographs, False Friends, Glitches
├── lib/
│   ├── cl100k_base.js          # OpenAI GPT-4 / ChatGPT tokenizer bundle
│   ├── o200k_base.js           # OpenAI GPT-4o / GPT-4o-mini tokenizer bundle
│   └── r50k_base.js            # OpenAI GPT-3 / text-davinci tokenizer bundle
├── pyproject.toml              # Python project configuration
├── src/
│   ├── config.py               # pydantic-settings configuration
│   ├── schemas.py              # Pydantic v2 domain models
│   ├── core/
│   │   ├── tokenizer_service.py # Pure decoupled Python tokenizer service
│   │   └── data_generator.py    # Generates and validates accurate datasets
│   └── cli.py                  # Typer CLI application for terminal exploration
├── tests/
│   ├── test_schemas.py         # Schema validation tests
│   ├── test_tokenizer_service.py # Core service contracts & TDD tests
│   └── test_web_assets.py      # Asset integrity and bundle verification
└── README.md                   # Full documentation & deployment guide
```

---

## 🧪 Local Verification & Testing

If you want to run the verification tests or CLI locally:

### 1. Run Python Tests
```bash
# Run test suite
python -m pytest -q

# Format and lint
python -m ruff check . --fix
python -m ruff format .
```

### 2. Run the Typer CLI
```bash
# Tokenize any text with detailed byte breakdowns:
python -m src.cli tokenize "strawberry"

# Compare across GPT-4, GPT-4o, and GPT-3:
python -m src.cli compare "All human beings are born free"

# View the Language Equity Benchmark table in your terminal:
python -m src.cli languages
```

### 3. Run Web App Locally
```bash
# Launch a local server:
python -m http.server 8080

# Open in browser:
http://localhost:8080
```

---

## 📄 License
MIT License. Free for educational, research, and commercial use.
