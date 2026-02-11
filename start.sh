#!/bin/bash

# phone-mcp 一键启动脚本

cd "$(dirname "$0")"

# 检查是否有虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 启动服务
python -m phone_mcp

