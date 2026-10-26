from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict

class State(TypedDict):
    messages: list[str]
    step: int

def node_a(state: State) -> State:
    print(f"  [node_a] step={state['step']}")
    return {"messages": state["messages"] + ["node_a ran"], "step": state["step"] + 1}

def node_b(state: State) -> State:
    print(f"  [node_b] step={state['step']}")
    return {"messages": state["messages"] + ["node_b ran"], "step": state["step"] + 1}

builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}

# -------------------------------------------------------------GET 
# graph.invoke({"messages": ["hello"], "step": 0}, config=config)

# snapshot = graph.get_state(config)

# print("Current state values :", snapshot.values)
# print("Next node(s)         :", snapshot.next)
# print("Step number          :", snapshot.metadata["step"])

# print("\n── Full checkpoint history ──")
# for snap in graph.get_state_history(config):
#     print(f"  step={snap.metadata['step']}  next={snap.next}  values={snap.values}")

# ----------------------------------UPDATE 
# graph.invoke({"messages": ["hello"], "step": 0}, config=config)

# before = graph.get_state(config)
# print("Before:", before.values, before.next, before.tasks,"+++++++++++++++++ before ++++++++++++++++")

# new_config = graph.update_state(
#     config,
#     values={"messages": ["manually injected message"], "step": 99},
#     as_node="node_a",
# )

# after = graph.get_state(config)
# print("After :", after.values, after.next ,"+++++++++++++++++++++ after +++++++++++++++")

# print("New checkpoint_id:", new_config["configurable"]["checkpoint_id"])

# # ----------------------REPLAY
graph.invoke({"messages": ["hello"], "step": 0}, config=config)

history = list(graph.get_state_history(config))
print(history,"HISTORY")
target_checkpoint = history[1]   
target_checkpoint_id = target_checkpoint.config["configurable"]["checkpoint_id"]

print("Replaying from checkpoint:", target_checkpoint_id)
print("State at that point      :", target_checkpoint.values)

replay_config = {
    "configurable": {
        "thread_id": "thread-1",
        "checkpoint_id": target_checkpoint_id,
    }
}

result = graph.invoke(None, replay_config)  

print("Result after replay:", result)


graph.invoke({"messages": ["Hi ur an idiot "], "step": 0}, config=config)
history = list(graph.get_state_history(config))
print(history,"HISTORY 1")
target_checkpoint = history[1]   
target_checkpoint_id = target_checkpoint.config["configurable"]["checkpoint_id"]

print("Replaying from checkpoint 1:", target_checkpoint_id)
print("State at that point 1     :", target_checkpoint.values)