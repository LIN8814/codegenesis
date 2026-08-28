#!/bin/bash
# CodeGenesis 开发环境一键启动脚本
# 用法：bash scripts/start.sh

# 颜色定义（Day 4 学过）
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CodeGenesis 开发环境启动 ===${NC}"

# 1. 自动定位项目根目录（不管你在哪运行，都能找到项目）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"   # 脚本所在目录 = scripts/
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"        # 上级目录 = 项目根目录
cd "$PROJECT_DIR" || exit 1
echo -e "${GREEN}[1/3] 项目目录: ${NC}$PROJECT_DIR"

# 2. 检查依赖是否安装（装了就不重复装）
cd backend || exit 1
echo -e "${GREEN}[2/3] 检查依赖...${NC}"
python -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}依赖未安装，正在安装...${NC}"
    pip install -r requirements.txt
else
    echo -e "${GREEN}依赖已就绪 ✓${NC}"
fi

# 3. 启动服务器
echo -e "${GREEN}[3/3] 启动服务器...${NC}"
echo -e "${YELLOW}提示：按 Ctrl+C 停止服务器${NC}"
exec uvicorn main:app --reload
