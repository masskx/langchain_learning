from typing import TypedDict, List, Annotated
import operator

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class MyState(TypedDict):
    data_list:Annotated[List[str],operator.add]

def a(state:MyState):
    return {"data_list":["a"]}
def b_1(state:MyState):
    return {"data_list":["b_1"]}
def b_2(state:MyState):
    return {"data_list":["b_2"]}
def c(state:MyState):
    return {"data_list":["c"]}
def d(state:MyState):
    return {"data_list":["d"]}

builder = StateGraph(state_schema=MyState)
builder.add_node(a)
builder.add_node(b_1)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d)

builder.add_edge(START, "a")
builder.add_edge("a", "b_1")
builder.add_edge("b_1", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("a", "c")
builder.add_edge("c", "d")
builder.add_edge( "d",END)

graph = builder.compile()
result = graph.invoke({})
print(result)
