from typing import TypedDict
import time


from langchain_core.caches import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import START,END,StateGraph
from langgraph.types import CachePolicy

class MyState(TypedDict):
    x:int
    result:int

def node_1(state:MyState):
    print("进入计算节点")
    time.sleep(5)
    print("计算完成")
    x = state['x']
    return {"result":x*2}

builder = StateGraph(MyState)
builder.add_node(node_1,cache_policy=CachePolicy(ttl=10))
# 这个节点能保存上一个节点的结果10秒钟
builder.add_edge(START,"node_1")
builder.add_edge("node_1",END)

cache = InMemoryCache()
checkpointer = InMemorySaver()
graph = builder.compile(cache = cache,checkpointer=checkpointer)

config_1 = {
    "configurable":{
        "thread_id":"id_1"
    }
}

result_1 = graph.invoke({"x":1},config = config_1)
print(result_1)
