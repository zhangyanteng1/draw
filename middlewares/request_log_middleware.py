import json
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from tool.logging_config import trace_id_var

logger = logging.getLogger("request")

# 单条 body 截断长度, 避免大 body 撑爆日志
_MAX_BODY_LOG = 2000


def _compact_body(raw: bytes) -> str:
    """把 body 压成单行: JSON 紧凑序列化, 非 JSON 折叠空白。避免多行/缩进撑断日志行。"""
    if not raw:
        return ""
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        text = " ".join(text.split())
    return text[:_MAX_BODY_LOG]


class RequestLogMiddleware(BaseHTTPMiddleware):
    """记录每个接口请求: url、method、请求头、请求体、响应体、状态码、耗时。"""

    # 流式响应(SSE/大文件下载)特征: media_type 或 content-type 含这些值时, 不能读 body
    _STREAM_MEDIA_TYPES = ("text/event-stream", "application/octet-stream")
    _STREAM_MEDIA_HINTS = ("stream", "event-stream")

    @classmethod
    def _is_streaming(cls, media_type: str, content_type: str) -> bool:
        """判断是否流式响应: 流式响应不可全量读 body, 否则破坏分片输出/撑爆内存。"""
        mt = (media_type or "").lower()
        ct = (content_type or "").lower()
        if mt in cls._STREAM_MEDIA_TYPES:
            return True
        return any(hint in mt or hint in ct for hint in cls._STREAM_MEDIA_HINTS)

    async def dispatch(self, request: Request, call_next):
        # 探活接口不记, 减噪
        if request.url.path.endswith("/ping"):
            return await call_next(request)

        trace_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        # 写入请求上下文: 下游 service 层日志经 TraceIdFilter 自动带上同一 trace_id, 串联链路
        trace_id_var.set(trace_id)

        req_content_type = request.headers.get("content-type", "")
        req_streaming = self._is_streaming("", req_content_type)
        # 请求体: Starlette 的 body() 会缓存, 端点仍能正常读取; 文件上传/流式请求跳过
        if req_content_type.startswith("multipart/form-data") or req_streaming:
            req_body_str = "<skipped>"
        else:
            req_body = await request.body()
            req_body_str = _compact_body(req_body)

        start = time.time()
        response = await call_next(request)
        cost = (time.time() - start) * 1000

        # 防御性判断: 流式响应(SSE/大文件下载)不能全量读 body, 否则破坏分片输出、撑爆内存。
        # 此类响应原样放行(仅回写 x-request-id 头), 不记录响应体。
        resp_content_type = response.headers.get("content-type", "")
        if self._is_streaming(response.media_type, resp_content_type):
            logger.info(
                "%s %s -> %s cost=%.0fms (streaming, body not logged) req=%s",
                request.method,
                str(request.url.path),
                response.status_code,
                cost,
                req_body_str,
            )
            response.headers["x-request-id"] = trace_id
            return response

        # 响应体是流式, 消费后需重建一个 Response 返回, 否则客户端拿不到 body
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        resp_body = b"".join(chunks)
        resp_body_str = _compact_body(resp_body)
        # 写回 x-request-id: 前端报错时可带上, 后端凭此 ID 直查日志, 闭环排查
        resp_headers = dict(response.headers)
        resp_headers["x-request-id"] = trace_id
        new_response = Response(
            resp_body,
            status_code=response.status_code,
            headers=resp_headers,
            media_type=response.media_type,
        )

        logger.info(
            "%s %s -> %s cost=%.0fms headers=%s req=%s resp=%s",
            request.method,
            str(request.url.path),
            response.status_code,
            cost,
            dict(request.headers),
            req_body_str,
            resp_body_str,
        )
        return new_response
