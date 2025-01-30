# SearchHub

一个基于 FastAPI 的分布式搜索聚合系统，支持多数据源的实时搜索、聚合和管理。

## 特性

- 🔌 插件化架构：轻松扩展新的数据源
- 🚀 实时搜索：毫秒级响应
- 🛠 内置工具：RSS 插件生成器
- 🎯 精准聚合：智能结果排序
- 🎨 Web 界面：可视化管理
- 🔄 自动管理：环境依赖自动处理
- 📊 监控系统：实时性能监控
- �� 限流保护：内置限流机制

## 系统要求

- Python 3.8+
- 操作系统：Linux/macOS/Windows
- 内存：至少 2GB RAM
- 磁盘空间：至少 1GB 可用空间

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/SearchHub.git
cd SearchHub

# 安装依赖
chmod +x install.sh
./install.sh
```

### 启动

```bash
./manage.sh start
```

访问 http://localhost:9527 打开管理界面

### 使用示例

```bash
# 搜索接口调用
curl -X POST "http://localhost:9527/api/search" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "搜索关键词"}'
```

## 使用指南

### 1. 生成 RSS 插件

使用内置的批量生成工具：

```bash
cd tools
python batch_rss_generator.py example.txt --prefix feed
```

这将为 example.txt 中的每个 URL 生成一个插件。

### 2. 管理插件

通过 Web 界面：
- 访问 http://localhost:9527/plugins
- 可以启动/停止/删除插件
- 查看插件状态和日志

通过命令行：
```bash
# 查看插件状态
./manage.sh status

# 重启所有插件
./manage.sh restart
```

### 3. 搜索数据

REST API:
```bash
curl -X POST "http://localhost:9527/api/search" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "关键词"}'
```

Web 界面：
- 访问 http://localhost:9527
- 使用搜索框直接搜索

### 4. 系统维护

```bash
# 查看系统状态
./manage.sh status

# 查看日志
tail -f logs/app.log

# 清理系统
./cleanup.sh

# 重启系统
./manage.sh restart
```

## 配置说明

### 系统配置 (config/config.yaml)
```yaml
system:
  timeout: 30
  max_concurrent_crawlers: 10
  
plugins:
  timeout_per_plugin: 10
  retry_count: 3
```

### 环境变量 (.env)
```env
API_PORT=9527
LOG_LEVEL=INFO
ENABLE_CACHE=true
```

## 插件开发

1. 创建插件目录结构：
```
plugins/
  └── your_plugin/
      ├── plugin.yaml    # 插件配置
      ├── main.py        # 主代码
      └── test.py        # 测试文件
```

2. 实现必要的接口：
```python
class YourPlugin(PluginBase):
    async def search(self, keyword: str) -> List[Dict]:
        # 实现搜索逻辑
        pass

    async def health_check(self) -> bool:
        # 实现健康检查
        return True
```

## 故障排除

1. 插件无法加载：
   - 检查 plugin.yaml 配置
   - 查看 logs/app.log
   - 确保依赖已安装

2. 搜索无结果：
   - 检查插件状态
   - 验证关键词
   - 查看插件日志

3. 系统无响应：
   - 运行 ./cleanup.sh
   - 检查端口占用
   - 查看系统日志

## API 文档

启动系统后访问：
- Swagger UI: http://localhost:9527/docs
- ReDoc: http://localhost:9527/redoc

## 贡献指南

1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

[MIT License](LICENSE)

## 作者

[您的名字] - [您的邮箱]

## 更新日志

### [1.0.0] - 2024-01-01
- 初始发布
- 支持多种数据源插件
- 添加Web管理界面
- 添加插件生成工具

## 文档

详细文档请访问 [Wiki](https://github.com/YOUR_USERNAME/SearchHub/wiki)
