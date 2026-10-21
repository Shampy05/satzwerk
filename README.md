# Satzwerk

**Satzwerk** is a closed-loop German writing production system grounded in **Second Language Acquisition (SLA)** principles. 

While flashcard systems drill lexical recall and cloze tests test passive recognition, Satzwerk trains **active morphosyntactic production** under authentic cognitive load.

---

## The Core Cognitive Problem

Language learners frequently possess **declarative knowledge** (they know the grammatical rule and can pass a multiple-choice quiz) but struggle to deploy **procedural knowledge** (actually producing the structure while drafting under working memory constraints). 

For example, a B1/B2 learner knows the finite verb belongs at the end of a subordinate clause (`weil`), yet continues making verb-second mistakes in spontaneous emails. This happens due to three cognitive bottlenecks:

1. **Avoidance (Schachter, 1974)**: When given open writing prompts, learners subconsciously take the path of least resistance, sticking to simple Subject-Verb-Object sentences where they feel safe. Grammatical gaps remain invisible.
2. **Attention Overload (Sweller, 1988)**: Working memory is finite. When a learner is simultaneously inventing a storyline, recalling vocabulary, and negotiating word order, syntax is the first cognitive ball to drop.
3. **Passive Correction**: When an automated tool or instructor simply hands over the corrected sentence, the learner nods and moves on. The brain performs zero retrieval work, meaning no neural proceduralization occurs.

---

## The 5-Step SLA Closed Loop

```
┌──────────────┐     ┌──────────────┐     ┌────────────────────┐     ┌───────────────┐     ┌───────────────┐
│ 1. Task      │ ──► │ 2. Draft     │ ──► │ 3. Graduated       │ ──► │ 4. Clean      │ ──► │ 5. Error      │
│ (Obligatory) │     │ (Production) │     │    Feedback        │     │    Rewrite    │     │    Ledger     │
└──────────────┘     └──────────────┘     └────────────────────┘     └───────────────┘     └───────────────┘
                                                    │
                                          5-Rung Hartshorn Ladder
                                           L1: Locate
                                           L2: Underline
                                           L3: Taxonomy Code
                                           L4: Rule Hint
                                           L5: Clean Rewrite
```

1. **Obligatory-Context Task**: Generates situational writing prompts that structurally require 2–3 specific target grammar patterns, preventing avoidance.
2. **Drafting**: The learner writes a complete multi-sentence draft without live as-you-type interference.
3. **Graduated Feedback (The 5-Rung Ladder)**:
   Feedback is never dumped at once. The learner requests assistance rung by rung:
   - **L1 (Locate)**: Highlights the sentence index (`sentence_index`) containing the error.
   - **L2 (Underline)**: Underlines the exact verbatim mistake (`quote`).
   - **L3 (Taxonomy Code)**: Displays a standardized pedagogical category badge (e.g. `WO-VF`, `KAS-PREP`).
   - **L4 (Rule Hint)**: A pedagogical explanation (`explanation`) that describes the rule mechanism without leaking the solution.
   - **L5 (Clean Rewrite)**: The final target correction (`correction`).
4. **Clean Rewrite**: The session cannot finish until the text has been edited and verified clean by the learner.
5. **Error Ledger**: Longitudinal tracking of recurring pattern codes over weeks and months, charting ladder rung progression from $L4 \rightarrow L3 \rightarrow L1$ (internalization).

---

## System Architecture

```text
satzwerk/
├── src/
│   ├── ai/                         # LangGraph Evaluator-Optimizer Engine
│   │   ├── constants.py            # 24-code PatternCode StrEnum & SLA taxonomy
│   │   ├── schema.py               # Pydantic v2 schemas: GermanCard, EnrichedGermanCard, Analysis
│   │   ├── state.py                # TypedDict LangGraph workflow state
│   │   ├── prompts.py              # System & Human prompt builders
│   │   ├── llm.py                  # ChatLiteLLM configured with structured output
│   │   ├── nodes.py                # Generator node & 3-point deterministic Evaluator gate
│   │   ├── edges.py                # decide() conditional routing
│   │   ├── graph.py                # Compiled LangGraph StateGraph
│   │   ├── utils.py                # Deterministic sentence boundary splitter & locator
│   │   ├── service.py              # AIService asynchronous execution bridge
│   │   ├── router.py               # FastAPI endpoints (/ai/generate-card)
│   │   └── exceptions.py           # Domain exceptions
│   ├── auth/                       # Authentication, JWT, Valkey OTP, Users
│   ├── config.py                   # Central Pydantic BaseSettings (.env loading)
│   ├── database.py                 # Async SQLAlchemy engine & session factory
│   ├── cache.py                    # Valkey / Redis client
│   ├── exceptions.py               # Global exception handlers
│   └── main.py                     # FastAPI application entrypoint
└── tests/
    ├── ai/                         # Unit tests for deterministic evaluator checks
    └── conftest.py                 # Async database & cache test fixtures
```

### The Evaluator-Optimizer Workflow
Satzwerk uses a cyclic LangGraph architecture with a **two-stage verification gate**:
1. **Generator Node**: Prompts `litellm.Router` ("generator") with OpenAI Structured Outputs constrained to the `Analysis` schema and `PatternCode` enum.
2. **Stage 1 — Deterministic Evaluator Node (Pure Python Gate)**:
   - **Verbatim Substring Check**: Verifies that `card.quote` exists verbatim in the submitted text (catches hallucinations).
   - **No-Leak Check**: Verifies that `card.correction.lower()` does not appear in `card.explanation.lower()`.
   - **No-Op Check**: Verifies that `card.quote.strip() != card.correction.strip()`.
   - *If any deterministic check fails, it loops straight back to generator without spending tokens on an LLM critic call.*
3. **Stage 2 — Semantic Evaluator Node (Cross-Family Critic Gate)**:
   - Invokes `litellm.Router` ("critic") using `CRITIC_LLM_MODEL` to verify:
     - Every inline `?` hypothesis marker in the learner's draft was addressed.
     - The `pattern_code` accurately matches the grammatical error between quote and correction.
     - Zero pedantic stylistic false positives are flagged.
4. **Conditional Edges**: Routes back to `generator` with accumulated targeted critiques if any check fails, or terminates at `END` when valid or `AI_MAX_ITERATIONS` is reached.

---

## 24-Pattern Error Taxonomy & SLA Grounding

Satzwerk standardizes German grammatical errors into a 24-code enum (`PatternCode`) rooted in Manfred Pienemann's **Processability Theory (1998)**, Dana Ferris's **treatable vs. untreatable error taxonomy (2002)**, and the **Profile deutsch / CEFR** curricular framework (Glaboniat et al., Goethe-Institut / Council of Europe).

### Processability Theory (Pienemann Stages) vs. CEFR Levels
- **Pienemann Processability Theory (`stage: 3..5`)**: Strictly models developmental constraints on syntactic constituent movement and exchange across grammatical structures (originally derived from the ZISA German L2 longitudinal study). Exactly **5 codes** in our taxonomy represent syntactic word order movement:
  - `WO-SEP` (Stage 3: Separable prefix split)
  - `WO-KLAM` (Stage 3: Verbal bracket / *Satzklammer*)
  - `WO-V2` (Stage 4: Subject-verb inversion / Verb-second)
  - `WO-VF` (Stage 5: Subordinate clause verb-final)
  - `PRO-REL` (Stage 5: Relative pronoun subordinate clause syntax)
  The remaining 19 codes represent morpholexical features, prepositions, or inflectional paradigms where syntactic movement stages do not apply (`stage: None`).
- **CEFR Proficiency Alignment (`cefr: A1..B2`)**: To ensure comprehensive pedagogical coverage across levels A1 through B2, all 24 error codes are mapped to CEFR tiers using *Profile deutsch* benchmarks and empirical learner corpus frequencies (MERLIN, Falko):

| CEFR Level | Target Grammar Categories (`PatternCode`) | Focus & SLA Pedagogical Milestones |
| :--- | :--- | :--- |
| **A1 (Foundation)** | `WO-V2`, `WO-SEP`, `WO-KLAM`, `KAS-AKK`, `ART-GEN`, `N-PL`, `V-KONJ`, `ORTH` | Canonical V2 order, separable verbs, verbal brackets, accusative objects, grammatical gender, basic verb conjugation, and capitalization. |
| **A2 (Core Expansion)** | `WO-VF`, `KAS-DAT`, `KAS-PREP`, `KAS-2WEG`, `PRO-KAS`, `V-TEMP`, `V-PART`, `V-REFL` | Subordinate clauses (*weil*, *dass*), dative objects and fixed prepositions, two-way prepositions (*Wechselpräpositionen*), Perfekt auxiliary and participle formation, reflexive pronouns. |
| **B1 (Intermediate)** | `WO-TMP`, `ADJ-END`, `PRO-REL`, `V-K2`, `PREP-W` | Adverbial ordering (TeKaMoLo), adjective declension paradigms, relative clauses, Konjunktiv II (hypotheticals/politeness), verb/noun prepositional idioms. |
| **B2 (Advanced)** | `KAS-GEN`, `WORTW`, `SONST` | Genitive case and prepositions (*trotz*, *während*, *wegen*), subtle register and lexical nuance (*Wortwahl*), complex stylistic/discourse structures. |

### Complete Taxonomy Overview

| Group | Code | CEFR | PT Stage | Treatable? | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Word Order** | `WO-V2` | A1 | 4 | Yes | Verb-second in main clauses (*Gestern habe ich…*) |
| | `WO-SEP` | A1 | 3 | Yes | Separable-verb split (*Ich rufe dich morgen an*) |
| | `WO-VF` | A2 | 5 | Yes | Verb-final in subordinate clauses (*weil/dass/wenn/ob*) |
| | `WO-KLAM` | A1 | 3 | Yes | Verbal bracket (*Satzklammer*) with auxiliaries/modals |
| | `WO-TMP` | B1 | — | Yes | TeKaMoLo adverbial sequence (Temporal before Manner before Place) |
| **Case** | `KAS-AKK` | A1 | — | Yes | Direct object accusative (*Ich sehe den Mann*) |
| | `KAS-DAT` | A2 | — | Yes | Indirect objects and dative verbs (*helfen*, *danken*, *gefallen*) |
| | `KAS-GEN` | B2 | — | Yes | Genitive possession and prepositions (*wegen*, *trotz*, *während*) |
| | `KAS-PREP` | A2 | — | Yes | Fixed-case prepositions (*mit/zu* &rarr; Dat; *für/ohne* &rarr; Akk) |
| | `KAS-2WEG` | A2 | — | Yes | Two-way prepositions (motion &rarr; Akk, location &rarr; Dat) |
| **Agreement** | `ADJ-END` | B1 | — | Yes | Adjective declension after *der*-words, *ein*-words, and bare nouns |
| | `ART-GEN` | A1 | — | Yes | Article & determiner gender agreement (*der/die/das*) |
| | `N-PL` | A1 | — | Yes | Plural formation and umlaut/ending selection |
| | `PRO-REL` | B1 | 5 | Yes | Relative pronoun agreement and case |
| | `PRO-KAS` | A2 | — | Yes | Personal pronoun case reference (*mir/mich*, *ihm/ihn*) |
| **Verbs** | `V-KONJ` | A1 | — | Yes | Subject-verb agreement and present-tense vowel changes |
| | `V-TEMP` | A2 | — | Yes | Tense choice & Perfekt auxiliary (*haben* vs. *sein*) |
| | `V-PART` | A2 | — | Yes | Participle formation (*ge-* prefix, *-t* vs. *-en*) |
| | `V-K2` | B1 | — | Yes | Konjunktiv II (*würde* + inf, *hätte*, *wäre*, *könnte*) |
| | `V-REFL` | A2 | — | Yes | Reflexive verbs and pronoun selection (*sich freuen auf*) |
| **Other** | `PREP-W` | B1 | — | Yes | Preposition choice for verb/noun collocations (*warten auf*) |
| | `ORTH` | A1 | — | Yes | Orthography, noun capitalization, umlauts, *ß/ss* |
| | `WORTW` | B2 | — | No | Word choice and unidiomatic phrasing |
| | `SONST` | B2 | — | No | General syntax or other non-categorized issues |

---

## Getting Started

### Prerequisites
- Python `>= 3.12`
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `venv`
- Docker & Docker Compose (for PostgreSQL and Valkey)

### 1. Environment Setup
Copy the example environment configuration:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```dotenv
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/satzwerk_test"
VALKEY_URL="valkey://localhost:6379"
SECRET_KEY="your-secret-key"
OPENAI_API_KEY="sk-..."
OPENAI_LLM_MODEL="gpt-4o-mini"
CRITIC_LLM_MODEL="gpt-4o-mini"
LLM_TEMPERATURE=1.0
AI_MAX_ITERATIONS=3
```

### 2. Start Services
Launch PostgreSQL and Valkey with Docker Compose:
```bash
docker-compose up -d
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run the API Server
```bash
uv run uvicorn src.main:app --reload --port 8000
```
API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Running Tests
Run the test suite:
```bash
uv run pytest
```
Run Pyright static type checking:
```bash
uv run pyright src/
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status check |
| `POST` | `/ai/generate-card` | Runs Evaluator-Optimizer analysis on a draft and returns enriched L1–L5 cards |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and issue JWT tokens |
| `POST` | `/auth/verify-otp` | Verify email via Valkey-backed one-time password |

---

## Developer Guidelines

For internal design contracts, pedagogical invariants, and agent development guidelines, see [AGENTS.md](file:///Users/macbook/Desktop/satzwerk/AGENTS.md).
