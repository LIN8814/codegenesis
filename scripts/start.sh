#!/bin/bash
# CodeGenesis 开发环境一键启动脚本
# 用法：bash scripts/start.sh

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CodeGenesis 开发环境启动 ===${NC}"

# 1. 自动定位项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"   # 脚本所在目录 = scripts/
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"        # 上级目录 = 项目根目录
cd "$PROJECT_DIR" || exit 1
echo -e "${GREEN}[1/4] 项目目录: ${NC}$PROJECT_DIR"

# 2. 激活虚拟环境
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/Scripts/activate"
    echo -e "${GREEN}[2/4] 虚拟环境已激活 ✓${NC}"
else
    echo -e "${RED}未找到虚拟环境，请先运行: python -m venv venv${NC}"
    exit 1
fi

# 3. 检查依赖
echo -e "${GREEN}[3/4] 检查依赖...${NC}"
python -c "import fastapi, uvicorn, httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}依赖未安装，正在安装...${NC}"
    pip install -r backend/requirements.txt
else
    echo -e "${GREEN}依赖已就绪 ✓${NC}"
fi

# 4. 启动服务器（backend 作为包从根目录启动）
echo -e "${GREEN}[4/4] 启动服务器...${NC}"
echo -e "${YELLOW}提示：按 Ctrl+C 停止服务器${NC}"
exec uvicorn backend.main:app --reload