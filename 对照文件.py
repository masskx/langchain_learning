
"""

"
@tool
def search_local_recipes(query: str) -> str:
    """
    # 从本地食谱知识库中搜索相关食谱。
    # 当用户问怎么做某道菜、有什么食材能做什么菜、或者需要食谱推荐时，优先使用此工具。
    # 参数 query: 搜索关键词，例如"西红柿鸡蛋"、"低脂健身餐"、"快手晚餐"
    """
    client = _get_client()
    embed_model = _get_embed_model()

    # 向量化查询
    query_vector = embed_model.embed_query(query)

    # Milvus 检索 top-5
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=5,
        output_fields=["text", "source", "chunk_id"],
    )

    if not results or not results[0]:
        return "本地知识库中没有找到相关食谱。"

    # 拼接检索结果
    parts = []
    for i, hit in enumerate(results[0], 1):
        text = hit["entity"]["text"]
        score = hit["distance"]
        parts.append(f"[食谱{i} | 相关度: {score:.2f}]\n{text}")

    return "\n\n---\n\n".join(parts)
第四步：修改 Agent
你需要改 app/agents/personal_chief.py：

4.1 导入检索工具
在文件顶部 import 区加一行：


from app.rag.retriever import search_local_recipes
4.2 把工具加入 Agent
create_agent 那一行，把 tools=[web_search] 改成：


agent = create_agent(
    model=model,
    tools=[search_local_recipes, web_search],
    system_prompt=system_prompt,
    checkpointer=checkpointer
)
4.3 更新系统提示词
system_prompt 改成引导 Agent 先搜本地、本地没有再用 Tavily：


system_prompt = """
# 你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
# 1. 识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态，评估其新鲜度与可用量，整理出一份"当前可用食材清单"。
# 2. 智能食谱检索：首先调用 search_local_recipes 工具从本地知识库检索匹配食谱。如果本地搜索结果不足3个或相关性不高，再调用 web_search 工具从互联网补充搜索。
# 3. 多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序，制作简单且营养丰富的排名靠前。
# 4. 结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告，要包含食谱信息、得分、推荐理由，帮助用户快速做出决策。

# 请严格按照流程，优先调用 search_local_recipes 工具搜索本地食谱，本地搜索不足时才调用 web_search 工具。
"""
第五步：运行 & 验证
5.1 确保 Milvus 在跑

docker-compose up -d
docker ps  # 确认 milvus-standalone 是 healthy
5.2 入库食谱数据

python -m app.rag.ingest
预期输出：成功插入 N 条记录

5.3 启动应用

python -m app.main
5.4 测试
在聊天界面问 "西红柿和鸡蛋能做什么菜？"，观察 Agent 是否走了 search_local_recipes 工具。你也可以在后端日志里看到工具调用情况。

操作清单
步骤	做什么	涉及文件
1	uv add pymilvus langchain-community langchain-text-splitters	pyproject.toml
2	写 10-15 道食谱	新建 resources/recipes.txt
3	创建入库脚本	新建 app/rag/ingest.py
4	创建检索工具	新建 app/rag/retriever.py
5	改 Agent：导入工具、加到 tools、更新 prompt	改 app/agents/personal_chief.py
6	跑 docker-compose up -d → 跑入库脚本 → 启动应用测试	—
有任何一步卡住了随时说，我帮你排查。做完这个之后，你的 Agent 就是 "本地知识库 + 联网搜索" 双工具驱动的了，和 agentic_rag.ipynb 学的模式完全一致。
""
