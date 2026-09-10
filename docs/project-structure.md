# CodeGenesis 项目结构说明

> 更新日期：2026-09-10（v0.2.0，认证体系完成）

## 一个请求的流动方向（最好记的角度）

```
请求进来
  ↓
① backend/main.py           入口：组装 app、中间件（日志/CORS）、异常处理、注册路由
  ↓
② backend/routers/          路由层：按业务分的接口文件
   ├─ projects.py           项目接口（CRUD + AI 生成 + 批量生成）
   ├─ auth.py               认证接口（注册 / 登录 / me / 用户列表）
   └─ stats.py              统计接口（/stats）
  ↓
③ backend/core/             核心安全与依赖
   ├─ deps.py               依赖项：get_current_user（认人）、require_role（查权限）
   └─ security.py           底层安全：JWT 签发/验证、密码哈希/比对
  ↓
④ backend/schemas.py        数据关卡：Pydantic 验证请求格式
  ↓
⑤ backend/services/         业务服务层（真正干活的外部能力）
   ├─ llm.py                调 DeepSeek 的客户端
   ├─ agent_service.py      代码生成 Agent（组织 prompt）
   └─ cache.py              Redis 缓存（同需求不重复调 AI）
  ↓
⑥ backend/models.py + database.py    数据层
   ├─ models.py             ORM 模型：Project / AgentLog / User（= 数据库三张表）
   └─ database.py           数据库连接（engine + get_db 依赖）
  ↓
出错时
⑦ backend/errors.py         自定义异常定义（PROJECT_NOT_FOUND / INVALID_TOKEN...）
   backend/exceptions.py    全局异常处理器（统一成 JSON 格式返回）
```

**分层意义**：改接口去 routers、改表去 models、改 AI 逻辑去 services——互不干扰（高内聚低耦合）。

## 根目录文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目介绍（GitHub 首页） |
| `.env` | 敏感配置：DeepSeek API Key 等（**不进 Git**） |
| `.env.example` | `.env` 模板（进 Git） |
| `alembic.ini` | Alembic 数据库迁移工具的配置 |
| `docker-compose.yml` | 编排三个容器：后端 + PostgreSQL + Redis |
| `codegenesis.db` | SQLite 数据库文件（本地开发数据，**不进 Git**） |

## 配套文件

| 文件 | 说明 |
|------|------|
| `backend/config.py` | 配置管理（读 .env：API Key、数据库地址、Redis 地址） |
| `backend/Dockerfile` | 构建后端镜像的说明书 |
| `backend/requirements.txt` | 依赖清单（pip freeze 生成） |
| `backend/tests/` | 测试（test_api.py 接口测试、test_schemas.py 验证器测试） |
| `backend/exercises/` | 学习练习（async_demo / jwt_demo / redis_demo / debug_practice），不属于项目本体 |

## 其他目录

| 目录/文件 | 说明 |
|-----------|------|
| `alembic/env.py`、`alembic/versions/*.py` | 迁移配置 + 版本文件（初始表 → 加 tags → 加 users） |
| `docs/weekly/` | 周报 |
| `docs/phase0-retrospective.md` | Phase 0 复盘 |
| `scripts/start.sh` | 一键启动（激活 venv + 检查依赖 + 起服务器） |
| `scripts/setup.sh` | 环境检查脚本 |

## 记忆口诀

> main（总装）→ routers（接客）→ core（安检）→ schemas（验证）→ services（干活）→ models/database（存取）→ errors（兜底）
