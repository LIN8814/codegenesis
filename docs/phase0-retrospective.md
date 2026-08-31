# Phase 0 复盘（2026.8.3 — 8.30）

## 目标回顾
工具链统一 → Python 过关 → 第一个 API 对接 LLM → 数据库读写

## 完成情况
- ✅ Git/GitHub 全流程、Linux 基础、Docker、VS Code 调试
- ✅ Python 进阶（OOP、异步、数据结构）
- ✅ FastAPI CRUD API + Pydantic 验证 + Swagger 文档
- ✅ 对接 DeepSeek：输入需求 → 生成代码（单项目 + 批量并发）
- ✅ SQLAlchemy + Alembic + Redis 缓存
- ✅ Docker Compose 全家桶一键启动
- ✅ 测试 11 个，覆盖率 72%；black/isort/mypy 通过

## 收获最大的三件事
1. 亲手让 API 调通大模型生成代码——"AI Agent"从概念变成现实
2. 数据持久化 + Docker 化——代码从"能跑"变成"能交付"
3. 学会了调试和排错的方法（看日志、查报错、一步步定位）

## 卡过的地方
- Docker 构建路径问题（COPY backend/ backend/ vs COPY . .）
- SQLite 不支持 ARRAY 类型
- Alembic NOT NULL 列报错
- 端口冲突（手动服务器和容器抢 8000）

## 下一步
进入 Phase 1