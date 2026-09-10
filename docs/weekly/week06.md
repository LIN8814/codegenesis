# Week 06 总结

## 学了什么
- JWT：三段式结构、签名验证、过期保护
- OAuth2 密码流：登录 → 签发 token → Bearer 认证
- 密码安全：bcrypt 哈希（绝不存明文）
- User 表 + Alembic 迁移
- 依赖工厂：get_current_user、require_role
- RBAC：401（未认证）vs 403（无权限）
- 所有 /projects 接口加登录鉴权

## 有信心的地方


## 卡在哪里
- bcrypt/passlib 版本不兼容、测试很麻烦、代码自己写还是有难度

## 下周目标
- 异步深入：asyncio.Semaphore 限流、超时控制
- PostgreSQL 进阶 + 10 张核心表设计