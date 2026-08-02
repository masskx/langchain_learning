# Personal Chief（私厨助手）

基于 **LangChain + LangGraph + FastAPI** 的 AI Agent 学习项目。通过构建一个"私厨助手"应用，实践 LLM 应用开发的核心概念：Agent、工具调用、RAG、流式对话、记忆管理等。

## 项目概览

拍一张食材照片 → AI 识别食材 → 调用搜索引擎查找菜谱 → 多维度打分排序 → 输出结构化建议报告

```
用户上传食材图片 → Agent(识别+搜索+评估+推荐) → 流式返回菜谱建议
```

## 技术栈

| 层级 | 技术 |
|------|------|
| **AI 框架** | LangChain、LangGraph |
| **模型** | 通义千问 (Qwen) via 阿里百炼 / SiliconFlow |
| **搜索工具** | Tavily Search API |
| **Web 框架** | FastAPI + Uvicorn |
| **向量数据库** | Milvus (Docker) |
| **状态持久化** | SQLite (LangGraph Checkpoint) |
| **对象存储** | 阿里云 OSS |
| **包管理** | uv |
| **异步** | Python asyncio |

## 项目结构

```
langchain/
├── app/                          # FastAPI 应用（主项目）
│   ├── main.py                   # 应用入口，路由挂载，CORS 配置
│   ├── api/v1/
│   │   ├── chat.py               # 对话接口（流式 SSE、历史消息、清空会话）
│   │   └── oss.py                # OSS 预签名上传 URL 接口
│   ├── agents/
│   │   └── personal_chief.py     # 私厨 Agent：提示词、工具、记忆、流式对话
│   ├── models/
│   │   └── schemas.py            # Pydantic 数据模型
│   └── common/
│       └── logger.py             # 日志配置
├── jupyter/                      # 学习笔记（按学习顺序排列）
│   ├── 01_hello_world.ipynb      # LangChain 入门
│   ├── 02_models.ipynb           # 模型调用
│   ├── 03_messages.ipynb         # 消息类型
│   ├── 04_prompt.ipynb           # 提示词工程
│   ├── 05_tools.ipynb            # 工具调用
│   ├── memory.ipynb              # 记忆管理
│   ├── rag.ipynb                 # RAG 检索增强生成
│   ├── ReAct.ipynb               # ReAct 推理模式
│   ├── agentic_rag.ipynb         # Agentic RAG
│   ├── project01.ipynb           # 项目实战 1
│   └── middle_ware.ipynb         # 中间件
├── async/
│   └── learning_async.py         # Python asyncio 学习笔记
├── resources/
│   └── checkpoint.db             # LangGraph 对话状态持久化
├── docker-compose.yml            # Milvus 向量数据库 + etcd + MinIO
├── pyproject.toml                # 项目配置与依赖
└── .env                          # 环境变量（API Key 等）
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖（使用 uv）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

复制 `.env` 文件并填入你的 API Key：

| 变量 | 说明 |
|------|------|
| `TAVILY_API_KEY` | Tavily 搜索 API Key |
| `BAILIAN_BASE_URL` | 百炼模型 API 地址 |
| `BAILIAN_API_KEY` | 百炼模型 API Key |
| `OSS_ACCESS_KEY_ID` | 阿里云 OSS AccessKey |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 OSS SecretKey |
| `OSS_BUCKET` | OSS Bucket 名称 |

### 3. 启动向量数据库（可选）

```bash
docker-compose up -d
```

### 4. 启动 API 服务

```bash
python -m app.main
# 访问 http://127.0.0.1:8001
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/chat/stream` | 流式对话（SSE） |
| `GET` | `/api/v1/chat/messages?thread_id=xxx` | 获取历史消息 |
| `DELETE` | `/api/v1/chat/messages?thread_id=xxx` | 清空会话 |
| `GET` | `/api/v1/oss/presign?filename=xxx.jpg` | 获取 OSS 上传预签名 URL |

### 对话请求示例

```json
{
  "message": "这些食材能做什么菜？",
  "image_url": "https://oss-bucket.oss-cn-beijing.aliyuncs.com/photo.jpg",
  "thread_id": "user_session_001"
}
```

## 学习路径

这个项目记录了从零开始学习 LangChain 生态的过程：

1. **Hello World** → 了解 LangChain 基本概念
2. **模型调用** → 对接各种 LLM（OpenAI 兼容接口）
3. **消息系统** → SystemMessage / HumanMessage / AIMessage
4. **提示词工程** → Prompt Template 设计与优化
5. **工具调用** → Tool / Function Calling
6. **记忆管理** → LangGraph Checkpoint（SQLite 持久化）
7. **RAG** → 检索增强生成，向量数据库（Milvus）
8. **ReAct** → 推理-行动循环模式
9. **Agentic RAG** → Agent 驱动的智能检索
10. **项目实战** → 构建完整的 FastAPI 应用
11. **异步编程** → Python asyncio 协程与并发
12. **中间件** → 请求/响应拦截与处理

## 关键设计决策

- **流式返回 (SSE)**：Agent 使用 `stream_mode="messages"` 逐 token 返回，提升用户体验
- **会话隔离**：通过 `thread_id` 区分不同用户/会话，支持历史查询和清空
- **多模型兼容**：使用 OpenAI 兼容接口，可灵活切换模型提供商（百炼、SiliconFlow 等）
- **记忆持久化**：LangGraph Checkpoint 存入 SQLite，服务重启不丢失对话状态
