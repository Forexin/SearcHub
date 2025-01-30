# Data Aggregator 工具集

本目录包含了一系列用于辅助系统运行和管理的工具。

## 批量 RSS 插件生成器 (batch_rss_generator.py)

### 功能特点

- 支持批量处理多个 RSS/API 源
- 自动检测数据源类型
- 自动配置端口和环境
- 生成完整的插件结构
- 包含测试文件

### 使用方法

1. 准备 URL 列表文件：
```txt
# example.txt
https://rsshub.rssforever.com/mrm
https://rsshub.rssforever.com/cls/telegraph
https://rsshub.rssforever.com/gelonghui/live
https://rsshub.rssforever.com/jin10
```

2. 运行生成器：
```bash
python batch_rss_generator.py example.txt --prefix feed
```

3. 生成的插件结构：
```
plugins/
  ├── feed_1/
  │   ├── plugin.yaml
  │   ├── main.py
  │   └── test.py
  ├── feed_2/
  │   └── ...
```

### 参数说明

- `file`: URL 列表文件路径（必需）
- `--prefix`: 插件名称前缀（默认：feed）
- `--output-dir`: 输出目录（默认：../plugins）

### 配置说明

生成的 plugin.yaml 示例：
```yaml
name: feed_1
version: 1.0.0
language: python
type: crawler
status: running
description: "自动生成的 RSS 插件"
environment:
  runtime: python3.8
  dependencies:
    - aiohttp==3.8.1
    - feedparser==6.0.10
settings:
  urls: 
    - https://example.com/feed
```

### 测试生成的插件

每个插件都包含测试文件：
```bash
cd plugins/feed_1
python test.py
```

## 插件模板生成器 (plugin_generator.py)

用于生成自定义插件的工具。

### 使用方法

```bash
python plugin_generator.py \
    --name custom_plugin \
    --type crawler \
    --template rss
```

### 可用模板

- rss：RSS 数据源插件
- api：API 数据源插件
- processor：数据处理插件

## 系统维护工具

### cleanup.sh

清理系统进程和端口：
```bash
./cleanup.sh
```

功能：
- 停止所有插件进程
- 清理占用的端口
- 删除临时文件

### check_frontend.sh

检查和修复前端文件：
```bash
./check_frontend.sh
```

功能：
- 验证前端文件完整性
- 创建必要的目录
- 复制静态资源

## 开发工具

### test_jin10.py

金十数据插件的测试工具：
```bash
python test_jin10.py
```

功能：
- 测试数据获取
- 验证数据格式
- 检查搜索功能

## 注意事项

1. 端口管理
   - 默认从 8081 开始分配
   - 确保端口未被占用
   - 可在 config.yaml 中配置

2. 依赖管理
   - 使用虚拟环境
   - 保持版本一致
   - 定期更新依赖

3. 日志管理
   - 日志位置：logs/
   - 定期清理旧日志
   - 设置合适的日志级别

## 故障排除

1. 生成器问题：
   - 检查 URL 可访问性
   - 验证文件格式
   - 查看生成器日志

2. 插件问题：
   - 检查配置文件
   - 运行测试脚本
   - 查看插件日志

## 最佳实践

1. URL 管理
   - 按类型分组
   - 添加注释说明
   - 定期验证有效性

2. 插件命名
   - 使用有意义的前缀
   - 避免特殊字符
   - 保持命名一致性

3. 测试策略
   - 先测试单个 URL
   - 再批量生成
   - 保存测试结果 