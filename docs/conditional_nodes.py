from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class State(TypedDict):
    message: str       # user request
    issue_type: str   # set by node_a — drives the conditional route
    context: str       # set by node_b (order) or node_e (refund)
    reply: str         # set by node_c

def node_a(state: State) -> State:
    """Classify the user's issue from their message."""
    message = state["message"].lower()
    if "refund" in message:
        issue_type = "refund"
    elif "order" in message:
        issue_type = "order"
    else:
        issue_type = "general"
    return {"issue_type": issue_type}

def node_b(state: State) -> State:
    """Handle order tracking issues."""
    return {"context": "Your order is on the way!"}

def node_e(state: State) -> State:
    """Handle refund issues."""
    return {"context": "Your refund has been initiated."}

def node_f(state: State) -> State:
    """Handle general / unknown issues."""
    return {"context": "How can I help you today?"}

def node_c(state: State) -> State:
    return {"reply": f"Hi! {state['context']}"}

def node_d(state: State) -> State:
    print("Issue type :", state["issue_type"])
    print("Reply      :", state["reply"])
    return {}

# Conditional router 
def route_by_issue(state: State) -> Literal["node_b", "node_e", "node_f"]:
    """Reads issue_type from state and returns the next node name."""
    issue = state["issue_type"]
    if issue == "order":
        return "node_b"
    elif issue == "refund":
        return "node_e"
    else:
        return "node_f"


graph = StateGraph(State)

graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)
graph.add_node("node_e", node_e)
graph.add_node("node_f", node_f)

graph.set_entry_point("node_a")

graph.add_conditional_edges(
    "node_a",          # source node
    route_by_issue,    # router function — returns a node name string
    {
        "node_b": "node_b",   # order   → node_b
        "node_e": "node_e",   # refund  → node_e
        "node_f": "node_f",   # general → node_f
    }
)

graph.add_edge("node_b", "node_c")
graph.add_edge("node_e", "node_c")
graph.add_edge("node_f", "node_c")
graph.add_edge("node_c", "node_d")
graph.add_edge("node_d", END)

app = graph.compile()

app.invoke({"message": "where is my order?"})
app.invoke({"message": "I want a refund"})
app.invoke({"message": "hello, need help"})