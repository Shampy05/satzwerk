from langgraph.graph import END, START, StateGraph

from src.ai.edges import decide_after_deterministic, decide_after_semantic
from src.ai.nodes import deterministic_evaluator, generator, semantic_evaluator
from src.ai.state import State

builder = StateGraph(State)

builder.add_node("generator", generator)
builder.add_node("deterministic_evaluator", deterministic_evaluator)
builder.add_node("semantic_evaluator", semantic_evaluator)

builder.add_edge(START, "generator")
builder.add_edge("generator", "deterministic_evaluator")

builder.add_conditional_edges(
    "deterministic_evaluator",
    decide_after_deterministic,
    {
        "semantic_evaluator": "semantic_evaluator",
        "generator": "generator",
        "end": END,
    },
)

builder.add_conditional_edges(
    "semantic_evaluator",
    decide_after_semantic,
    {
        "generator": "generator",
        "end": END,
    },
)

graph = builder.compile()
