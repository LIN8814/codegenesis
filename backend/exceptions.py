"""统一异常处理 —— 所有错误都返回统一格式"""

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.schemas import APIError
from backend.errors import CodeGenesisError

logger = logging.getLogger("codegenesis")


def register_exception_handlers(app: FastAPI) -> None:
    """给 app 注册所有异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理 HTTPException（404/401/422 等）"""
        logger.warning(f"{request.method} {request.url.path} → {exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content=APIError(
                code="HTTP_ERROR",
                message=str(exc.detail),
                status=exc.status_code,
                timestamp=datetime.now().isoformat(),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """兜底：处理所有未捕获的异常（500）"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=APIError(
                code="INTERNAL_ERROR",
                message="服务器内部错误，请稍后再试",
                status=500,
                timestamp=datetime.now().isoformat(),
            ).model_dump(),
        )

    @app.exception_handler(CodeGenesisError)
    async def codegenesis_exception_handler(request: Request, exc: CodeGenesisError):
        """处理业务异常(LLMAPIError 等)，返回对应错误码"""
        logger.warning(f"{request.method} {request.url.path} → {exc.code}")
        return JSONResponse(
            status_code=exc.status_code,
            content=APIError(
                code=exc.code,
                message=exc.message,
                status=exc.status_code,
                timestamp=datetime.now().isoformat(),
            ).model_dump(),
        )

