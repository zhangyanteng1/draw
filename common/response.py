from typing import Any

from starlette.responses import JSONResponse

from common.status import Status
from tool.logging_config import trace_id_var


class Response:

    @classmethod
    def _build_response(cls,
                        code: int = None,
                        success: bool = None,
                        message: str = None,
                        data: Any = None) -> dict[str, Any]:
        res = dict()
        res['code'] = code
        res['success'] = success
        res['message'] = message
        res['data'] = data
        # 透传当前请求/任务的 trace_id, 供前端报错时带上, 后端凭此 ID 直查日志, 闭环排查
        res['trace_id'] = trace_id_var.get()
        return res

    @classmethod
    def success(cls,
                code: int = Status.OK,
                success: bool = True,
                message: str = None,
                data: Any = None) -> dict[str, Any]:
        return cls._build_response(code, success, message, data)

    @classmethod
    def error(cls,
              code: int = Status.ERROR,
              success: bool = False,
              message: str = None,
              data: Any = None) -> dict[str, Any]:
        return cls._build_response(code, success, message, data)

    @classmethod
    def json_response(cls,
                      code: int = None,
                      success: bool = False,
                      message: str = None,
                      data: Any = None) -> JSONResponse:
        """构造 JSONResponse(供中间件/异常处理器直接返回, 复用统一信封)"""
        return JSONResponse(content=cls._build_response(code, success, message, data))
