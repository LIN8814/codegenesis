def fibonacci(n):
    # 🐛 故意有 bug：base case 不对
    if n == 0:
        return 0
    # 🐛 缺少 n == 1 的处理
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    print(fibonacci(5))  # 用它来练断点调试
