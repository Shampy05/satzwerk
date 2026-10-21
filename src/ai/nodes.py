from typing import Literal, cast

from src.ai.llm import structured_critic_llm, structured_generator_llm
from src.ai.prompts import build_critic_messages, build_generator_messages
from src.ai.schema import Analysis, SemanticEvaluation
from src.ai.state import State
from src.config import settings


async def generator(state: State):
    print("---Node Generator---")
    messages = build_generator_messages(
        sentence=state["sentence"],
        critique=state["critique"],
        previous_analysis=state["analysis"],
    )

    result: Analysis = cast(Analysis, await structured_generator_llm.ainvoke(messages))
    return {"analysis": result, "iterations": state["iterations"] + 1}


def deterministic_evaluator(state: State):
    print("---Node Evaluator---")

    analysis = state["analysis"]
    if analysis is None:
        raise ValueError("Evaluator called before analysis was generated.")

    critiques: list[str] = []

    for i, card in enumerate(analysis.cards, start=1):
        card_label = f"Card {i} ('{card.quote}')"

        # Check 1: Verbatim Substring Check
        if card.quote not in state["sentence"]:
            critiques.append(
                f"{card_label}: Quote was not found verbatim in the sentence. Copy the "
                "exact characters from the learner's text."
            )

        # Check 2: Leak Check (L4 != L5)
        if card.correction.lower() in card.explanation.lower():
            critiques.append(
                f"{card_label}: You leaked the answer '{card.correction}' inside your explanation! "
                "Rewrite that explanation without using that phrase."
            )

        # Check 3: No-Op Check (L5 != L2)
        if card.quote.strip() == card.correction.strip():
            critiques.append(
                f"{card_label}: Correction '{card.correction}' is identical to the quote."
                "If there is an error, the correction must differ from the quote."
            )

    if critiques:
        return {"is_valid": False, "critique": "\n".join(critiques)}

    return {"is_valid": True, "critique": ""}


async def semantic_evaluator(state: State):
    print("---Node Semantic Evaluator---")
    analysis = state["analysis"]
    if analysis is None:
        raise ValueError("Semantic evaluator called before analysis was generated.")

    messages = build_critic_messages(
        sentence=state["sentence"],
        analysis=analysis,
    )

    evaluation: SemanticEvaluation = cast(
        SemanticEvaluation, await structured_critic_llm.ainvoke(messages)
    )

    if not evaluation.is_valid and evaluation.critiques:
        return {"is_valid": False, "critique": "\n".join(evaluation.critiques)}

    return {"is_valid": True, "critique": ""}
