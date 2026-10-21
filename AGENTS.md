# Satzwerk — Agent & Engineering Guidelines

This document serves as the architectural and pedagogical contract for all developers and AI agents working on the **Satzwerk** codebase. 

---

## 1. The Core Purpose: Second Language Acquisition (SLA)

Satzwerk is a closed-loop German writing production system. It is deliberately **not** vocabulary flashcards (that is Anki/Garten) and **not** a passive spellchecker. Every interaction trains **active morphosyntactic production** under cognitive load.

The core problem Satzwerk solves is bridging the gap between:
- **Declarative Knowledge**: Knowing a grammar rule (e.g., scoring 100% on a multiple-choice quiz on subordinate clauses).
- **Procedural Knowledge**: Actually deploying that rule in real-time writing without cognitive collapse.

---

## 2. Pedagogical Invariants — Never Break These

1. **The 5-Rung Ladder Never Runs Backwards**:
   Feedback strictly escalates rung by rung upon learner request:
   - **L1 (Locate)**: `sentence_index: int` — Highlights which sentence contains an error.
   - **L2 (Underline)**: `quote: str` — Exact verbatim characters from the draft.
   - **L3 (Category Badge)**: `pattern_code: PatternCode` — Standardized taxonomy code (e.g., `WO-VF`, `KAS-PREP`).
   - **L4 (Rule Hint)**: `explanation: str` — Pedagogical hint on the grammatical mechanism.
   - **L5 (Clean Rewrite)**: `correction: str` — The target-form solution.

2. **L4 Must Never Leak L5**:
   An explanation (`explanation`) must **never** contain, state, or trivially paraphrase the correction (`correction`). If L4 leaks L5, the retrieval effort is destroyed and the learner reverts to passive reading.

3. **L2 (Quote) Must Be Verbatim**:
   The `quote` must match an exact substring in the learner's draft. LLMs love silently correcting umlauts, casing, or punctuation inside the quote. If a quote is not verbatim, L1 sentence location fails and the UI cannot underline the error.

4. **No Identity Corrections (No-Op)**:
   If an error is flagged, `quote.strip()` must never equal `correction.strip()`.

5. **L1 (Sentence Index) is Deterministic**:
   LLMs are unreliable at 0-indexed counting across multi-sentence paragraphs. `sentence_index` must always be calculated deterministically in Python via [`src/ai/utils.py`](file:///Users/macbook/Desktop/satzwerk/src/ai/utils.py#L9-L16) after the quote is validated.

6. **The Taxonomy is a Strict Enum**:
   `pattern_code` must always be an instance of `PatternCode` from [`src/ai/constants.py`](file:///Users/macbook/Desktop/satzwerk/src/ai/constants.py#L5-L35). Free-form strings (`"DATIVE_PREP"`, `"CASE_DAT"`) break relational integrity and longitudinal tracking in the Error Ledger.

7. **No Live As-You-Type Corrections**:
   Retrieval effort during full sentence drafting is the psychological mechanism. Feedback is generated only on submission.

8. **Pienemann Stage vs. CEFR Grounding**:
   - `stage` in `PatternMetadata` strictly reflects Manfred Pienemann's Processability Theory (1998) hierarchy (Stages 3–5) for syntactic constituent movement (`WO-SEP`, `WO-KLAM`, `WO-V2`, `WO-VF`, `PRO-REL`). Non-movement categories must remain `stage: None`.
   - `cefr` in `PatternMetadata` systematically anchors all 24 codes to CEFR levels (`A1`, `A2`, `B1`, `B2`) based on *Profile deutsch* (Glaboniat et al., Goethe-Institut) and empirical learner corpus frequencies (MERLIN, Falko).

---

## 3. System Architecture

```
satzwerk/
├── src/
│   ├── ai/                         # LangGraph Evaluator-Optimizer & AI Services
│   │   ├── constants.py            # 24-code PatternCode StrEnum and taxonomy metadata
│   │   ├── schema.py               # Pydantic v2 schemas: GermanCard, EnrichedGermanCard, Analysis, LearnerProfile
│   │   ├── state.py                # TypedDict LangGraph state
│   │   ├── prompts.py              # System & Human message builders
│   │   ├── llm.py                  # LiteLLM client with structured output bindings
│   │   ├── nodes.py                # generator() & evaluator() deterministic gate
│   │   ├── edges.py                # decide() conditional routing
│   │   ├── graph.py                # Compiled StateGraph workflow
│   │   ├── utils.py                # Deterministic sentence splitter & locator
│   │   ├── service.py              # AIService graph execution bridge
│   │   ├── router.py               # FastAPI endpoints (/ai/analyze-draft, /ai/demo)
│   │   ├── demo_html.py            # Standalone 5-rung HTML/Tailwind interactive test UI
│   │   └── exceptions.py           # CardGenerationFailedException
│   ├── auth/                       # Authentication, JWT, Valkey OTP, Users, Error Ledger, Dependencies
│   ├── config.py                   # Central Pydantic BaseSettings (.env loading)
│   ├── database.py                 # Async SQLAlchemy engine & session factory
│   ├── cache.py                    # Valkey / Redis client
│   ├── exceptions.py               # AppException & global exception handler
│   └── main.py                     # FastAPI entrypoint and lifespan
├── tests/
│   ├── ai/                         # AI graph and deterministic node tests
│   └── conftest.py                 # Async test database & cache fixtures
```

---

## 4. Evaluator-Optimizer Engine

The AI workflow runs on a LangGraph `StateGraph` with a two-stage verification pipeline:

```
               ┌─────────────────────────────────┐
               │              START              │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │         Node: generator         │ ◄──────────────────────┐
               └────────────────┬────────────────┘                        │
                                │                                         │
                                ▼                                         │ (Retry with
               ┌─────────────────────────────────┐                        │  critique)
               │   Node: deterministic_evaluator │                        │
               │        (Pure Python Gate)       │                        │
               └────────────────┬────────────────┘                        │
                                │                                         │
                                ▼                                         │
                   [ decide_after_deterministic ] ────────────────────────┤
                               /         \                                │
                   is_valid == True    iterations >= MAX                  │
                             /             \                              │
                            ▼               ▼                             │
               ┌─────────────────────────┐ [END]                          │
               │ Node: semantic_evaluator│                                │
               │   (Critic LLM Router)   │                                │
               └────────────┬────────────┘                                │
                            │                                             │
                            ▼                                             │
                     [ decide_after_semantic ] ───────────────────────────┘
                               /         \
                   is_valid == True    iterations >= MAX
                             /             \
                            ▼               ▼
                          [END]           [END]
```

### Stage 1: The 3-Point Deterministic Evaluator Gate
Inside [`src/ai/nodes.py`](file:///Users/macbook/Desktop/satzwerk/src/ai/nodes.py), `deterministic_evaluator` executes 100% deterministic Python checks (0 tokens consumed):
1. **Verbatim Check**: `card.quote in state["sentence"]`
2. **Leak Check**: `card.correction.lower() not in card.explanation.lower()`
3. **No-Op Check**: `card.quote.strip() != card.correction.strip()`

If any check fails, it collects targeted feedback in `critiques` and loops straight back to `generator` without invoking the critic LLM.

### Stage 2: The Cross-Family Semantic Critic Gate
`semantic_evaluator` only executes after deterministic checks pass. Routed via `litellm.Router` using a second model (`CRITIC_LLM_MODEL`), it evaluates 3 criteria:
1. **Inline Hypothesis Coverage (`?`)**: Verifies every uncertain word marked with inline `?` (e.g., `?zu den?`) was properly handled: genuine errors produce an error card, whereas correct hypotheses (e.g., `?dem Mann?`) are confirmed in `confirmed_hypotheses` with zero cards.
2. **Taxonomy Code Accuracy (L3)**: Confirms `pattern_code` accurately matches the grammatical error between `quote` and `correction` using the 24-code taxonomy.
3. **No Stylistic False Positives**: Ensures no card flags valid German merely for stylistic preference, and accepts clean drafts (`cards: []`) immediately without error.

---

## 5. Development Conventions

1. **Python Version**: `>=3.12`. Use modern union syntax (`str | None`, not `Optional[str]`).
2. **Type Checking**: Strict adherence to Pyright. Run:
   ```bash
   .venv/bin/pyright src/
   ```
   Code must pass with **0 errors, 0 warnings**.
3. **Pydantic & OpenAI Structured Outputs**:
   - Always avoid optional default factories on container models used for structured output (e.g., use `cards: list[GermanCard] = Field(...)` instead of `default_factory=list`). OpenAI Structured Outputs rejects schemas where properties are missing from the `required` list.
4. **Environment Variables**:
   - Secrets belong in `.env`.
   - Never commit `.env` or API keys.
   - Application configuration flows strictly through `Settings` in [`src/config.py`](file:///Users/macbook/Desktop/satzwerk/src/config.py).
5. **Testing**:
   - Run tests using `.venv/bin/pytest`.
   - Unit tests for deterministic nodes live in [`tests/ai/test_nodes.py`](file:///Users/macbook/Desktop/satzwerk/tests/ai/test_nodes.py).
