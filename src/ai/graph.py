from langgraph.graph import END, START, StateGraph

from src.ai.nodes import decide, evaluator, generator
from src.ai.state import State

builder = StateGraph(State)

builder.add_node("generator", generator)
builder.add_node("evaluator", evaluator)

builder.add_edge(START, "generator")
builder.add_edge("generator", "evaluator")
builder.add_conditional_edges(
    "evaluator", decide, {"generator": "generator", "end": END}
)

graph = builder.compile()
