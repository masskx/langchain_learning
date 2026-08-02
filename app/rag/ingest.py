# 这个脚本只跑一次，将菜谱向量化之后保存在数据库
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from pymilvus import MilvusClient
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

#######配置
MILVUS_URI = "http://localhost:19530"
DB_NAME = "personal_chief"
COLLECTION_NAME = "recipes"
EMBED_MODEL_NAME = "Pro/BAAI/bge-m3"
EMBED_MODEL_DIM = 1024
RECIPES_FILE = r"D:\DevSpace\langchain\resources\recipes.txt"

########连接数据库
client = MilvusClient(MILVUS_URI) # 这里不懂怎么创建客户端？
databases = client.list_databases()
if DB_NAME not in databases:
    client.create_database(db_name=DB_NAME)
client.use_database(db_name=DB_NAME)

# 如果collection已存在，就删掉重建
if client.has_collection(collection_name=COLLECTION_NAME): # 这里不懂为什么删掉？
    client.drop_collection(collection_name=COLLECTION_NAME)

client.create_collection( # 创建collection
    collection_name=COLLECTION_NAME, # 给collection起名字
    dimension=EMBED_MODEL_DIM, # 编码维度
    metric_type="COSINE" # 注意拼写
)

# 加载和切分文档
loader = TextLoader(RECIPES_FILE,encoding="utf-8")
documents = loader.load()
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap=50,
    separators=[
        "\n==============================\n",  # 优先按分隔线切
        "\n\n",
        "\n",
        "。",
        " ",
        "",
    ]
)

chunks = splitter.split_documents(documents=documents)
print(f"文档被切分为{len(chunks)}个chunk")

######向量化
embed_model = OpenAIEmbeddings(
    model = EMBED_MODEL_NAME,
    api_key=os.getenv("GUIJI_API_KEY"),
    base_url=os.getenv("GUIJI_BASE_URL")
)

texts = [chunk.page_content for chunk in chunks]
vectors = embed_model.embed_documents(texts)

# 写入milvus
data = [
    {
        "id":i,
        "vector":vectors[i],
        "text":chunks[i].page_content,
        "source":RECIPES_FILE,
        "chunk_id":i
    }
    for i in range(len(chunks))
]

insert_res = client.upsert(collection_name=COLLECTION_NAME,data=data)
client.flush(collection_name=COLLECTION_NAME)
print(f"成功插入{insert_res['upsert_count']}条记录")
stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"Collections 统计{stats}")