"""JWT 签发与验证"""

import jwt
import datetime

# 服务器密钥（真实项目放 .env，绝不写代码里）
SECRET_KEY = "codegenesis-dev-secret-key-2026-keep-private"

def create_token(user_id: str, role: str) -> str:
    """签发 JWT"""
    payload = {
        "sub": user_id,                    # 用户标识
        "role": role,                      # 角色
        "iat": datetime.datetime.now(datetime.timezone.utc),  # 签发时间
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=2),     # 2小时后过期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """验证 JWT，返回 payload（失败抛异常）"""
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


if __name__ == "__main__":
    # 1. 签发
    token = create_token("user-001", "owner")
    print("签发的 JWT:")
    print(token)
    print()

    # 2. 拆开看三段
    header, payload, signature = token.split(".")
    print(f"三段分别是: {header[:20]}... / {payload[:20]}... / {signature[:20]}...")
    print()

    # 3. 验证（正常）
    data = verify_token(token)
    print(f"验证通过 ✅ 你是谁: {data['sub']}, 角色: {data['role']}")

    # 4. 验证（篡改测试：改了 payload 一个字符）
    tampered = token[:-5] + "xxxxx"
    try:
        verify_token(tampered)
        print("篡改后竟然通过了 ❌")
    except jwt.InvalidSignatureError:
        print("篡改后验证失败 ✅ 签名保护生效！")

    # 5. 过期测试
    import time
    expired_payload = {
        "sub": "user-001",
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")
    try:
        verify_token(expired_token)
        print("过期 token 竟然通过了 ❌")
    except jwt.ExpiredSignatureError:
        print("过期 token 被拒绝 ✅ 过期保护生效！")