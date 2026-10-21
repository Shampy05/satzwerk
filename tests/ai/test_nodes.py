from src.ai.constants import PatternCode
from src.ai.nodes import deterministic_evaluator
from src.ai.schema import Analysis, GermanCard
from src.ai.state import State


def test_evaluator_passes_valid_card():
    card = GermanCard(
        quote="zu den Bahnhof",
        pattern_code=PatternCode.KAS_PREP,
        explanation="Nach festen Präpositionen verlangt das Nomen den Dativ.",
        correction="zum Bahnhof",
    )
    state: State = {
        "sentence": "Ich gehe zu den Bahnhof.",
        "analysis": Analysis(cards=[card], confirmed_hypotheses=[]),
        "critique": "",
        "is_valid": False,
        "iterations": 0,
    }

    result = deterministic_evaluator(state)
    assert result["is_valid"] is True
    assert result["critique"] == ""


def test_evaluator_catches_non_verbatim_quote():
    card = GermanCard(
        quote="zu dem Bahnhof",  # Not verbatim in sentence ("zu den Bahnhof")
        pattern_code=PatternCode.KAS_PREP,
        explanation="Dativ ist erforderlich.",
        correction="zum Bahnhof",
    )
    state: State = {
        "sentence": "Ich gehe zu den Bahnhof.",
        "analysis": Analysis(cards=[card], confirmed_hypotheses=[]),
        "critique": "",
        "is_valid": False,
        "iterations": 0,
    }

    result = deterministic_evaluator(state)
    assert result["is_valid"] is False
    assert "Quote was not found verbatim" in result["critique"]


def test_evaluator_catches_leaked_correction():
    card = GermanCard(
        quote="zu den Bahnhof",
        pattern_code=PatternCode.KAS_PREP,
        explanation="Du musst stattdessen zum Bahnhof verwenden.",  # Leaked!
        correction="zum Bahnhof",
    )
    state: State = {
        "sentence": "Ich gehe zu den Bahnhof.",
        "analysis": Analysis(cards=[card], confirmed_hypotheses=[]),
        "critique": "",
        "is_valid": False,
        "iterations": 0,
    }

    result = deterministic_evaluator(state)
    assert result["is_valid"] is False
    assert "leaked the answer 'zum Bahnhof'" in result["critique"]


def test_evaluator_catches_noop_correction():
    card = GermanCard(
        quote="zu den Bahnhof",
        pattern_code=PatternCode.KAS_PREP,
        explanation="Hier liegt ein Fehler vor.",
        correction="zu den Bahnhof",  # Identity / No-op!
    )
    state: State = {
        "sentence": "Ich gehe zu den Bahnhof.",
        "analysis": Analysis(cards=[card], confirmed_hypotheses=[]),
        "critique": "",
        "is_valid": False,
        "iterations": 0,
    }

    result = deterministic_evaluator(state)
    assert result["is_valid"] is False
    assert "identical to the quote" in result["critique"]


def test_evaluator_accumulates_critiques_across_cards():
    card1 = GermanCard(
        quote="halluziniert",  # Non-verbatim
        pattern_code=PatternCode.ORTH,
        explanation="Rechtschreibung anpassen.",
        correction="richtig",
    )
    card2 = GermanCard(
        quote="zu den Bahnhof",
        pattern_code=PatternCode.KAS_PREP,
        explanation="Nimm zum Bahnhof.",  # Leaked!
        correction="zum Bahnhof",
    )
    state: State = {
        "sentence": "Ich gehe zu den Bahnhof.",
        "analysis": Analysis(cards=[card1, card2], confirmed_hypotheses=[]),
        "critique": "",
        "is_valid": False,
        "iterations": 0,
    }

    result = deterministic_evaluator(state)
    assert result["is_valid"] is False
    assert "Card 1" in result["critique"]
    assert "Card 2" in result["critique"]
