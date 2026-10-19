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

## 24-Pattern Error Taxonomy

Satzwerk standardizes grammatical errors into a 24-code enum (`PatternCode`) rooted in Pienemann's Processability Theory and Ferris's treatable error categories:

| Group | Codes | Description |
| :--- | :--- | :--- |
| **Word Order** | `WO-V2`, `WO-SEP`, `WO-VF`, `WO-KLAM`, `WO-TMP` | Verb-second, separable prefixes, subordinate verb-final, Satzklammer, TeKaMoLo |
| **Case** | `KAS-AKK`, `KAS-DAT`, `KAS-GEN`, `KAS-PREP`, `KAS-2WEG` | Direct/indirect objects, genitive, fixed-case prepositions, two-way prepositions |
| **Agreement** | `ADJ-END`, `ART-GEN`, `N-PL`, `PRO-REL`, `PRO-KAS` | Adjective declension, gender agreement, plurals, relative/personal pronouns |
| **Verbs** | `V-KONJ`, `V-TEMP`, `V-PART`, `V-K2`, `V-REFL` | Conjugation, tense choice, participle formation, Konjunktiv II, reflexives |
| **Other** | `PREP-W`, `ORTH`, `WORTW`, `SONST` | Preposition choice, orthography/capitalization, word choice, other |

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
