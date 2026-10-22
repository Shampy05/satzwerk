from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.ai.constants import (
    LANGUAGE_NAMES,
    TAXONOMY,
    CEFRLevel,
    Language,
    PatternCode,
    taxonomy_prompt_block,
)
from src.ai.schema import Analysis

_LANGUAGE_SPECIFIC_RULES: dict[Language, str] = {
    Language.DE: (
        "   - Important: Subordinate clauses ('weil', 'dass', 'wenn', 'ob') where the finite verb is not at the end are ALWAYS `WO-VF` (never `V-TEMP`).\n"
        "   - Fixed-case preposition errors (e.g. 'zu den' instead of 'zum') are ALWAYS `KAS-PREP`.\n"
    ),
    Language.FR: (
        "   - Important: Mandatory preposition+article contraction errors (e.g. 'à le' instead of 'au', 'de le' instead of 'du') and place prepositions are ALWAYS `FR-PREP`.\n"
        "   - Auxiliary choice in compound tenses (using 'avoir' instead of 'être' with motion/reflexive verbs like 'je suis allé') is ALWAYS `FR-AUX`, whereas past participle spelling/agreement is `FR-PP`.\n"
        "   - Subjunctive mood required after expressions like 'il faut que', 'bien que', 'vouloir que' is ALWAYS `FR-SUBJ`.\n"
        "   - Conditional / si-clause tense errors (e.g. 'si j'aurais' instead of 'si j'avais') are ALWAYS `FR-COND`.\n"
    ),
}

_LANGUAGE_HYPOTHESIS_EXAMPLES: dict[Language, tuple[str, str]] = {
    Language.DE: ("?zu den?", "Ich helfe ?dem Mann?."),
    Language.FR: ("?à le?", "Je parle ?au professeur?."),
}


def get_system_prompt(language: Language = Language.DE) -> str:
    lang_name = LANGUAGE_NAMES[language]
    err_hyp, ok_hyp = _LANGUAGE_HYPOTHESIS_EXAMPLES[language]
    return (
        f"You are a {lang_name} SLA syntax analyser. Given a learner's draft, produce an error diagnosis with:\n"
        "1. quote (L2): The exact broken phrase/clause from the learner's draft (never quote the entire multi-clause sentence if only a phrase is wrong).\n"
        "2. pattern_code (L3): Exactly ONE pattern code chosen from the taxonomy below.\n"
        f"{_LANGUAGE_SPECIFIC_RULES[language]}"
        f"3. explanation (L4): A concise grammatical rule hint in English that MUST NEVER contain the corrected {lang_name} words from `correction` (L5).\n"
        f"4. correction (L5): The corrected {lang_name} words replacing `quote`.\n\n"
        "Pedagogical Guidelines:\n"
        "- Clause-by-Clause Comprehensive Scan: Inspect EVERY clause in the draft (both main clauses and subordinate clauses). You MUST generate a separate card for EVERY error in the draft. Never stop after checking only a '?' marker!\n"
        "- Clean Drafts: If the learner's draft is already 100% grammatically correct, return an empty cards list (`cards: []`). Do NOT invent errors where none exist.\n"
        "- Zero Answer Leaks in L4: Write `explanation` in English describing the grammar mechanism. Never write the exact `correction` string inside `explanation`.\n"
        "- CEFR Scaffolding: If a Learner Target CEFR Level is specified, calibrate explanation (L4) wording to be clear and accessible to a learner at that level.\n"
        "- Inline Hypothesis Markers (?):\n"
        f"  Learners mark uncertain words with inline '?' (e.g. '{err_hyp}').\n"
        f"  * If an inline hypothesis contains a real error (e.g. '{err_hyp}'), create an error card for it (so `confirmed_hypotheses` stays `[]`) AND still check the rest of the sentence for other unmarked errors!\n"
        f"  * If an inline hypothesis is ALREADY CORRECT (e.g. in '{ok_hyp}'), do NOT create an error card for it; add the correct phrase to `confirmed_hypotheses`.\n"
        "- No Stylistic Overcorrection: Only flag genuine grammatical, morphosyntactic, or orthographic "
        f"errors in standard written {lang_name}. Never correct grammatically valid phrasing purely for stylistic preference.\n\n"
        "Allowed Pattern Taxonomy (L3):\n"
        f"{taxonomy_prompt_block(language)}"
    )


def get_critic_system_prompt(language: Language = Language.DE) -> str:
    lang_name = LANGUAGE_NAMES[language]
    err_hyp, _ = _LANGUAGE_HYPOTHESIS_EXAMPLES[language]
    return (
        f"You are a Senior {lang_name} SLA Pedagogical Critic. Verify the AI-generated error cards against the learner's draft.\n\n"
        "Check ONLY these 3 rules. If there are no violations, return `critiques: []` and `is_valid: true`:\n\n"
        "1. Hypothesis Marker Coverage (?):\n"
        f"   - When the draft has an incorrect '?...?' phrase (e.g. '{err_hyp}'), having an Error Card that includes '{err_hyp}' and having `Confirmed Correct Hypotheses: (None)` is 100% VALID. Do NOT complain that Confirmed Correct Hypotheses is (None) when the '?' phrase was an error!\n"
        "   - Only when a '?...?' phrase in the draft is grammatically CORRECT should it be in Confirmed Correct Hypotheses.\n"
        "   - When the draft has NO '?' markers at all, this rule automatically passes.\n\n"
        "2. Taxonomy Code Accuracy (L3):\n"
        "   - Verify each card's PatternCode matches the error between Quote and Correction using the taxonomy below.\n\n"
        "3. No Stylistic False Positives & No Missed Clause Errors:\n"
        f"   - Ensure no card flags valid standard written {lang_name} merely for style, and ensure obvious clause errors were not missed.\n\n"
        "Allowed Pattern Taxonomy:\n"
        f"{taxonomy_prompt_block(language)}"
    )


def get_writing_task_system_prompt(language: Language = Language.DE) -> str:
    lang_name = LANGUAGE_NAMES[language]
    return (
        f"You are a witty, creative {lang_name} SLA task designer. Generate a short, fun 1-2 sentence "
        f"writing prompt in English for a {lang_name} learner.\n\n"
        "Rules:\n"
        "- Make It Fun (No Boring Textbook Prompts!): Avoid dry topics like writing to a boss or landlord. "
        "Use playful, dramatic, gossipy, or slightly absurd everyday scenarios (e.g., a terrible restaurant date, "
        "a suspicious excuse for being late, a dramatic complaint about a chaotic roommate, or a pet's secret life).\n"
        "- Keep Vocabulary Accessible: Even when the scenario is funny, make sure the learner can answer using "
        f"everyday {lang_name} words appropriate for their CEFR level.\n"
        "- Explicit Grammar Constraints: Tell the learner which structures they MUST use to trigger the target patterns.\n"
        f"- NEVER write the {lang_name} target sentences for the learner!\n\n"
        "Allowed Pattern Taxonomy:\n"
        f"{taxonomy_prompt_block(language)}"
    )


# Backward-compatible constants for German defaults
SYSTEM_PROMPT = get_system_prompt(Language.DE)
CRITIC_SYSTEM_PROMPT = get_critic_system_prompt(Language.DE)
WRITING_TASK_SYSTEM_PROMPT = get_writing_task_system_prompt(Language.DE)


def build_generator_messages(
    sentence: str,
    critique: str | None = None,
    previous_analysis: Analysis | None = None,
    cefr_level: CEFRLevel | None = None,
    language: Language = Language.DE,
) -> list[BaseMessage]:
    lang_name = LANGUAGE_NAMES[language]
    user_content = f"Language: {lang_name}\nSentence: {sentence}"
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
    return [
        SystemMessage(content=get_system_prompt(language)),
        HumanMessage(content=user_content),
    ]


def build_critic_messages(
    sentence: str,
    analysis: Analysis,
    language: Language = Language.DE,
) -> list[BaseMessage]:
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
        SystemMessage(content=get_critic_system_prompt(language)),
        HumanMessage(content=user_content),
    ]


def build_writing_prompt_messages(
    cefr_level: CEFRLevel,
    target_patterns: list[PatternCode],
    language: Language = Language.DE,
) -> list[BaseMessage]:
    lang_name = LANGUAGE_NAMES[language]
    if target_patterns:
        patterns_desc = "\n".join(
            f"- {code} ({TAXONOMY[code]['name']}): {TAXONOMY[code]['hint']}"
            for code in target_patterns
        )
        user_content = (
            f"Target Language: {lang_name}\n"
            f"Learner CEFR Level: {cefr_level}\n"
            f"Target Weaknesses to Drill:\n{patterns_desc}"
        )
    else:
        user_content = (
            f"Target Language: {lang_name}\n"
            f"Learner CEFR Level: {cefr_level}\n"
            f"This learner has no recorded {lang_name} errors yet. Choose 1-2 foundational {lang_name} patterns "
            f"appropriate for {cefr_level} from the taxonomy and design a writing prompt around them."
        )
    return [
        SystemMessage(content=get_writing_task_system_prompt(language)),
        HumanMessage(content=user_content),
    ]
