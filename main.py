import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from exceptions.exception_handler import register_exception_handlers
from middlewares.auth_middleware import auth_middleware
from middlewares.request_log_middleware import RequestLogMiddleware
from route.draw_prize_route import draw_prize_router
from route.draw_route import draw_router
from route.ping_route import ping
from route.prize_route import prize_router
from route.requirement_route import requirement_router
from route.user_draw_route import user_draw_router
from route.user_route import user_router
from tool.logging_config import setup_request_logging, setup_service_logging

API_PREFIX = "/pulse"

load_dotenv()

# 配置请求日志(request logger -> logs/request.log)
setup_request_logging()
# 配置 service 层日志(service logger -> logs/service.log)
setup_service_logging()

app = FastAPI()

register_exception_handlers(app)

# 服务探活
app.include_router(ping, prefix=API_PREFIX)

# 用户
app.include_router(user_router, prefix=API_PREFIX)

# 需求
app.include_router(requirement_router, prefix=API_PREFIX)

# 抽奖活动
app.include_router(draw_router, prefix=API_PREFIX)

# 奖品
app.include_router(prize_router, prefix=API_PREFIX)

# 关联抽奖奖品
app.include_router(draw_prize_router, prefix=API_PREFIX)

# 抽奖次数
app.include_router(user_draw_router, prefix=API_PREFIX)


# 指定静态文件
# app.mount("/upload", StaticFiles(directory="upload"))


# 全局鉴权中间件
app.middleware("http")(auth_middleware)

# 配置 CORS 中间件
# 注意: allow_credentials=True 时, allow_origins 不能用 "*" (浏览器会拒绝该组合)。
# 白名单从环境变量 CORS_ALLOW_ORIGINS 读取(逗号分隔), 缺省放开本机常见调试源。
_cors_origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,  # 生产环境通过环境变量指定具体域名
    allow_credentials=True,  # 允许发送凭据（如 cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# 请求日志中间件(最后注册 = 最外层, 覆盖所有请求, 含被鉴权拒绝的)
app.add_middleware(RequestLogMiddleware)


if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, reload=True)
