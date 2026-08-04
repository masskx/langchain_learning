### 这里是给Agent调用的检索工具
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from pymilvus import MilvusClient
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.tools import tool

MILVUS_URI = "http://localhost:19530"
DB_NAME = "personal_chief"
COLLECTION_NAME = "recipes"
EMBED_MODEL_NAME = "Pro/BAAI/bge-m3"

# 懒加载，避免每次导入都初始化
_client:MilvusClient|None = None
_embed_model:OpenAIEmbeddings|None = None

def _get_client()->MilvusClient:
    global _client
    if _client is None:
        _client = MilvusClient(MILVUS_URI)
        _client.use_database(db_name=DB_NAME)
    return _client

def _get_embed_model()->OpenAIEmbeddings:
    global _embed_model
    if _embed_model is None:
        _embed_model = OpenAIEmbeddings(
            model=EMBED_MODEL_NAME,
            api_key=os.getenv("GUIJI_API_KEY"),
            base_url=os.getenv("GUIJI_BASE_URL")
        )
    return _embed_model
    
@tool
def search_local_recipes(query:str)->str:
    """
    从本地食谱知识库中搜索相关食谱
    当用户问做什么菜，做某道菜，有什么食材能做什么菜的时候优先使用该工具
    Args:query
        搜索关键字
    """
    client = _get_client()
    embed_model = _get_embed_model()
    
    # 向量化查询
    query_vector = embed_model.embed_query(query)
    # Milvus检索Top5
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=5,
        output_fields=["text","source","chunk_id"],
    )
    
    if not results or not results[0]:
        return "vending知识库中没有相关食谱哦"

    # 拼接检索结果
    parts = []
    for i,hit in enumerate(results[0],1):
        text = hit["entity"]["text"]
        score = hit["distance"]
        parts.append(f"[食谱{i}|相关度:{score:.2f}\n{text}]")

    return "\n\n--\n\n".join(parts)
