from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.ai.constants import TAXONOMY, CEFRLevel, PatternCode, taxonomy_prompt_block
from src.ai.schema import Analysis

SYSTEM_PROMPT = (
    "You are a German SLA syntax analyser. Given a learner's draft, produce an error diagnosis with:\n"
    "1. quote (L2): The exact broken phrase/clause from the learner's draft (never quote the entire multi-clause sentence if only a phrase is wrong).\n"
    "2. pattern_code (L3): Exactly ONE pattern code chosen from the taxonomy below.\n"
    "   - Important: Subordinate clauses ('weil', 'dass', 'wenn', 'ob') where the finite verb is not at the end are ALWAYS `WO-VF` (never `V-TEMP`).\n"
    "   - Fixed-case preposition errors (e.g. 'zu den' instead of 'zum') are ALWAYS `KAS-PREP`.\n"
    "3. explanation (L4): A concise grammatical rule hint in English that MUST NEVER contain the corrected German words from `correction` (L5).\n"
    "4. correction (L5): The corrected German words replacing `quote`.\n\n"
    "Pedagogical Guidelines:\n"
    "- Clause-by-Clause Comprehensive Scan: Inspect EVERY clause in the draft (both main clauses and subordinate clauses after commas like 'weil ...', 'dass ...'). You MUST generate a separate card for EVERY error in the draft. Never stop after checking only a '?' marker!\n"
    "- Clean Drafts: If the learner's draft is already 100% grammatically correct, return an empty cards list (`cards: []`). Do NOT invent errors where none exist.\n"
    "- Zero Answer Leaks in L4: Write `explanation` in English describing the grammar mechanism (e.g. 'This preposition requires the dative case, so the masculine article must change'). Never write the exact `correction` string inside `explanation`.\n"
    "- CEFR Scaffolding: If a Learner Target CEFR Level is specified, calibrate explanation (L4) wording to be clear and accessible to a learner at that level.\n"
    "- Inline Hypothesis Markers (?):\n"
    "  Learners mark uncertain words with inline '?' (e.g. '?zu den?' or '?dem Mann?').\n"
    "  * If an inline hypothesis contains a real error (e.g. '?zu den?'), create an error card for it (so `confirmed_hypotheses` stays `[]`) AND still check the rest of the sentence for other unmarked errors!\n"
    "  * If an inline hypothesis is ALREADY CORRECT (e.g. '?dem Mann?' in 'Ich helfe ?dem Mann?.'), do NOT create an error card for it; add the correct phrase to `confirmed_hypotheses`.\n"
    "- No Stylistic Overcorrection: Only flag genuine grammatical, morphosyntactic, or orthographic "
    "errors in standard written German. Never correct grammatically valid phrasing purely for stylistic preference.\n\n"
    "Allowed Pattern Taxonomy (L3):\n"
    f"{taxonomy_prompt_block()}"
)

CRITIC_SYSTEM_PROMPT = (
    "You are a Senior German SLA Pedagogical Critic. Verify the AI-generated error cards against the learner's draft.\n\n"
    "Check ONLY these 3 rules. If there are no violations, return `critiques: []` and `is_valid: true`:\n\n"
    "1. Hypothesis Marker Coverage (?):\n"
    "   - When the draft has an incorrect '?...?' phrase (e.g. '?zu den?'), having an Error Card that includes '?zu den?' and having `Confirmed Correct Hypotheses: (None)` is 100% VALID. Do NOT complain that Confirmed Correct Hypotheses is (None) when the '?' phrase was an error!\n"
    "   - Only when a '?...?' phrase in the draft is grammatically CORRECT should it be in Confirmed Correct Hypotheses.\n"
    "   - When the draft has NO '?' markers at all, this rule automatically passes.\n\n"
    "2. Taxonomy Code Accuracy (L3):\n"
    "   - Verify each card's PatternCode matches the error between Quote and Correction using the taxonomy below.\n\n"
    "3. No Stylistic False Positives & No Missed Clause Errors:\n"
    "   - Ensure no card flags valid standard written German merely for style, and ensure obvious clause errors (like V2 after 'weil' -> WO-VF) were not missed.\n\n"
    "Allowed Pattern Taxonomy:\n"
    f"{taxonomy_prompt_block()}"
)

WRITING_TASK_SYSTEM_PROMPT = (
    "You are a witty, creative German SLA task designer. Generate a short, fun 1-2 sentence "
    "writing prompt in English for a German learner.\n\n"
    "Rules:\n"
    "- Make It Fun (No Boring Textbook Prompts!): Avoid dry topics like writing to a boss or landlord. "
    "Use playful, dramatic, gossipy, or slightly absurd everyday scenarios (e.g., a terrible restaurant date, "
    "a suspicious excuse for being late, a dramatic complaint about a chaotic roommate, or a pet's secret life).\n"
    "- Keep Vocabulary Accessible: Even when the scenario is funny, make sure the learner can answer using "
    "everyday German words appropriate for their CEFR level.\n"
    "- Explicit Grammar Constraints: Tell the learner which structures they MUST use to trigger the target patterns "
    "(e.g., 'Start one sentence with a time expression, and use weil or obwohl').\n"
    "- NEVER write the German target sentences for the learner!\n\n"
    "Allowed Pattern Taxonomy:\n"
    f"{taxonomy_prompt_block()}"
)


def build_generator_messages(
    sentence: str,
    critique: str | None = None,
    previous_analysis: Analysis | None = None,
    cefr_level: CEFRLevel | None = None,
) -> list[BaseMessage]:
    user_content = f"Sentence: {sentence}"
    if cefr_level:
        user_content += f"\nLearner Target CEFR Level: {cefr_level}"

    if previous_analysis and previous_analysis.cards and critique:
        attempt_summary = "\n".join(
            f"Card {i} (Quote='{c.quote}' -> Correction='{c.correction}'): Pattern={c.pattern_code}, Explanation='{c.explanation}'"
            for i, c in enumerate(previous_analysis.cards, start=1)
        )
        user_content += (
            f"\n\nYour previous attempt produced:\n{attempt_summary}\n\n"
            f"Keep any valid cards from your previous attempt and fix/add what is noted in this critique:\n{critique}"
        )
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_content)]


def build_critic_messages(sentence: str, analysis: Analysis) -> list[BaseMessage]:
    cards_summary = (
        "\n".join(
            f"Card {i}: Quote='{c.quote}' -> Correction='{c.correction}' (Pattern={c.pattern_code})"
            for i, c in enumerate(analysis.cards, start=1)
        )
    ) or "(No error cards generated)"

    confirmed_summary = (
        ", ".join(f"'{h}'" for h in analysis.confirmed_hypotheses) or "(None)"
    )

    user_content = (
        f"Learner Draft: {sentence}\n\n"
        f"Generated Error Cards:\n{cards_summary}\n\n"
        f"Confirmed Correct Hypotheses: {confirmed_summary}\n\n"
        "Evaluate the cards against the 3 rules."
    )

    return [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]


def build_writing_prompt_messages(
    cefr_level: CEFRLevel, target_patterns: list[PatternCode]
) -> list[BaseMessage]:
    if target_patterns:
        patterns_desc = "\n".join(
            f"- {code} ({TAXONOMY[code]['name']}): {TAXONOMY[code]['hint']}"
            for code in target_patterns
        )
        user_content = (
            f"Learner CEFR Level: {cefr_level}\n"
            f"Target Weaknesses to Drill:\n{patterns_desc}"
        )
    else:
        user_content = (
            f"Learner CEFR Level: {cefr_level}\n"
            "This learner has no recorded errors yet. Choose 1-2 foundational patterns "
            f"appropriate for {cefr_level} and design a writing prompt around them."
        )
    return [
        SystemMessage(content=WRITING_TASK_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
