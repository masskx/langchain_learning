# 🍳 DevChef — 程序员的 AI 私厨

> 全栈 AI Agent 应用 · 每一个程序员都值得拥有一个懂他的私人厨师。

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://www.langchain.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 目录

- [项目定位](#项目定位)
- [系统架构](#系统架构)
- [技术选型与决策](#技术选型与决策)
- [功能模块详解](#功能模块详解)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [前端设计](#前端设计)
- [数据流](#数据流)
- [安全性](#安全性)
- [路线图](#路线图)
- [面试要点（Talking Points）](#面试要点-talking-points)
- [学习笔记](#学习笔记)

---

## 项目定位

**DevChef** 是一个面向程序员的 AI 私厨助手。核心差异化在于：不是泛用菜谱推荐，而是**根据用户的岗位、作息和饮食习惯，推理最适合的膳食方案**。

### 为什么是"程序员私厨"？

| 岗位 | 典型作息 | 饮食痛点 | Agent 策略 |
|------|----------|----------|-------------|
| 后端开发 | 久坐、熬夜 on-call | 肠胃负担重、夜宵需求 | 推荐易消化高蛋白、可批量预制 |
| 前端开发 | 盯像素、频繁沟通 | 用眼疲劳、饮食不规律 | 护眼食材、15 分钟快手菜 |
| DevOps/SRE | 高压、随时待命 | 应激性进食、咖啡依赖 | 稳定血糖低 GI、富含 B 族 |
| 算法工程师 | 深度思考、长时间专注 | 脑力消耗大、忘记吃饭 | 高 DHA、抗氧化、坚果加餐 |

### 核心链路

```
用户上传食材图片 / 文字描述
        │
        ▼
┌──────────────────────────────────────────────────┐
│              FastAPI (SSE 流式响应)                 │
│                                                    │
│  POST /api/v1/chat/stream                         │
│    ├── 接收 ChatRequest (message, image_url,       │
│    │                    thread_id)                 │
│    └── 返回 StreamingResponse (text/event-stream) │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│                 Agent 层 (LangGraph)               │
│                                                    │
│  1. 系统提示词注入（角色 + 推理流程）                │
│  2. 工具调用 ─── Tavily 搜索菜谱                   │
│  3. ReAct 推理循环（思考→行动→观察→再思考）         │
│  4. 流式输出 (AIMessageChunk)                      │
│  5. Checkpoint 持久化 (SQLite)                     │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│                  数据层                            │
│                                                    │
│  ├── Milvus 向量库 (RAG 菜谱检索)                  │
│  ├── SQLite (LangGraph Checkpoint 会话持久化)       │
│  └── 阿里云 OSS (食材图片存储)                      │
└──────────────────────────────────────────────────┘
```

---

## 系统架构

### 分层设计

```
┌──────────────────────────────────────┐
│           React 前端 (SPA)           │  ← 展示层
│   Vite + Tailwind + React 18        │
├──────────────────────────────────────┤
│         FastAPI 网关层               │  ← 路由 / CORS / 静态文件
│   SSE Streaming / REST              │
├──────────────────────────────────────┤
│         Agent 编排层                 │  ← LangGraph Agent + Tools
│   ReAct Loop / Tool Calling         │
├──────────────────────────────────────┤
│         状态持久化层                  │  ← LangGraph Checkpoint (SQLite)
│   多轮对话记忆 / 用户偏好             │
├──────────────────────────────────────┤
│         基础设施层                    │  ← Milvus / OSS / Tavily
│   向量检索 / 对象存储 / 搜索引擎      │
└──────────────────────────────────────┘
```

每层职责单一，替换任何一层不影响其他——比如换一个模型提供商只需改 `ChatOpenAI` 的 `base_url`，不需要动 Agent 逻辑。

### 技术栈全景

| 层级 | 技术 | 为什么选它 |
|------|------|-----------|
| **前端框架** | React 18 + Vite | Vite HMR 极快，构建产物直接输出到 `app/static/` 实现前后端一体化部署 |
| **样式方案** | Tailwind CSS 3.4 | 原子化 CSS，配合 `backdrop-blur` 实现毛玻璃 UI |
| **图标库** | Lucide React | Tree-shaking，按需加载，不会像 Font Awesome 整个打包 |
| **AI 编排** | LangChain 0.3 + LangGraph | Agent 创建、工具绑定、Checkpoint 持久化一站式 |
| **推理框架** | ReAct (Reasoning + Acting) | 思考→行动→观察循环，比纯 Tool Calling 更可控 |
| **模型** | 通义千问 Qwen3.6 + DeepSeek-V4 | OpenAI 兼容接口，可无缝切换 |
| **搜索工具** | Tavily Search API | 专为 AI Agent 优化的搜索，返回结构化结果 |
| **后端框架** | FastAPI 0.115 | 原生异步 (`async def`)，原生 SSE (`StreamingResponse`) |
| **向量数据库** | Milvus 2.6 | 支持混合检索，Docker 一键部署 |
| **关系存储** | SQLite | 零配置，`check_same_thread=False` 适配异步环境 |
| **对象存储** | 阿里云 OSS | 预签名 URL 上传，前端直传不经过后端 |
| **容器化** | Docker Compose | Milvus (etcd + MinIO) 三件套一键起 |
| **包管理** | uv | Rust 实现，比 pip 快 10-100 倍 |
| **异步** | Python asyncio | Agent 流式调用 + SSE 推送的全链路异步 |

---

## 技术选型与决策

### 1. 为什么用 LangGraph 而不是纯 LangChain？

LangChain 的 `create_agent` 底层就是 LangGraph 构建的图。关键区别是 **Checkpoint 机制**：
- 每一轮对话自动保存状态快照
- `thread_id` 隔离不同用户/会话
- SQLite 持久化，服务重启不丢失

```python
# app/agents/personal_chief.py
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=system_prompt,
    checkpointer=checkpointer  # ← LangGraph 的核心能力
)
# 流式调用时传入 thread_id，自动按会话隔离
agent.stream(
    {"messages": [message]},
    {"configurable": {"thread_id": thread_id}},
    stream_mode="messages"
)
```

### 2. 为什么用 SSE 而不是 WebSocket？

| 场景 | SSE | WebSocket |
|------|-----|-----------|
| 单向推送（服务端→客户端） | ✅ 原生支持 | 可以但重 |
| 自动重连 | ✅ 浏览器内置 | ❌ 需手写 |
| HTTP/2 多路复用 | ✅ | ❌ |
| 穿透代理/防火墙 | ✅ 标准 HTTP | ❌ 需要 upgrade |

对话场景是**服务端单向流式推送 token**，客户端只需要接收，SSE 是最佳匹配。代码量也最小：FastAPI 的 `StreamingResponse` 一行搞定。

### 3. 为什么图片上传用 OSS 预签名 URL 而不是 `multipart/form-data`？

```
传统方式:  浏览器 → FastAPI → OSS    （后端成为瓶颈，吃内存带宽）
预签名方式: 浏览器 ──PUT──→ OSS       （直传，后端只签发一个临时 URL）
```

- 大文件不经过 FastAPI，后端只需要返回一个签名的 URL
- 支持断点续传（OSS SDK）
- 前端上传进度不受后端限制

### 4. 前后端同源部署

Vite build 产物直接输出到 `app/static/`，FastAPI 通过 `StaticFiles` 挂载：

```python
# app/main.py
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
```

开发时 Vite dev server 通过 proxy 转发 `/api` 到 FastAPI，生产环境只需启动一个 Python 进程。

---

## 功能模块详解

### Agent 引擎（[app/agents/personal_chief.py](app/agents/personal_chief.py)）

```
系统提示词设计（4 步推理链）:
  1. 识别和评估食材  →  分析新鲜度、可用量
  2. 智能食谱检索    →  Tavily 搜索 + RAG 本地菜谱库
  3. 多维度评分排序  →  营养价值 + 制作难度 + 耗时
  4. 结构化方案输出  →  食谱信息、得分、理由、参考图片
```

**设计要点**：
- 优先级指令：`优先调用 web_search 工具搜索食谱，搜索不到才自己发挥` 防止幻觉
- 异常处理：Agent 调用失败时返回降级文案，不会暴露内部错误
- 多模态输入：根据是否有图片自动组装不同的 `HumanMessage` 格式

```python
# 无图片：纯文本消息
message = HumanMessage(content=prompt)
# 有图片：多模态消息（image_url + text）
message = HumanMessage(content=[
    {"type": "image", "url": image},
    {"type": "text", "text": prompt}
])
```

### Tool 定义（[jupyter/tool.ipynb](jupyter/langchain/tool.ipynb)）

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

class QueryTicketsSchema(BaseModel):
    ticket_id: Optional[str] = Field(default=None, description="工单ID")
    status: Optional[Literal["open", "resolved", "closed"]] = Field(
        default=None, description="工单状态"
    )

    @field_validator("ticket_id")
    def validate_ticket_id(cls, v):
        return v.upper() if v else None  # 自动规范化 LLM 的输入

@tool(args_schema=QueryTicketsSchema)
def query_tickets(ticket_id=None, status=None, ...):
    """根据条件查询工单"""
    # 链式过滤：传什么参数就筛什么
    ...
```

**面试亮点**：
- `Literal` 约束参数枚举值 → LLM 不会传无效状态
- `field_validator` 输入规范化 → 大小写自动处理
- `Field(description=...)` → 描述直接暴露给 LLM 的 Function Calling Schema

### 记忆管理（LangGraph Checkpoint）

```
thread_id_张三 → [消息1, 消息2, 消息3, ...]  ← 张三的完整对话
thread_id_李四 → [消息1, 消息2, ...]        ← 李四的完整对话

存储介质: SQLite (resources/checkpoint.db)
API:
  GET    /api/v1/chat/messages?thread_id=xxx   → 查询历史
  DELETE /api/v1/chat/messages?thread_id=xxx   → 清空会话
```

每个程序员 = 一个 `thread_id` = 一个独立 Chef Agent，偏好和习惯完全隔离。

### RAG 菜谱检索（规划中，基础设施就绪）

```
菜谱文档 → Embedding (Qwen) → Milvus 向量库
用户查询 → Embedding → 相似度检索 → Top-K 相关菜谱 → 注入 Agent 上下文
```

| 组件 | 技术 | 状态 |
|------|------|------|
| 向量存储 | Milvus 2.6 (Docker) | ✅ 已部署 |
| Embedding | 通义千问 Embedding | 🔜 待接入 |
| 文档分块 | LangChain Text Splitter | 🔜 待实现 |
| 菜谱结构化 | Markdown → Pydantic Model | 🔜 待整理 |

### 前端（[frontend/](frontend/)）

| 组件 | 文件 | 职责 |
|------|------|------|
| `App` | [App.jsx](frontend/src/App.jsx) | 根布局：毛玻璃背景 + 渐变装饰 Blob |
| `Header` | [Header.jsx](frontend/src/components/Header.jsx) | Logo + 新建会话按钮 |
| `ChatArea` | [ChatArea.jsx](frontend/src/components/ChatArea.jsx) | 空状态引导 / 消息列表 / 自动滚动 |
| `MessageBubble` | [MessageBubble.jsx](frontend/src/components/MessageBubble.jsx) | 用户/AI 双向气泡 + 流式光标动画 |
| `InputArea` | [InputArea.jsx](frontend/src/components/InputArea.jsx) | 图片预览 + textarea 自适应 + 发送 |
| `useChat` | [useChat.js](frontend/src/hooks/useChat.js) | 状态管理：消息、流式、上传、持久化 |
| `chat.js` | [chat.js](frontend/src/api/chat.js) | API 封装：SSE Stream 读取、OSS 上传 |

**UX 细节**：
- 流式光标：AI 输出时显示闪烁竖线，完成时消失
- 三点等待动画：AI 思考中但还没内容时的 `dotPulse` 动画
- 自动滚动：新消息到达时 `scrollIntoView({ behavior: 'smooth' })`
- 图片上传中遮罩：上传时图片上覆盖半透明 + spinner
- textarea 自适应高度：`scrollHeight` 动态调整，上限 120px
- `thread_id` 持久化：`localStorage` 存储，刷新页面保持同一会话
- Enter 发送 / Shift+Enter 换行

---

## 项目结构

```
langchain/
├── app/                          # FastAPI 后端
│   ├── main.py                   # 入口：FastAPI 实例化、CORS、路由挂载、SPA fallback
│   ├── api/v1/
│   │   ├── chat.py               # POST /chat/stream · GET /chat/messages · DELETE /chat/messages
│   │   └── oss.py                # GET /oss/presign?filename=xxx → 返回预签名上传 URL
│   ├── agents/
│   │   └── personal_chief.py     # Agent 定义：模型、工具、系统提示词、流式对话、记忆管理
│   ├── models/
│   │   └── schemas.py            # ChatRequest (Pydantic BaseModel)
│   ├── common/
│   │   └── logger.py             # 日志配置（stdout + 可选文件）
│   └── static/                   # 前端构建产物（Vite build 输出）
├── frontend/                     # React SPA
│   ├── src/
│   │   ├── App.jsx               # 根组件
│   │   ├── main.jsx              # ReactDOM 入口
│   │   ├── index.css             # Tailwind 指令 + 自定义动画
│   │   ├── api/chat.js           # fetch 封装：SSE Stream / REST
│   │   ├── hooks/useChat.js      # 核心状态 Hook
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ChatArea.jsx
│   │       ├── MessageBubble.jsx
│   │       └── InputArea.jsx
│   ├── vite.config.js            # Proxy + build.outDir = ../app/static
│   ├── tailwind.config.js        # 自定义 chef 色板 + 动画 keyframes
│   └── package.json
├── jupyter/                      # 学习笔记（12 个 notebook）
│   ├── 01_hello_world.ipynb      # LangChain 入门
│   ├── 02_models.ipynb           # 多模型调用（OpenAI 兼容接口）
│   ├── 03_messages.ipynb         # System / Human / AI Message
│   ├── 04_prompt.ipynb           # Prompt Template 工程
│   ├── 05_tools.ipynb            # Tool / Function Calling
│   ├── tool.ipynb                # Pydantic Schema + field_validator + Literal
│   ├── memory.ipynb              # LangGraph Checkpoint 记忆管理
│   ├── rag.ipynb                 # RAG + Milvus 向量检索
│   ├── ReAct.ipynb               # ReAct 推理模式
│   ├── agentic_rag.ipynb         # Agentic RAG（Agent 驱动的检索）
│   ├── project01.ipynb           # 项目实战：FastAPI + Agent
│   └── middle_ware.ipynb         # 请求/响应中间件
├── common/                       # 共享工具
│   └── init_llm.py               # LLM 工厂：DeepSeek / Qwen 实例
├── async/
│   └── learning_async.py         # Python asyncio 协程笔记
├── resources/
│   └── checkpoint.db             # LangGraph 对话状态（SQLite）
├── docker-compose.yml            # Milvus + etcd + MinIO
├── pyproject.toml                # 项目元数据 + 依赖
└── .env                          # 环境变量（API Key 等）
```

---

## 快速开始

### 1. 安装依赖

```bash
uv sync            # Python 依赖
cd frontend && npm install && cd ..   # 前端依赖
```

### 2. 配置环境变量

```bash
cp .env.example .env   # 编辑填入 API Key
```

| 变量 | 用途 |
|------|------|
| `TAVILY_API_KEY` | Tavily 搜索（Agent Tool） |
| `BAILIAN_BASE_URL` | 百炼模型 API 地址 |
| `BAILIAN_API_KEY` | 百炼模型 API Key |
| `GUIJI_BASE_URL` | SiliconFlow / 硅基流动 API 地址 |
| `GUIJI_API_KEY` | SiliconFlow API Key |
| `OSS_ACCESS_KEY_ID` | 阿里云 OSS AccessKey |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 OSS SecretKey |
| `OSS_BUCKET` | OSS Bucket 名称 |
| `OSS_ENDPOINT` | OSS Endpoint（默认 `oss-cn-beijing.aliyuncs.com`） |

### 3. 启动基础设施

```bash
# Milvus 向量数据库（RAG 需要）
docker-compose up -d

# 验证
docker ps  # 应看到 milvus-standalone、milvus-etcd、milvus-minio
```

### 4. 启动服务

```bash
# 后端（开发模式，热重载）
python -m app.main          # http://127.0.0.1:8001

# 前端（开发模式，HMR）
cd frontend && npm run dev  # http://localhost:5173

# 生产构建
cd frontend && npm run build  # 输出到 app/static/
python -m app.main            # 前后端一体化：http://127.0.0.1:8001
```

---

## API 文档

### 接口一览

| 方法 | 路径 | Content-Type | 说明 |
|------|------|-------------|------|
| `POST` | `/api/v1/chat/stream` | `text/event-stream` | 流式对话（SSE） |
| `GET` | `/api/v1/chat/messages` | `application/json` | 查询历史消息 |
| `DELETE` | `/api/v1/chat/messages` | `application/json` | 清空会话 |
| `GET` | `/api/v1/oss/presign` | `application/json` | 获取 OSS 上传凭证 |

### POST /api/v1/chat/stream

请求体：
```json
{
  "message": "今天加班好累，有什么简单又能填饱肚子的？",
  "image_url": "https://bucket.oss-cn-beijing.aliyuncs.com/fridge.jpg",
  "thread_id": "user_zhangsan"
}
```

响应：SSE 流，每个 chunk 是一段文本 token，客户端逐块拼接渲染。

```
data: 根据
data: 你冰箱里
data: 的食材
data: ...
```

### GET /api/v1/chat/messages?thread_id=xxx

响应：
```json
{
  "messages": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

### DELETE /api/v1/chat/messages?thread_id=xxx

响应：
```json
{ "success": true }
```

### GET /api/v1/oss/presign?filename=photo.jpg

响应：
```json
{
  "uploadUrl": "https://bucket.oss-cn-beijing.aliyuncs.com/photo.jpg?Signature=...",
  "contentType": "image/jpeg",
  "accessUrl": "https://bucket.oss-cn-beijing.aliyuncs.com/photo.jpg"
}
```

前端拿到 `uploadUrl` 后直接 `PUT` 上传文件到 OSS，上传成功后用 `accessUrl` 传给对话接口。

---

## 前端设计

### 状态管理（useChat Hook）

```
useChat() 返回:
  ├── messages:     Message[]     消息列表（user + assistant）
  ├── isStreaming:  boolean       是否正在流式输出
  ├── uploading:    boolean       是否正在上传图片
  ├── threadId:     string        当前会话 ID
  ├── sendMessage   (text, imageUrl?) => void
  ├── newSession    () => void
  └── uploadFile    (File) => Promise<string>  返回 OSS accessUrl
```

**关键实现细节**：

1. **流式接收**：用 `fetch` + `ReadableStream` 逐块读取 SSE 响应，不依赖 EventSource（EventSource 不支持 POST）
2. **乐观更新**：用户消息立即显示，AI 消息先占位（空内容 + `streaming: true`），token 到达后逐步填充
3. **线程安全**：`abortRef` 防止组件卸载后 setState
4. **会话持久化**：`threadId` 存 `localStorage`，页面刷新不丢会话

### UI 设计系统

| 元素 | 设计 |
|------|------|
| 背景 | 固定层：渐变 `from-amber-50 via-orange-50/50 to-rose-50/30` + 三色毛玻璃 Blob |
| 导航栏 | `backdrop-blur-xl` 毛玻璃，渐变 Logo 图标 |
| 用户气泡 | 右对齐，渐变暖色 `from-amber-50 to-orange-100`，圆角 16px |
| AI 气泡 | 左对齐，`bg-white/80` + `backdrop-blur-sm`，圆角 16px |
| 流式光标 | `w-1.5 h-4 bg-amber-500 rounded-full` 脉冲动画 |
| 思考动画 | 三个圆点依次缩放（`dotPulse`，1400ms，stagger 200ms） |
| 发送按钮 | 渐变 `from-amber-500 to-orange-500`，禁用态变灰 |
| 空状态 | 3 张引导卡片（拍食材 → AI 分析 → 获取食谱） |
| 自定义色板 | `chef` 色系：amber 50-900（Tailwind 扩展） |
| 字体 | `"Noto Sans SC"` 优先 → `Inter` → system-ui |

---

## 数据流

### 完整对话链路

```
1. 用户输入文字 + 可选图片
         │
2. 如果有图片 → uploadFile(file) → GET /oss/presign → PUT OSS → accessUrl
         │
3. sendMessage(text, accessUrl)
         │
4. POST /api/v1/chat/stream  { message, image_url, thread_id }
         │
5. FastAPI chat_endpoint → StreamingResponse(search_recipes(...))
         │
6. Agent 层:
   ├── 组装 HumanMessage (text / text+image)
   ├── agent.stream(messages, configurable={thread_id}, stream_mode="messages")
   ├── LangGraph 从 SQLite 恢复历史对话
   ├── ReAct 循环: 思考 → 调用 Tavily 搜索 → 观察结果 → 思考 → 输出
   └── 每个 AIMessageChunk → yield token
         │
7. SSE 流 → 前端 ReadableStream reader → onToken 逐字追加到消息气泡
         │
8. 流结束 → onDone → streaming: false → 光标消失
```

### 会话生命周期

```
创建: thread_id = "session_{timestamp}_{random}" → localStorage
活跃: 每轮对话自动追加到 LangGraph Checkpoint
查询: GET /chat/messages?thread_id=xxx → SQLite 反序列化
清空: DELETE /chat/messages?thread_id=xxx → checkpointer.delete_thread()
恢复: 刷新页面 → localStorage 读取 thread_id → GET /chat/messages 加载历史
```

---

## 安全性

| 措施 | 实现 |
|------|------|
| **CORS** | `allow_origins=["*"]`（开发期），生产环境限制具体域名 |
| **OSS 预签名** | 临时 URL 1 小时过期，AK/SK 仅存服务端环境变量 |
| **输入验证** | Pydantic `BaseModel` 自动校验，`Literal` 约束枚举值 |
| **错误降级** | Agent 异常返回 `"信息检索失败，试试看手动输入食物列表？"` 不暴露堆栈 |
| **会话隔离** | `thread_id` 严格隔离，不同用户无法读取对方对话 |
| **静态文件** | SPA fallback 只匹配非 `/api/*` 路径，避免路由泄漏 |

---

## 路线图

```
✅ Phase 1 — 核心 MVP（已完成）
├── FastAPI + SSE 流式对话
├── LangGraph Agent + ReAct 推理
├── Tavily 搜索工具集成
├── React 前端（完整对话 UI）
├── OSS 图片上传（预签名 URL）
├── LangGraph Checkpoint (SQLite) 会话持久化
└── 前后端一体化部署

🔨 Phase 2 — 智能增强（进行中，预计 2-3 周）
├── 用户系统：每个程序员创建独立 Chef Agent
├── 岗位画像 → 习惯推理（Prompt Engineering 核心）
├── RAG 菜谱库：Milvus 向量化存储 + 检索
├── 菜谱结构化 Schema（Pydantic + Tool 定义）
└── 多模型切换（Qwen / DeepSeek 策略路由）

📋 Phase 3 — 体验升级（规划中，预计 2-3 周）
├── 多 Agent 协作（营养分析 Agent + 烹饪指导 Agent）
├── 用户反馈闭环（👍/👎 → 强化偏好学习）
├── 周食谱批量规划
├── 食材库存管理
└── 移动端适配（PWA）
```

---

## 面试要点（Talking Points）

> 如果面试官问"这个项目你做了什么"，以下是可以展开的方向：

### 架构设计

> **"我设计了一个分层架构，展示层 / 网关层 / Agent 编排层 / 持久化层 / 基础设施层各司其职。替换任何一层不影响其他——比如换模型只需要改 ChatOpenAI 的 base_url，Agent 代码一行不动。前后端同源部署，一个 Python 进程跑全部。"**

### Agent 设计

> **"Agent 的核心是系统提示词设计——我给 Agent 定了 4 步推理流程：食材识别→菜谱检索→多维度打分→结构化输出。通过 '优先调用工具' 的指令防止幻觉。用 LangGraph Checkpoint 做会话记忆，SQLite 持久化，不同用户通过 thread_id 完全隔离。"**

### Tool Calling

> **"用 Pydantic 的 BaseModel + Field + Literal 定义工具参数 Schema，枚举值约束让 LLM 不可能传无效参数，field_validator 自动做输入规范化比如大小写转换。这个 Schema 会自动转换成 OpenAI 的 Function Calling JSON Schema 给到 LLM。"**

### 流式对话

> **"为什么不用 WebSocket？对话场景是单向推送 token，SSE 原生支持自动重连、穿透代理更友好、HTTP/2 多路复用。FastAPI 的 StreamingResponse 让流式返回只需要一个 async generator。"**

### 前后端协作

> **"图片上传不是传统的 multipart/form-data 过一遍后端，而是后端签发 OSS 预签名 URL，前端直传 OSS。大文件不经过 Python 进程，不占内存带宽。Vite build 产物直接输出到 FastAPI 的 static 目录，前后端一体化部署。"**

### React 状态管理

> **"没有引入 Redux 或者 Zustand，因为对话状态的作用域就在当前页面，用自定义 Hook（useChat）就够了。流式接收的关键是用 fetch + ReadableStream 逐块读 SSE，不能用 EventSource 因为它只支持 GET。乐观更新让用户消息立刻显示，AI 消息先占位再逐 token 填充。"**

### 技术深度

> **"Python asyncio 全链路异步：从 FastAPI async endpoint → Agent stream generator → SSE response，没有同步阻塞点。asyncio 的协程比线程轻量得多，一个进程可以处理成百上千的并发 SSE 连接。"**

### 学习能力

> **"这个项目的学习过程我全部记录在 jupyter/ 目录的 12 个 notebook 里——从 Hello World 到 Agentic RAG，每一步都有可执行的代码和笔记。项目完全从零搭建，没有脚手架。"**

---

## 学习笔记

`jupyter/` 目录包含 12 个按学习顺序排列的 notebook，记录了从零掌握 LangChain 生态的全过程。适合作为团队新人的 AI Agent 入门材料。

| # | Notebook | 掌握内容 |
|---|----------|----------|
| 1 | `01_hello_world` | LangChain 基本概念与链式调用 |
| 2 | `02_models` | 对接各种 LLM（OpenAI 兼容接口的威力） |
| 3 | `03_messages` | SystemMessage / HumanMessage / AIMessage 消息类型 |
| 4 | `04_prompt` | Prompt Template 设计与变量注入 |
| 5 | `05_tools` | Tool 定义 + Function Calling 机制 |
| 6 | `tool` | Pydantic Schema 深度：BaseModel、Field、Literal、field_validator |
| 7 | `memory` | LangGraph Checkpoint 记忆管理（SQLite 持久化） |
| 8 | `rag` | RAG 全流程：文档加载→分块→Embedding→Milvus 检索→生成 |
| 9 | `ReAct` | Reasoning + Acting 推理-行动循环模式 |
| 10 | `agentic_rag` | Agent 驱动的智能检索（Agent 自主决策要不要查、查什么） |
| 11 | `project01` | 完整项目实战：从 FastAPI 搭建到 Agent 集成 |
| 12 | `middle_ware` | 请求/响应中间件：拦截、日志、处理 |

另有 [async/learning_async.py](async/learning_async.py) 记录 Python asyncio 协程与并发的学习笔记。

---

<p align="center">
  <b>Built with 🍳 by a programmer, for programmers.</b>
</p>
