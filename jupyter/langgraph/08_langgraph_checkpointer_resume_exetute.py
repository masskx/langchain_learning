import sqlite3
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import START
from langgraph.graph import StateGraph

# 展示如何在langgraph中从上次运行断掉的地方回复运行
conn = sqlite3.connect(
    database=r"D:\DevSpace\langchain\resources\07.sqlite",
    check_same_thread=False
)
# 创建检查点，不是放在内存，而是放在数据库中
memory = SqliteSaver(conn)
class MyState(TypedDict):
    key_1:str
    key_2:str
    key_3:str

def node_1(state:MyState):
    print(f"节点一的初始状态为：{state}")
    return {
        "key_1":"value_1"
    }

def node_2(state:MyState):
    print(f"节点二的初始状态为：{state}")
    # raise Exception("节点二出错")
    return {
        "key_2":"value_2"
    }

def node_3(state:MyState):
    print(f"节点三的初始状态为：{state}")
    return {
        "key_3":"value_3"
    }


builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")

graph = builder.compile(checkpointer = memory)
config = {
    "configurable":{
        'thread_id':"66"
    }
}

res = graph.invoke(None,config)
print(res)