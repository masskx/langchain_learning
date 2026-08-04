好，只给示例代码，你自己动手。

改动涉及 6 个文件
1. frontend/src/App.jsx — 把模型状态提升到顶层

// 新增状态
const [model, setModel] = useState('qwen')

// 传给 useChat
const { messages, isStreaming, uploading, sendMessage, newSession, uploadFile } = useChat(model)

// 传给 Sidebar
<Sidebar
  isOpen={sidebarOpen}
  onClose={() => setSidebarOpen(false)}
  user={user}
  activeModel={model}
  onModelChange={setModel}
/>
2. frontend/src/components/Sidebar.jsx — 接收 props 替代本地 state

// props 改成
export default function Sidebar({ isOpen, onClose, user, activeModel, onModelChange }) {
  // 删掉这行：const [activeModel, setActiveModel] = useState('qwen')

  // 按钮 onClick 改成
  onClick={() => onModelChange(m.id)}
3. frontend/src/hooks/useChat.js — 传递 model 参数

// 函数签名加上 model
export function useChat(model) {

  // sendMessage 里调用 streamChat 时多传 model
  await streamChat(
    { message: text, imageUrl, threadId, model },  // ← 加了 model
    // onToken, onDone, onError 不变...
  )
}, [threadId, model])  // ← 依赖数组加上 model
4. frontend/src/api/chat.js — 请求体带上 model

export async function streamChat({ message, imageUrl, threadId, model }, onToken, onDone, onError) {
  const res = await fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      image_url: imageUrl || null,
      thread_id: threadId,
      model: model || 'qwen',   // ← 新增
    }),
  })
  // 后面不变...
}
5. app/models/schemas.py — ChatRequest 加字段

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    image_url: str | None = None
    thread_id: str = "default"
    model: str = "qwen"   # ← 新增，默认 qwen
6. app/agents/personal_chief.py — 根据 model 动态选 LLM
核心思路：当前 model 是模块级硬编码的，改成懒加载 + 缓存，按需取不同模型。


import os
from langchain_openai import ChatOpenAI

# 模型注册表
MODELS = {
    "qwen": {
        "model": "qwen3.6-flash",
        "base_url": os.getenv("BAILIAN_BASE_URL"),
        "api_key": os.getenv("BAILIAN_API_KEY"),
    },
    "deepseek": {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "base_url": os.getenv("GUIJI_BASE_URL"),
        "api_key": os.getenv("GUIJI_API_KEY"),
    },
}

_model_cache: dict[str, ChatOpenAI] = {}

def get_model(model_name: str = "qwen") -> ChatOpenAI:
    """根据模型名获取 ChatOpenAI 实例，带缓存"""
    if model_name not in _model_cache:
        cfg = MODELS.get(model_name, MODELS["qwen"])
        _model_cache[model_name] = ChatOpenAI(
            model=cfg["model"],
            base_url=cfg["base_url"],
            api_key=cfg["api_key"],
        )
    return _model_cache[model_name]


# ---- Agent 创建改成函数 ----

from langchain.agents import create_agent

def get_agent(model_name: str = "qwen"):
    """根据模型名创建 Agent 实例"""
    model = get_model(model_name)
    return create_agent(
        model=model,
        tools=[search_local_recipes, web_search],
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )


# ---- search_recipes 函数加 model 参数 ----

async def search_recipes(prompt: str, image: str, thread_id: str, model_name: str = "qwen"):
    logger.info(f"[用户]: {prompt}, model: {model_name}, thread_id: {thread_id}")
    agent = get_agent(model_name)
    # ... 后面不变
注意：原来的模块级 model 和 agent 变量删掉，改成上面的函数和缓存。

7. app/api/v1/chat.py — 把 model 传给 agent

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_stream():
        async for token in search_recipes(
            prompt=req.message,
            image=req.image_url or "",
            thread_id=req.thread_id,
            model_name=req.model,   # ← 新增
        ):
            yield token
    return StreamingResponse(event_stream(), media_type="text/event-stream")
数据流总结

用户点 Sidebar 选模型
  → App.jsx setModel('deepseek')
  → useChat.sendMessage 带 model
  → api/chat.js POST 请求体带 model: "deepseek"
  → FastAPI ChatRequest.model = "deepseek"
  → search_recipes(model_name="deepseek")
  → get_model("deepseek") → DeepSeek ChatOpenAI 实例
  → create_agent → Agent 用 DeepSeek 推理
改完后的效果：Sidebar 里点 Qwen → 走百炼 API，点 DeepSeek → 走硅基流动 API，实时切换。