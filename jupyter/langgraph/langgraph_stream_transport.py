# langgraph的流式输出

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


class MyState(TypedDict):
    value_1:str
    value_2:str
    value_3:str

def node_1(state:MyState,runtime:Runtime):
    writer = runtime.stream_writer
    writer({
        "node_name":"node_1",
        "status":"succed",
        "description":"节点一运行成功"
    })
    return {"value_1":"111"}

def node_2(state:MyState):
    return {"value_2":"222"}

def node_3(state:MyState):
    return {"value_3":"333"}

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)

builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")
builder.add_edge("node_3",END)

graph = builder.compile()
# for event in graph.stream({},stream_mode="values"):
#     print(event)

# for event in graph.stream({},stream_mode="updates"):
#     print(event)

# for event in graph.stream({},stream_mode="debug"):
#     print(event)

# for event in graph.stream({},stream_mode="custom"):
#     print(event)

for event in graph.stream({},stream_mode=["updates","debug"]):
    print(event)