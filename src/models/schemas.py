from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    keyword: str
    platforms: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "keyword": "python",
                "platforms": ["github", "stackoverflow"]
            }
        }

class SearchResult(BaseModel):
    platform: str
    content: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}

    class Config:
        schema_extra = {
            "example": {
                "platform": "github",
                "content": "示例搜索结果",
                "url": "https://github.com/example/repo",
                "metadata": {"score": 0.95}
            }
        }

class SearchResponse(BaseModel):
    keyword: str
    results: List[SearchResult]
    error: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "keyword": "python",
                "results": [
                    {
                        "platform": "github",
                        "content": "示例搜索结果",
                        "url": "https://github.com/example/repo",
                        "metadata": {"score": 0.95}
                    }
                ],
                "error": None
            }
        }

class PluginInfo(BaseModel):
    name: str = Field(..., description="插件名称")
    version: str = Field(..., description="插件版本")
    language: str = Field(..., description="插件使用的编程语言")
    type: str = Field(..., description="插件类型")
    status: str = Field(..., description="插件状态")
    environment: Dict[str, Any] = Field(..., description="插件环境配置")
    communication: Dict[str, Any] = Field(..., description="插件通信配置")

    class Config:
        schema_extra = {
            "example": {
                "name": "example_plugin",
                "version": "1.0.0",
                "language": "python",
                "type": "crawler",
                "status": "running",
                "environment": {
                    "runtime": "python3.8",
                    "dependencies": ["requests", "beautifulsoup4"]
                },
                "communication": {
                    "protocol": "websocket",
                    "port": 8080
                }
            }
        } 