"""LLM 客户端 —— 封装 DeepSeek API 调用"""

import os
from dataclasses import dataclass
from backend.config import settings
import httpx


@dataclass
class LLMMessage:
    """一条对话消息"""

    role: str  # "system"（系统设定）| "user"（用户）| "assistant"（AI回复）
    content: str  # 消息内容


@dataclass
class LLMResponse:
    """LLM 返回的结果"""

    content: str  # AI 生成的内容
    model: str  # 使用的模型名
    tokens_used: int  # 消耗的 token 数



class LLMClient:
    """DeepSeek API 客户端"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ):
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = base_url or settings.deepseek_base_url
        self.model = model or settings.deepseek_model

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """发送对话请求到 LLM,返回回复"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": m.role, "content": m.content} for m in messages
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()  # 状态码不是 2xx 会抛异常
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                tokens_used=data["usage"]["total_tokens"],
            )
