"""Agent 服务 —— 组织提示词，调用 LLM 生成代码"""

from backend.services.llm import LLMClient, LLMMessage


class LLMCodeGenAgent:
    """接入真实 LLM 的代码生成 Agent"""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "CodeGenAgent"

    async def generate_code(self, task: str, tech_stack: list[str]) -> str:
        """根据需求生成代码，返回代码字符串"""
        system_prompt = (
            "你是一个资深 Python 后端工程师。"
            "用户会描述一个需求，你需要生成完整的 FastAPI 代码。"
            "代码要能直接运行，包含必要的 import 和错误处理。"
            "只输出 Python 代码，不要解释。"
        )
        user_prompt = f"需求：{task}\n技术栈：{', '.join(tech_stack)}"

        response = await self.llm.chat(
            [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt),
            ]
        )

        return response.content
