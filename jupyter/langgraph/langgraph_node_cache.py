from typing import TypedDict
import time


from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import START,END,StateGraph
from langgraph.types import CachePolicy

class MyState(TypedDict):
    x:int
    result:int

# 进入此节点时候，X是1
# 如何击中缓存：
# 1.图结构和映射名不变
# 2.开启缓存的节点，当前运行时，状态和之前创建缓存时一致
def node_1(state:MyState):
    print("进入计算节点")
    time.sleep(5)
    print("计算完成")
    x = state['x']
    return {"result":x*2}

def node_2(state:MyState):
    time.sleep(3)

builder = StateGraph(MyState)
builder.add_node(node_1,cache_policy=CachePolicy(ttl=2))
builder.add_node(node_2)
# 这个节点能保存上一个节点的结果10秒钟
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2",END)

cache = InMemoryCache()
checkpointer = InMemorySaver()
graph = builder.compile(cache = cache,checkpointer=checkpointer)

config_1 = {
    "configurable":{
        "thread_id":"id_1"
    }
}
config_2 = {
    "configurable":{
        "thread_id":"id_2"
    }
}

result_1 = graph.invoke({"x":1},config = config_1)
print(result_1)
result_2 = graph.invoke({"x":1},config = config_2)
print(result_2)

