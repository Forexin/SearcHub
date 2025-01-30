from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.schemas import SearchRequest, SearchResponse, PluginInfo
from loguru import logger
import time
import subprocess
import os

# 创建一个依赖函数来获取组件实例
def get_plugin_manager():
    from main import plugin_manager
    return plugin_manager

def get_search_coordinator():
    from main import search_coordinator
    return search_coordinator

router = APIRouter(
    prefix="/api",
    tags=["API"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/search", 
    response_model=SearchResponse,
    summary="执行聚合搜索",
    description="根据关键词在所有启用的插件中执行搜索并返回聚合结果"
)
async def search(
    request: SearchRequest,
    search_coordinator = Depends(get_search_coordinator)
):
    """
    执行聚合搜索
    
    - **keyword**: 搜索关键词
    - **timeout**: 可选的超时时间（秒）
    - **platforms**: 可选的平台列表，限制只在指定平台中搜索
    """
    try:
        response = await search_coordinator.search(request)
        return response
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plugins", 
    response_model=List[PluginInfo],
    summary="获取插件列表",
    description="获取所有已安装插件的信息和状态"
)
async def list_plugins(
    plugin_manager = Depends(get_plugin_manager)
):
    """
    获取所有可用插件列表
    """
    try:
        plugins = await plugin_manager.get_active_plugins()
        return plugins
    except Exception as e:
        logger.error(f"Error listing plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plugins/{plugin_name}/start",
    response_model=dict,
    summary="启动插件",
    description="启动指定名称的插件"
)
async def start_plugin(
    plugin_name: str,
    plugin_manager = Depends(get_plugin_manager)
):
    """
    启动指定插件
    
    - **plugin_name**: 插件名称
    """
    try:
        result = await plugin_manager.start_plugin(plugin_name)
        return result
    except Exception as e:
        logger.error(f"Error starting plugin {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plugins/{plugin_name}/stop",
    response_model=dict,
    summary="停止插件",
    description="停止指定名称的插件"
)
async def stop_plugin(
    plugin_name: str,
    plugin_manager = Depends(get_plugin_manager)
):
    """
    停止指定插件
    
    - **plugin_name**: 插件名称
    """
    try:
        result = await plugin_manager.stop_plugin(plugin_name)
        return result
    except Exception as e:
        logger.error(f"Error stopping plugin {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plugins/{plugin_name}/stats",
    response_model=dict,
    summary="获取插件统计信息",
    description="获取指定插件的运行统计信息"
)
async def get_plugin_stats(plugin_name: str):
    """
    获取插件统计信息
    
    - **plugin_name**: 插件名称
    """
    try:
        limiter = plugin_manager.rate_limiter_manager.get_limiter(plugin_name)
        stats = {
            "total_requests": limiter.total_requests,
            "current_rate": limiter.total_requests / ((time.time() - limiter.start_time) / 60),
            "available_tokens": limiter.tokens,
            "last_request": time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(limiter.last_request))
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/system/{action}",
    response_model=dict,
    summary="系统控制",
    description="控制系统的启动、停止和重启"
)
async def control_system(action: str):
    """
    控制系统
    
    - **action**: 操作类型 (start/stop/restart)
    """
    try:
        script_path = "./manage.sh"
        result = subprocess.run([script_path, action], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"系统{action}成功",
                "details": result.stdout
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"操作失败: {result.stderr}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 