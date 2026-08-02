from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv(override=True)

deepseek_llm = ChatOpenAI(
    model = "deepseek-ai/DeepSeek-V4-Flash",
    base_url=os.getenv("GUIJI_BASE_URL"),
    api_key=os.getenv("GUIJI_API_KEY")
)

qwen_llm = ChatOpenAI(
    model='Qwen/Qwen3.6-35B-A3B',
    base_url=os.getenv("GUIJI_BASE_URL"),
    api_key=os.getenv("GUIJI_API_KEY"),
)