from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.ai.constants import taxonomy_prompt_block
from src.ai.schema import Analysis

SYSTEM_PROMPT = (
    "You are a German SLA syntax analyser. Given a learner's draft, produce an error diagnosis with:\n"
    "1. quote (L2): The exact broken words from the learner's draft.\n"
    "2. pattern_code (L3): Exactly ONE pattern code chosen from the taxonomy below.\n"
    "3. explanation (L4): A concise grammatical rule hint that MUST NOT contain any words from the correction.\n"
    "4. correction (L5): The corrected words.\n\n"
    "Pedagogical Guidelines:\n"
    "- Inline Hypothesis Markers: Learners mark uncertain words or structures with inline '?' "
    "(e.g., '?zu den?' or 'zu den?'). You MUST inspect and address every marked hypothesis.\n"
    "- No Stylistic Overcorrection: Only flag genuine grammatical, morphosyntactic, or orthographic "
    "errors. Never correct grammatically valid phrasing purely for stylistic preference.\n\n"
    "Allowed Pattern Taxonomy (L3):\n"
    f"{taxonomy_prompt_block()}"
)

CRITIC_SYSTEM_PROMPT = (
    "You are a Senior German SLA Pedagogical Critic. Your job is to verify AI-generated error diagnosis "
    "cards against a learner's draft.\n\n"
    "Crucial Context:\n"
    "- Cards exist to diagnose genuine grammatical, word order, case, and spelling errors in the learner's draft.\n"
    "- Most drafts will NOT contain any '?' markers. Error cards are expected whenever the learner makes an error!\n\n"
    "You must evaluate three strict criteria:\n\n"
    "1. Hypothesis Marker Coverage (?):\n"
    "   Learners may optionally mark words they felt uncertain about using inline '?' (e.g. '?zu den?' or 'zu den?').\n"
    "   - If the draft contains inline '?' markers, verify that each marked hypothesis was addressed by a card.\n"
    "   - If the draft contains NO '?' markers, this check PASSES completely. Do NOT penalize cards or claim cards shouldn't exist just because there are no '?' markers.\n\n"
    "2. Taxonomy Code Accuracy (L3):\n"
    "   Verify that each card's pattern_code accurately matches the error transition using ONLY the 24 allowed codes.\n"
    "   - KAS-PREP is the correct code for prepositional case errors (e.g. 'zu' + dative).\n"
    "   - WO-VF is the correct code for verb-final position in subordinate clauses (e.g. 'weil ...').\n"
    "   Do NOT reject standard, valid taxonomy codes.\n\n"
    "3. No Stylistic False Positives:\n"
    "   Ensure no cards flag grammatically valid German just for stylistic preference.\n\n"
    "If any check fails, return is_valid=False and provide targeted, actionable critiques for the generator. "
    "If all checks pass, return is_valid=True with an empty critiques list."
)


def build_generator_messages(
    sentence: str, critique: str | None, previous_analysis: Analysis | None = None
) -> list[BaseMessage]:
    user_content = f"Sentence: {sentence}"

    if previous_analysis and previous_analysis.cards and critique:
        attempt_summary = "\n".join(
            f"Card {i} ('{c.quote}'): Pattern={c.pattern_code.value}, Explanation='{c.explanation}'"
            for i, c in enumerate(previous_analysis.cards, start=1)
        )
        user_content += (
            f"\n\nYour previous attempt produced:\n{attempt_summary}\n\n"
            f"Critique to fix: \n{critique}"
        )
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_content)]


def build_critic_messages(sentence: str, analysis: Analysis) -> list[BaseMessage]:
    cards_summary = (
        "\n".join(
            f"Card {i} ('{c.quote}'): Pattern={c.pattern_code.value}, Explanation='{c.explanation}', Correction='{c.correction}'"
            for i, c in enumerate(analysis.cards, start=1)
        )
    ) or "(No error cards generated)"

    user_content = (
        f"Learner Draft: {sentence}\n\n"
        f"Generated Cards:\n{cards_summary}\n\n"
        "Evaluate the cards against the 3 criteria (Hypothesis Markers, Taxonomy Accuracy, No Stylistic False Positives)."
    )

    return [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
