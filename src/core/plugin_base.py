from abc import ABC, abstractmethod
from typing import Dict, Any, List
import aiohttp
from loguru import logger

class PluginBase(ABC):
    """插件基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    @abstractmethod
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """执行搜索"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    async def _make_request(self, url: str, **kwargs) -> str:
        """发送 HTTP 请求"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, **kwargs) as response:
                return await response.text() 