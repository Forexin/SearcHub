import os
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

class Feed5Plugin(PluginBase):
    """自动生成的数据源插件 - 界面新闻-只服务于独立思考的人群-Jiemian.com"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.headers.update(self.config.get("settings", {}).get("request", {}).get("headers", {}))
    
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """执行搜索"""
        try:
            results = []
            urls = self.config["settings"]["urls"]
            
            for url in urls:
                try:
                    logger.info(f"从 {{url}} 获取数据")
                    content = await self._make_request(url)
                    if not content:
                        logger.warning(f"从 {{url}} 获取内容为空")
                        continue
                        
                    feed = feedparser.parse(content)
                    if not feed.entries:
                        logger.warning(f"Feed 没有条目: {{url}}")
                        continue
                    
                    logger.info(f"获取到 {{len(feed.entries)}} 条 Feed 条目")
                    for entry in feed.entries:
                        title = entry.get("title", "")
                        description = entry.get("description", "")
                        
                        # 打印调试信息
                        logger.debug(f"检查条目: {{title}}")
                        logger.debug(f"关键词: {{keyword}}")
                        logger.debug(f"标题: {{title}}")
                        logger.debug(f"描述: {{description[:100]}}...")
                        
                        # 扩展搜索范围，包括更多字段
                        searchable_text = " ".join([
                            title,
                            description,
                            entry.get("summary", ""),
                            entry.get("content", [{}])[0].get("value", ""),
                            entry.get("author", ""),
                            entry.get("category", "")
                        ]).lower()
                        
                        # 在所有文本中搜索关键词
                        if keyword.lower() in searchable_text:
                            logger.info(f"找到匹配: {{title}}")
                            
                            # 构建搜索结果
                            result = {
                                "platform": self.name,
                                "content": f"{{title}}\n{{self._clean_html(description)}}",
                                "url": entry.get("link", ""),
                                "metadata": {
                                    "title": title,
                                    "published": entry.get("published", time.strftime("%Y-%m-%d %H:%M:%S")),
                                    "author": entry.get("author", "unknown"),
                                    "source": "界面新闻-只服务于独立思考的人群-Jiemian.com"
                                }
                            }
                            results.append(result)
                            logger.info(f"添加结果: {{result['platform']}} - {{result['metadata']['title']}}")
                    
                except Exception as e:
                    logger.error(f"处理 {{url}} 时出错: {{str(e)}}")
                    continue
            
            logger.info(f"搜索完成，找到 {{len(results)}} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索过程出错: {{str(e)}}")
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
            logger.error(f"Health check failed: {{str(e)}}")
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
            logger.error(f"Error cleaning HTML: {{str(e)}}")
            return html