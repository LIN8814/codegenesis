"""CodeGenesis 自定义异常体系
用法：业务代码 raise LLMAPIError("deepseek 超时")
      → 全局处理器捕获 → 返回统一格式
"""

from typing import Optional


class CodeGenesisError(Exception):
    """所有业务异常的基础类"""

    code = "BUSINESS_ERROR"  # 机器可读错误码
    status_code = 400  # HTTP 状态码

    def __init__(self, message: str, agent_name: Optional[str] = None):
        self.message = message
        self.agent_name = agent_name
        super().__init__(f"[{agent_name or 'System'}] {message}")


class LLMAPIError(CodeGenesisError):
    """LLM API 调用失败（超时/限流/服务不可用）"""

    code = "LLM_API_ERROR"
    status_code = 502  # Bad Gateway（上游 DeepSeek 挂了）


class AgentExecutionError(CodeGenesisError):
    """Agent 执行过程中出错"""

    code = "AGENT_EXECUTION_ERROR"
    status_code = 500


class ProjectNotFoundError(CodeGenesisError):
    """项目不存在"""

    code = "PROJECT_NOT_FOUND"
    status_code = 404
