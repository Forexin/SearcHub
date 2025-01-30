#!/bin/bash

# 加载环境变量
set -a
source .env
set +a

# 获取虚拟环境路径
VENV_PATH="venv/bin/activate"
PID_FILE="data_aggregator.pid"

check_port() {
    local port=$1
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost $port >/dev/null 2>&1
        return $?
    elif command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
        return $?
    else
        # 如果都没有，尝试使用 Python 检查端口
        python -c "import socket; s=socket.socket(); s.connect(('localhost', $port))" >/dev/null 2>&1
        return $?
    fi
}

cleanup_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process using port $port (PID: $pid)"
        kill -9 $pid
    fi
}

status() {
    echo "=== Data Aggregator 系统状态 ==="
    
    # 检查 PID 文件
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "系统状态: 运行中 (PID: $PID)"
            
            # 检查端口状态
            if check_port 9527; then
                echo "API 端口 (9527): 正常"
            else
                echo "API 端口 (9527): 异常"
            fi
            
            # 检查日志文件
            if [ -f "logs/app.log" ]; then
                echo -e "\n最近的日志:"
                tail -n 5 logs/app.log
            fi
            
            # 检查插件状态
            echo -e "\n已加载的插件:"
            ls -1 plugins/ 2>/dev/null | grep -v "__" || echo "没有找到插件"
            
        else
            echo "系统状态: 已停止 (PID 文件存在但进程不存在)"
            rm -f $PID_FILE
        fi
    else
        echo "系统状态: 已停止"
    fi
}

start() {
    if [ -f "$PID_FILE" ]; then
        echo "系统已经在运行中"
        exit 1
    fi
    
    # 检查虚拟环境
    if [ ! -f "$VENV_PATH" ]; then
        echo "错误: 虚拟环境未找到，请先运行 install.sh"
        exit 1
    fi
    
    # 检查并创建日志目录
    mkdir -p logs
    
    # 检查并清理端口
    if check_port 9527; then
        echo "端口 9527 被占用，正在清理..."
        cleanup_port 9527
        sleep 2
    fi
    
    echo "启动 Data Aggregator..."
    source $VENV_PATH
    
    # 使用 nohup 启动服务并重定向输出
    nohup python main.py > logs/app.log 2>&1 &
    
    # 保存 PID
    echo $! > $PID_FILE
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 5
    
    # 检查服务是否成功启动
    if check_port 9527; then
        echo "系统已启动，PID: $(cat $PID_FILE)"
        echo "访问 http://localhost:9527 打开管理界面"
    else
        echo "错误: 系统启动失败，请检查 logs/app.log"
        rm -f $PID_FILE
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "系统未在运行"
        exit 1
    fi
    
    echo "停止 Data Aggregator..."
    kill $(cat $PID_FILE)
    rm $PID_FILE
    echo "系统已停止"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac 