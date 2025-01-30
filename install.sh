#!/bin/bash

echo "开始安装 Data Aggregator..."

# 检查 Python 版本
python3 -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)" || {
    echo "错误: 需要 Python 3.8 或更高版本"
    exit 1
}

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
# 先安装核心依赖
pip install fastapi uvicorn

# 然后安装其他依赖
pip install -r requirements.txt

# 创建必要的目录
echo "创建目录结构..."
mkdir -p logs
mkdir -p .environments
mkdir -p frontend/static/{css,js,img}
mkdir -p frontend/templates/{components,pages}

# 复制配置文件
echo "初始化配置..."
if [ ! -f config/config.yaml ]; then
    cp config/config.yaml.example config/config.yaml
fi

if [ ! -f .env ]; then
    cp .env.example .env
fi

# 检查前端文件
echo "检查前端文件..."
chmod +x check_frontend.sh
./check_frontend.sh

# 设置权限
chmod +x manage.sh

echo "安装完成！"
echo "使用以下命令启动系统："
echo "./manage.sh start" 