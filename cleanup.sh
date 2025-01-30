#!/bin/bash

echo "清理旧进程..."

# 停止所有相关进程
pkill -f "uvicorn main:app"
pkill -f "python.*plugins/.*/main.py"

# 清理端口
for port in 9527 8081; do
    pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "终止使用端口 $port 的进程"
        kill -9 $pid
    fi
done

# 删除 PID 文件
if [ -f "data_aggregator.pid" ]; then
    rm data_aggregator.pid
fi

# 等待端口释放
sleep 2

echo "清理完成" 