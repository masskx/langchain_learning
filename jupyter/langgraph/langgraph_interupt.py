from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START
from langgraph.graph.state import StateGraph
from langgraph.types import Command, interrupt

class MyState(TypedDict):
    user_input:str
    result:str

def node_1(state:MyState):
    user_input = state['user_input']
    print(f"获得了用户的输入{user_input}")

    data  = interrupt(
        {
            "node":"node_1",
            "description":"现在需要用户提供一些额外的补充信息",
            "date":"2026/7/4"
        }
    )
    print(data)

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_edge(START,"node_1")
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {
    "configurable":{
        "thread_id":"id2"
    }
}
response = graph.invoke({"user_input":"哈哈"},config=config)
print(response)
response = graph.invoke(Command(resume={"permit":"允许"}),config=config)
print(response)