from typing import List
import asyncio
from loguru import logger
from ..models.schemas import SearchRequest, SearchResult, SearchResponse

class SearchCoordinator:
    def __init__(self, plugin_manager, environment_manager, result_aggregator):
        self.plugin_manager = plugin_manager
        self.environment_manager = environment_manager
        self.result_aggregator = result_aggregator
        
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        协调多个插件执行搜索
        """
        try:
            results = []
            errors = []
            
            # 获取活动的插件
            plugins = await self.plugin_manager.get_active_plugins()
            logger.info(f"找到 {len(plugins)} 个插件")
            
            # 过滤出运行中的插件
            active_plugins = [p for p in plugins if p.status == "running"]
            logger.info(f"其中 {len(active_plugins)} 个插件处于运行状态")
            
            for plugin_info in active_plugins:
                plugin_name = plugin_info.name
                logger.info(f"使用插件 {plugin_name} 搜索关键词: {request.keyword}")
                
                try:
                    plugin_results = await self.plugin_manager.search(plugin_name, request.keyword)
                    if plugin_results:
                        results.extend(plugin_results)
                        logger.info(f"插件 {plugin_name} 返回 {len(plugin_results)} 条结果")
                    else:
                        logger.info(f"插件 {plugin_name} 没有找到结果")
                    
                except Exception as e:
                    error_msg = f"插件 {plugin_name} 搜索失败: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            logger.info(f"搜索完成，共找到 {len(results)} 条结果")
            return SearchResponse(
                keyword=request.keyword,
                results=results,
                error="; ".join(errors) if errors else None
            )
        except Exception as e:
            logger.error(f"搜索过程出错: {str(e)}")
            return SearchResponse(
                keyword=request.keyword,
                results=[],
                error=str(e)
            )
        
    async def _search_with_plugin(self, plugin_name: str, keyword: str) -> List[dict]:
        """
        使用指定插件执行搜索
        """
        try:
            # 直接使用插件实例进行搜索
            return await self.plugin_manager.search(plugin_name, keyword)
            
        except Exception as e:
            logger.error(f"Error in plugin {plugin_name}: {str(e)}")
            raise 