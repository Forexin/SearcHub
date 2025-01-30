import os
import yaml
from typing import List, Tuple, Dict, Any
import asyncio
import aiohttp
import feedparser
from urllib.parse import urlparse
import time
from loguru import logger
import sys

class BatchRssGenerator:
    def __init__(self, output_dir: str = None):
        # 如果没有指定输出目录，则使用系统的 plugins 目录
        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.output_dir = os.path.join(project_root, "plugins")  # 直接指向 plugins 目录
        else:
            self.output_dir = output_dir
            
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def generate_from_file(self, file_path: str, prefix: str) -> List[Tuple[str, str]]:
        """从文件生成插件"""
        try:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # 如果是相对路径，则相对于项目根目录
            if not os.path.isabs(file_path):
                # 移除路径中可能的重复 'tools' 目录
                if file_path.startswith('tools/'):
                    file_path = file_path[6:]  # 移除开头的 'tools/'
                file_path = os.path.join(current_dir, file_path)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"URL列表文件不存在: {file_path}")
                
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f.readlines() 
                       if line.strip() and not line.strip().startswith('#')]
            
            logger.info(f"Found {len(urls)} URLs in {file_path}")
            return await self.generate_plugins(urls, prefix)
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    async def generate_plugins(self, urls: List[str], prefix: str) -> List[Tuple[str, str]]:
        """为每个 URL 生成插件"""
        generated = []
        
        for i, url in enumerate(urls, 1):
            try:
                # 生成插件名和路径
                plugin_name = f"{prefix}_{i}"
                plugin_path = os.path.join(self.output_dir, plugin_name)
                
                # 检测 Feed 信息
                feed_info = await self._detect_feed_info(url)
                logger.info(f"Detected feed: {feed_info['title']} ({feed_info['type']})")
                
                # 生成插件文件
                self._generate_plugin_files(plugin_path, plugin_name, url, feed_info)
                
                # 验证生成的插件
                try:
                    # 修改 sys.path 以便能找到插件
                    if plugin_path not in sys.path:
                        sys.path.insert(0, plugin_path)
                    
                    # 动态导入插件模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("main", os.path.join(plugin_path, "main.py"))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 获取插件类名
                    class_name = "".join(word.capitalize() for word in plugin_name.split("_")) + "Plugin"
                    
                    # 获取插件类
                    if hasattr(module, class_name):
                        plugin_class = getattr(module, class_name)
                        # 读取配置
                        with open(os.path.join(plugin_path, "plugin.yaml")) as f:
                            config = yaml.safe_load(f)
                        # 创建实例并测试
                        plugin = plugin_class(config["name"], config)
                        is_healthy = await plugin.health_check()
                        if not is_healthy:
                            logger.warning(f"Plugin {plugin_name} health check failed")
                    else:
                        raise AttributeError(f"Plugin class {class_name} not found in module")
                        
                finally:
                    # 清理 sys.path
                    if plugin_path in sys.path:
                        sys.path.remove(plugin_path)
                
                generated.append((plugin_name, plugin_path))
                logger.info(f"Generated plugin: {plugin_name}")
                
            except Exception as e:
                logger.error(f"Error generating plugin for {url}: {str(e)}")
                continue
        
        return generated
    
    async def _detect_feed_info(self, url: str) -> dict:
        """检测 Feed 类型和信息"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    content = await response.text()
                    
                    # 尝试解析为 RSS
                    feed = feedparser.parse(content)
                    
                    # 检查是否为有效的 RSS Feed
                    if hasattr(feed, 'feed') and hasattr(feed.feed, 'title'):
                        return {
                            "title": feed.feed.get("title", "Unknown Feed"),
                            "description": feed.feed.get("description", "RSS Feed"),
                            "type": "rss"
                        }
                    
                    # 如果不是 RSS，尝试解析为 JSON API
                    try:
                        import json
                        json_data = json.loads(content)
                        return {
                            "title": f"API Feed ({urlparse(url).netloc})",
                            "description": "JSON API Endpoint",
                            "type": "api"
                        }
                    except json.JSONDecodeError:
                        # 如果既不是 RSS 也不是 JSON，返回通用信息
                        domain = urlparse(url).netloc
                        return {
                            "title": f"Data Source ({domain})",
                            "description": "Generic Data Endpoint",
                            "type": "unknown"
                        }
                        
        except Exception as e:
            logger.warning(f"Error detecting feed type for {url}: {str(e)}")
            # 发生错误时返回基本信息
            domain = urlparse(url).netloc
            return {
                "title": f"Feed ({domain})",
                "description": "Data Feed",
                "type": "unknown"
            }
    
    def _generate_plugin_files(self, plugin_path: str, plugin_name: str, url: str, feed_info: dict):
        """生成插件相关文件"""
        # 获取已存在的端口号
        existing_ports = set()
        plugins_dir = os.path.dirname(plugin_path)  # 修改为直接使用 plugin_path 的父目录
        if os.path.exists(plugins_dir):
            for plugin_folder in os.listdir(plugins_dir):
                config_path = os.path.join(plugins_dir, plugin_folder, "plugin.yaml")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            plugin_config = yaml.safe_load(f)
                            if 'communication' in plugin_config:
                                existing_ports.add(plugin_config['communication']['port'])
                    except:
                        continue

        # 找到一个可用的端口号
        port = 8081
        while port in existing_ports:
            port += 1

        # 生成配置
        config = {
            "name": plugin_name,
            "version": "1.0.0",
            "language": "python",
            "type": "crawler",
            "status": "running",
            "description": f"自动生成的 RSS 插件 - {feed_info['title']}",
            
            "environment": {
                "runtime": "python3.8",
                "dependencies": [
                    "aiohttp==3.8.1",
                    "feedparser==6.0.10",
                    "beautifulsoup4==4.9.3"
                ]
            },
            
            "communication": {
                "protocol": "http",
                "port": port
            },
            
            "settings": {
                "urls": [url],
                "request": {
                    "timeout": 10,
                    "max_retries": 3,
                    "retry_delay": 2,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                }
            }
        }
        
        # 创建插件目录并写入配置
        os.makedirs(plugin_path, exist_ok=True)
        with open(os.path.join(plugin_path, "plugin.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        
        # 生成其他文件
        self._generate_main_py(plugin_path, plugin_name, feed_info)
        self._generate_test_py(plugin_path)
    
    def _generate_main_py(self, plugin_path: str, plugin_name: str, feed_info: dict):
        """生成插件主文件"""
        class_name = "".join(word.capitalize() for word in plugin_name.split("_")) + "Plugin"
        
        # 使用 {{ 和 }} 来转义大括号
        template = '''import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from typing import Dict, Any, List
from src.core.plugin_base import PluginBase
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from loguru import logger
import time

class {class_name}(PluginBase):
    """自动生成的数据源插件 - {feed_title}"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.headers.update(self.config.get("settings", {{}}).get("request", {{}}).get("headers", {{}}))
    
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """执行搜索"""
        try:
            results = []
            urls = self.config["settings"]["urls"]
            
            for url in urls:
                try:
                    logger.info(f"从 {{{{url}}}} 获取数据")
                    content = await self._make_request(url)
                    if not content:
                        logger.warning(f"从 {{{{url}}}} 获取内容为空")
                        continue
                        
                    feed = feedparser.parse(content)
                    if not feed.entries:
                        logger.warning(f"Feed 没有条目: {{{{url}}}}")
                        continue
                    
                    logger.info(f"获取到 {{{{len(feed.entries)}}}} 条 Feed 条目")
                    for entry in feed.entries:
                        title = entry.get("title", "")
                        description = entry.get("description", "")
                        
                        # 打印调试信息
                        logger.debug(f"检查条目: {{{{title}}}}")
                        logger.debug(f"关键词: {{{{keyword}}}}")
                        logger.debug(f"标题: {{{{title}}}}")
                        logger.debug(f"描述: {{{{description[:100]}}}}...")
                        
                        # 扩展搜索范围，包括更多字段
                        searchable_text = " ".join([
                            title,
                            description,
                            entry.get("summary", ""),
                            entry.get("content", [{{}}])[0].get("value", ""),
                            entry.get("author", ""),
                            entry.get("category", "")
                        ]).lower()
                        
                        # 在所有文本中搜索关键词
                        if keyword.lower() in searchable_text:
                            logger.info(f"找到匹配: {{{{title}}}}")
                            
                            # 构建搜索结果
                            result = {{
                                "platform": self.name,
                                "content": f"{{{{title}}}}\\n{{{{self._clean_html(description)}}}}",
                                "url": entry.get("link", ""),
                                "metadata": {{
                                    "title": title,
                                    "published": entry.get("published", time.strftime("%Y-%m-%d %H:%M:%S")),
                                    "author": entry.get("author", "unknown"),
                                    "source": "{feed_title}"
                                }}
                            }}
                            results.append(result)
                            logger.info(f"添加结果: {{{{result['platform']}}}} - {{{{result['metadata']['title']}}}}")
                    
                except Exception as e:
                    logger.error(f"处理 {{{{url}}}} 时出错: {{{{str(e)}}}}")
                    continue
            
            logger.info(f"搜索完成，找到 {{{{len(results)}}}} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索过程出错: {{{{str(e)}}}}")
            return []
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            url = self.config["settings"]["urls"][0]
            content = await self._make_request(url)
            if not content:
                return False
            feed = feedparser.parse(content)
            return len(feed.entries) > 0
        except Exception as e:
            logger.error(f"Health check failed: {{{{str(e)}}}}")
            return False
    
    def _clean_html(self, html: str) -> str:
        """清理 HTML 标签"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(strip=True)
            return " ".join(text.split())
        except Exception as e:
            logger.error(f"Error cleaning HTML: {{{{str(e)}}}}")
            return html'''

        # 使用 format 替换变量
        template = template.format(
            class_name=class_name,
            feed_title=feed_info['title']
        )

        with open(os.path.join(plugin_path, "main.py"), "w", encoding="utf-8") as f:
            f.write(template)
    
    def _generate_test_py(self, plugin_path: str):
        """生成测试文件"""
        template = '''
import asyncio
import os
import yaml
from main import *  # 导入插件类

async def test_plugin():
    try:
        # 读取配置文件
        with open("plugin.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 创建插件实例
        plugin_class = [cls for cls in globals().values() 
                       if isinstance(cls, type) and cls.__name__.endswith("Plugin")][0]
        plugin = plugin_class(config["name"], config)
        
        # 测试健康检查
        print("\\n=== 测试健康检查 ===")
        is_healthy = await plugin.health_check()
        print(f"健康状态: {'正常' if is_healthy else '异常'}")
        
        # 测试搜索功能
        print("\\n=== 测试搜索功能 ===")
        keywords = ["测试", "news", "市场"]
        
        for keyword in keywords:
            print(f"\\n搜索关键词: {keyword}")
            results = await plugin.search(keyword)
            
            if results:
                print(f"找到 {len(results)} 条结果:")
                for i, result in enumerate(results, 1):
                    print(f"\\n--- 结果 {i} ---")
                    print(f"平台: {result['platform']}")
                    print(f"内容: {result['content'][:100]}...")
                    print(f"链接: {result['url']}")
                    if 'metadata' in result:
                        metadata = result['metadata']
                        print(f"标题: {metadata.get('title', 'N/A')}")
                        print(f"时间: {metadata.get('published', 'N/A')}")
                        print(f"作者: {metadata.get('author', 'N/A')}")
                        print(f"来源: {metadata.get('source', 'N/A')}")
            else:
                print("未找到相关结果")
                
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 确保在插件目录中运行测试
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(test_plugin())
'''
        
        with open(os.path.join(plugin_path, "test.py"), "w", encoding="utf-8") as f:
            f.write(template.lstrip())

    def _generate_plugin_yaml(self, plugin_path: str, plugin_name: str, url: str, feed_info: dict):
        """生成插件配置文件"""
        config = {
            "name": plugin_name,
            "version": "1.0.0",
            "language": "python",
            "type": "crawler",
            "status": "running",  # 确保插件状态为 running
            "description": f"自动生成的 RSS 插件 - {feed_info['title']}",
            
            "environment": {
                "runtime": "python3.8",
                "dependencies": [
                    "aiohttp==3.8.1",
                    "feedparser==6.0.10",
                    "beautifulsoup4==4.9.3"
                ]
            },
            
            "settings": {
                "urls": [url],
                "request": {
                    "timeout": 10,
                    "max_retries": 3,
                    "retry_delay": 2,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                }
            }
        }
        
        os.makedirs(plugin_path, exist_ok=True)
        with open(os.path.join(plugin_path, "plugin.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

async def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="批量生成 RSS/API 插件")
    parser.add_argument("file", help="包含 URL 列表的文本文件路径")
    parser.add_argument("--prefix", default="feed", help="插件名称前缀")
    parser.add_argument("--output-dir", help="插件输出目录路径")
    args = parser.parse_args()
    
    try:
        generator = BatchRssGenerator(args.output_dir)
        generated = await generator.generate_from_file(args.file, args.prefix)
        
        print(f"\n成功生成 {len(generated)} 个插件:")
        for name, path in generated:
            print(f"- {name}: {path}")
            
        print("\n重要提示：")
        print("1. 插件已生成到系统的 plugins 目录")
        print("2. 请运行 ./cleanup.sh 清理旧进程")
        print("3. 然后运行 ./manage.sh start 重启系统")
        print("4. 使用 ./manage.sh status 检查系统状态")
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    # 设置日志
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/generator.log", rotation="500 MB", level="INFO")
    
    # 运行主函数
    exit_code = asyncio.run(main())
    exit(exit_code) 