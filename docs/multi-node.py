from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    message: str #user req
    issue_type1: str # res node 1 - order
    context: str # res node 2 - your order is on the way
    reply: str #res node 3 - hi 

def node_a(state: State) -> State:
    return {"issue_type1": "order"}

def node_b(state: State) -> State:
    return {"context": "Your order is on the way!"}

def node_c(state: State) -> State:
    return {"reply": f"Hi! {state['context']}"}

def node_d(state: State) -> State:
    print(state['issue_type1'])
    print(state["reply"])
    return {}

graph = StateGraph(State)

graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)

graph.set_entry_point("node_a")

graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", "node_c")
graph.add_edge("node_c", "node_d")

graph.add_edge("node_d", END)

app = graph.compile()
app.invoke({"message": "where is my order?, user prefernce"})