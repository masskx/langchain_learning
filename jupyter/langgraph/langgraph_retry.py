from typing import TypedDict

from langgraph import graph
from langgraph.graph import START, StateGraph
from langgraph.graph.state import RetryPolicy

class MyState(TypedDict):
    result:str

attempt_count = 0

def unstable_api_call(state:MyState):
    global attempt_count
    attempt_count+=1
    if attempt_count<3:
        print(f"运行失败，这是第{attempt_count}次调用")
        raise Exception(f"运行失败，这是第{attempt_count}次调用")
    else:
        return{"result":"运行成功"}

builder = StateGraph(MyState)
builder.add_node(unstable_api_call,retry_policy=RetryPolicy(max_attempts=5))
builder.add_edge(START,"unstable_api_call")
graph = builder.compile()
result = graph.invoke({})
print(result)