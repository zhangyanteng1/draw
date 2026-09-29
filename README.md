# Pulse

基于 **FastAPI + SQLAlchemy + Redis** 的抽奖活动后端服务，提供抽奖活动管理、奖品配置、用户抽奖次数控制等完整能力，支持定时任务驱动活动上线/下线与库存对账。

## ✨ 功能特性

- **抽奖活动管理**：创建 / 更新 / 上线 / 下线抽奖活动，支持活动生命周期管理
- **奖品配置**：奖品维护，活动-奖品关联与库存管理
- **抽奖逻辑**：用户参与抽奖，奖品发放与库存扣减，未中奖兜底
- **用户与次数**：用户体系、抽奖次数控制、参与记录与登录日志
- **需求管理**：业务需求条目维护
- **定时任务**：基于 APScheduler 的活动自动上线 / 下线 / 库存对账
- **认证授权**：JWT 鉴权中间件、管理员权限校验
- **可观测性**：分层日志 + 全链路 trace_id 追踪（详见下文）
- **统一规范**：统一响应体、全局异常处理、CORS 配置

## 🔍 全链路日志跟踪

项目内置基于 `trace_id` 的全链路日志追踪能力，一次请求贯穿所有日志可串联排查。

**trace_id 流转**

```
请求进入
  → RequestLogMiddleware: 生成 trace_id (优先取请求头 x-request-id, 否则 uuid), 写入 ContextVar
    → service 层日志: 经 TraceIdFilter 自动注入同一 trace_id
    → 响应回写 x-request-id 头
```

- **trace_id 生成与传递**：在请求中间件入口生成 `trace_id`，写入 `contextvars.ContextVar`，协程间隔离、子任务自动继承，service 层无需感知。
- **自动注入**：`TraceIdFilter` 挂载到各 handler，把当前 `trace_id` 注入每条日志的 `%(trace_id)s` 字段，无需业务代码手动传参。
- **闭环排查**：响应头回写 `x-request-id`，前端报错时带上该 ID，后端凭此直接检索日志，快速定位链路。
- **分层日志隔离**：按职责拆分独立日志文件，互不干扰，均带 `trace_id`：

| 日志文件 | 记录内容 | 来源 |
| --- | --- | --- |
| `logs/request.log` | 每个接口请求：URL、method、请求头/体、响应体、状态码、耗时 | `RequestLogMiddleware` |
| `logs/service.log` | 业务层日志（`service.*` 子 logger） | service 层 |
| `logs/script.log` | 脚本与定时任务日志（`script.*` / `job.*`） | script / job |

- **日志格式**：`时间 [级别] trace_id=xxx 模块 - 内容`，单行紧凑，便于检索。
- **健壮性**：按大小滚动（10MB/份，保留 5 份，UTF-8）；大 body 截断（2000 字符）；流式响应（SSE / 文件下载）原样放行不读 body，避免破坏分片输出与内存撑爆。

## 🛠 技术栈

| 分类 | 技术 |
| --- | --- |
| Web 框架 | FastAPI + Uvicorn + Starlette |
| ORM & 数据库 | SQLAlchemy 2.0 + PyMySQL (MySQL) |
| 缓存 | Redis |
| 数据校验 | Pydantic 2.x |
| 定时任务 | APScheduler |
| 认证 | PyJWT |
| 密码哈希 | argon2-cffi |
| 配置管理 | PyYAML + python-dotenv |
| 部署 | Docker |

## 📁 项目结构

```
pulse/
├── main.py              # 应用入口, 路由注册 / 中间件 / CORS
├── route/               # 路由层 (接口定义)
├── service/             # 业务逻辑层
├── dao/                 # 数据访问层 (数据库操作)
├── model/               # 数据库模型 (ORM 实体)
├── schema/              # 数据校验模型 (Pydantic 入参/出参)
├── db/                  # 数据库会话与引擎
├── cache/               # Redis 缓存封装
├── const/               # 常量与缓存 key 定义
├── job/                 # 定时任务 (活动上线/下线/对账)
├── middlewares/         # 中间件 (鉴权 / 请求日志)
├── exceptions/          # 统一异常处理
├── common/              # 公共组件 (响应体 / 状态码)
├── tool/                # 工具类 (JWT / Redis / 日期 / 日志配置等)
├── script/              # 脚本入口
├── config/              # 配置文件 (config-prod.yaml 等, 不入库)
├── logs/                # 运行时日志 (不入库)
├── requirements.txt
├── Dockerfile.web       # Web 服务镜像
└── .env                 # 环境变量 (不入库)
```

## 📦 分层架构

请求流向遵循清晰的分层调用链：

```
HTTP 请求
  → 中间件 (请求日志 → 全局鉴权)
    → route (路由层, 参数校验)
      → service (业务逻辑层)
        → dao (数据访问层)
          → model / cache (数据库 / Redis)
        ← 返回
      ← 业务结果
    → schema (响应结构)
  → 统一响应体 Response
← HTTP 响应
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.x
- Redis 5+

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量与连接信息
#    .env          数据库 / Redis / JWT 密钥等
#    config/config-prod.yaml   运行配置
cp .env.example .env   # 按模板填写
# 按需修改 config 中的数据库与 Redis 连接

# 3. 启动服务 (开发模式, 默认 8080 端口, 热重载)
python main.py
```

启动后访问接口文档：`http://localhost:8080/docs`（FastAPI 自动生成的 Swagger UI）。

### Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.web -t pulse-web:latest .

# 运行 (挂载配置与日志, 避免敏感信息打入镜像)
docker run -d \
  --name pulse-web \
  -p 8080:8080 \
  -v ./config:/app/config \
  -v ./.env:/app/.env \
  -v ./logs:/app/logs \
  pulse-web:latest
```

## 🔌 接口预览

所有接口统一前缀 `/pulse`，主要模块：

| 模块 | 路由前缀 | 说明 |
| --- | --- | --- |
| 探活 | `/ping` | 服务健康检查 |
| 用户 | `/user` | 用户体系、登录 |
| 需求 | `/requirement` | 需求条目管理 |
| 抽奖活动 | `/draw` | 活动 CRUD、上线/下线、参与抽奖 |
| 奖品 | `/prize` | 奖品配置 |
| 活动-奖品 | `/draw_prize` | 活动关联奖品与库存 |
| 抽奖次数 | `/user_draw` | 用户抽奖次数控制 |

## 📝 配置说明

敏感配置通过环境变量 / 挂载文件注入，**不纳入版本控制**（见 `.gitignore`）：

- `.env`：数据库连接、Redis 连接、JWT 密钥、CORS 白名单等
- `config/config-*.yaml`：各环境运行配置，运行时通过 volume 挂载

## 📄 License

本项目仅供学习与内部使用。
