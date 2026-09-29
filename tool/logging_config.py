import contextvars
import logging
import os
from logging.handlers import RotatingFileHandler

# 项目根目录(本文件位于 <root>/tool/), 锚定日志目录, 避免受 cwd 影响(PyCharm/命令行/celery 等工作目录不一致)
_LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep + "logs"

# 请求链路追踪ID上下文: 每次请求在中间件入口 set, 协程间隔离, 子任务(call_next)自动继承。
# service 层无需感知 trace_id, 由 TraceIdFilter 在日志输出时自动注入。
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


class TraceIdFilter(logging.Filter):
    """把 trace_id_var 当前值注入每条日志记录, 供 formatter 的 %(trace_id)s 使用。

    必须挂载到 handler(而非 logger): service.user_service 等子 logger 日志通过 propagate
    上浮到 service logger 处理, 此间只经过祖先 handler 的 filter, 不经过祖先 logger 的 filter。
    """

    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True


_REQUEST_LOG_FILE = os.path.join(_LOG_DIR, "request.log")
_REQUEST_FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] trace_id=%(trace_id)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_SCRIPT_LOG_FILE = os.path.join(_LOG_DIR, "script.log")
_SCRIPT_FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] trace_id=%(trace_id)s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_SERVICE_LOG_FILE = os.path.join(_LOG_DIR, "service.log")
_SERVICE_FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] trace_id=%(trace_id)s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_root_logging():
    """配置 root logger 的默认输出(INFO 级别, 统一格式)。

    幂等: root logger 已有 handler 时不重复配置, 避免 import 时多次调用叠加。
    业务模块只需 `logging.getLogger(__name__)`, 由入口统一调用本函数完成配置。
    """
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_request_logging():
    """配置 request logger 输出到单独文件 logs/request.log(按大小轮转, utf-8)。

    与业务日志隔离: propagate=False, 仅写 request.log。
    idempotent: 重复调用不会叠加 handler。
    """
    os.makedirs(_LOG_DIR, exist_ok=True)
    req_logger = logging.getLogger("request")
    req_logger.setLevel(logging.INFO)
    req_logger.propagate = False
    if req_logger.handlers:
        return
    handler = RotatingFileHandler(
        _REQUEST_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(_REQUEST_FORMATTER)
    handler.addFilter(TraceIdFilter())
    req_logger.addHandler(handler)


def setup_script_logging():
    """配置脚本运行日志输出到单独文件 logs/script.log(按大小轮转, utf-8)。

    挂载到 root logger: 捕获 script.* 与 job.* 等所有上浮日志, 与 setup_root_logging 的 stdout 并存。
    与 request 日志隔离: request logger 已 propagate=False, 不会写进 script.log。
    幂等: 重复调用不会叠加 handler。
    """
    os.makedirs(_LOG_DIR, exist_ok=True)
    root = logging.getLogger()
    if any(
        isinstance(h, logging.FileHandler)
        and os.path.basename(getattr(h, "baseFilename", "")) == "script.log"
        for h in root.handlers
    ):
        return
    handler = RotatingFileHandler(
        _SCRIPT_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(_SCRIPT_FORMATTER)
    handler.addFilter(TraceIdFilter())
    root.addHandler(handler)


def setup_service_logging():
    """配置 service 层日志输出到单独文件 logs/service.log(按大小轮转, utf-8)。

    利用 logging 层级命名: service 模块均用 getLogger(__name__), 名为 service.xxx,
    均为 service 父 logger 的子 logger, 日志上浮至此。propagate=False 使其不再上浮 root,
    仅写 service.log, 与 stdout/script.log 隔离。幂等: 重复调用不叠加 handler。
    """
    os.makedirs(_LOG_DIR, exist_ok=True)
    svc_logger = logging.getLogger("service")
    svc_logger.setLevel(logging.INFO)
    svc_logger.propagate = False
    if svc_logger.handlers:
        return
    handler = RotatingFileHandler(
        _SERVICE_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(_SERVICE_FORMATTER)
    handler.addFilter(TraceIdFilter())
    svc_logger.addHandler(handler)
