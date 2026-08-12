#!/bin/bash
# ========================================
# CodeGenesis 环境初始化脚本
# Usage: bash scripts/setup.sh
# ========================================

# 颜色输出（Git Bash 支持的颜色代码）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # 恢复默认颜色

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CodeGenesis 环境初始化脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 打印系统信息
echo -e "${YELLOW}[1/4] 系统信息${NC}"
echo "  操作系统: $(uname -s)"
echo "  架构: $(uname -m)"
echo "  当前时间: $(date)"
echo ""

# 2. 创建项目目录结构
echo -e "${YELLOW}[2/4] 创建项目目录结构${NC}"
mkdir -p backend/services
mkdir -p backend/agents
mkdir -p backend/tests
mkdir -p frontend
mkdir -p docs/weekly
mkdir -p scripts
mkdir -p logs
echo -e "  ${GREEN}✓ 目录结构已创建${NC}"
echo ""

# 3. 检查 Python 是否安装
echo -e "${YELLOW}[3/4] 检查 Python 环境${NC}"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "  ${GREEN}✓ Python 已安装: $PYTHON_VERSION${NC}"
else
    echo -e "  ${RED}✗ 未找到 Python，请先安装 Python 3.12+${NC}"
    exit 1
fi

# 检查 pip
if command -v pip &> /dev/null; then
    PIP_VERSION=$(pip --version 2>&1 | awk '{print $2}')
    echo -e "  ${GREEN}✓ pip 已安装: $PIP_VERSION${NC}"
else
    echo -e "  ${RED}✗ 未找到 pip${NC}"
    exit 1
fi
echo ""

# 4. 检查 Git 是否安装
echo -e "${YELLOW}[4/4] 检查 Git 环境${NC}"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version 2>&1)
    echo -e "  ${GREEN}✓ Git 已安装: $GIT_VERSION${NC}"
else
    echo -e "  ${RED}✗ 未找到 Git${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  环境检查完成！可以开始开发了。${NC}"
echo -e "${GREEN}========================================${NC}"


:<<!
========================================
  CodeGenesis 环境初始化脚本
========================================

[1/4] 系统信息
  操作系统: MINGW64_NT-10.0-26200
  架构: x86_64
  当前时间: 2026年08月 7日 17:22:34

[2/4] 创建项目目录结构
  ✓ 目录结构已创建

[3/4] 检查 Python 环境
  ✓ Python 已安装: Python 3.11.9
  ✓ pip 已安装: 24.0

[4/4] 检查 Git 环境
  ✓ Git 已安装: git version 2.54.0.windows.1

========================================
  环境检查完成！可以开始开发了。
========================================
!