import asyncio
import os
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from loguru import logger
from src.core.plugin_manager import PluginManager
from src.core.environment_manager import EnvironmentManager
from src.core.result_aggregator import ResultAggregator
from src.core.search_coordinator import SearchCoordinator
from src.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import yaml
import shutil
from src.models.schemas import SearchRequest, SearchResponse

app = FastAPI(
    title="Data Aggregator",
    description="一个基于 FastAPI 的可扩展数据聚合系统",
    version="1.0.0",
    # 禁用默认的文档路由，使用我们的自定义路由
    docs_url=None,
    redoc_url=None,
    openapi_tags=[{
        "name": "API",
        "description": "系统核心 API 接口",
        "externalDocs": {
            "description": "了解更多",
            "url": "https://github.com/yourusername/data-aggregator",
        },
    }]
)

# 配置日志
logger.add("logs/app.log", rotation="500 MB", level="INFO")

# 修改静态文件和模板配置
static_path = os.path.join(os.path.dirname(__file__), "frontend", "static")
templates_path = os.path.join(os.path.dirname(__file__), "frontend", "templates")

# 确保目录存在
os.makedirs(static_path, exist_ok=True)
os.makedirs(templates_path, exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 初始化模板引擎
templates = Jinja2Templates(directory=templates_path)

# 初始化核心组件
environment_manager = EnvironmentManager()

# 修改 plugin_manager 的初始化
plugin_manager = PluginManager()

result_aggregator = ResultAggregator()
search_coordinator = SearchCoordinator(
    plugin_manager=plugin_manager,
    environment_manager=environment_manager,
    result_aggregator=result_aggregator
)

# 注册路由
app.include_router(router)

# 在应用初始化后添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由处理函数
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """重定向到仪表盘页面"""
    try:
        return await dashboard(request)
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": "500",
                "error_message": str(e)
            }
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        # 获取所有插件
        plugins = await plugin_manager.get_active_plugins()
        active_plugins_count = len([p for p in plugins if p.status == "running"])
        
        # 获取系统运行时间
        uptime = "0天0小时0分钟"  # 这里可以添加实际的运行时间计算
        
        # 获取总请求数
        total_requests = 0
        
        # 获取插件状态列表
        plugins_status = []
        for plugin in plugins:
            try:
                stats = await plugin_manager.get_plugin_stats(plugin.name)
                plugins_status.append(stats)
                total_requests += stats["total_requests"]
            except Exception as e:
                logger.error(f"Error getting stats for plugin {plugin.name}: {str(e)}")
                plugins_status.append({
                    "name": plugin.name,
                    "status": "error",
                    "requests": 0,
                    "last_request": "未知"
                })
        
        return templates.TemplateResponse(
            "pages/dashboard.html",
            {
                "request": request,
                "active_plugins_count": active_plugins_count,
                "uptime": uptime,
                "total_requests": total_requests,
                "plugins_status": plugins_status
            }
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": "500",
                "error_message": str(e)
            }
        )

@app.get("/plugins", response_class=HTMLResponse)
async def plugins(request: Request):
    try:
        # 获取所有插件
        plugins = await plugin_manager.get_active_plugins()
        return templates.TemplateResponse(
            "pages/plugins.html",
            {
                "request": request,
                "plugins": plugins
            }
        )
    except Exception as e:
        logger.error(f"Error rendering plugins page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": "500",
                "error_message": str(e)
            }
        )

@app.get("/config", response_class=HTMLResponse)
async def config(request: Request):
    try:
        # 读取配置文件
        with open("config/config.yaml", "r") as f:
            system_config = f.read()
        
        # 读取环境变量
        with open(".env", "r") as f:
            env_config = f.read()
            
        return templates.TemplateResponse(
            "pages/config.html",
            {
                "request": request,
                "system_config": system_config,
                "env_config": env_config
            }
        )
    except Exception as e:
        logger.error(f"Error rendering config page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": "500",
                "error_message": str(e)
            }
        )

@app.get("/tools", response_class=HTMLResponse)
async def tools(request: Request):
    try:
        return templates.TemplateResponse(
            "pages/tools.html",
            {
                "request": request,
                "tools": []  # 这里可以添加实际的工具列表
            }
        )
    except Exception as e:
        logger.error(f"Error rendering tools page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": "500",
                "error_message": str(e)
            }
        )

# 添加自定义 Swagger UI 路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>Data Aggregator - API 文档</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        
        *,
        *:before,
        *:after {
            box-sizing: inherit;
        }

        body {
            margin: 0;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                docExpansion: 'list',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                showExtensions: true,
                showCommonExtensions: true
            });
        };
    </script>
</body>
</html>
        """
    )

@app.on_event("startup")
async def startup_event():
    """服务启动时执行"""
    logger.info("系统启动中...")
    await plugin_manager.discover_plugins()
    logger.info("插件加载完成")

@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时的清理
    """
    try:
        # 停止所有插件
        plugins = await plugin_manager.get_active_plugins()
        for plugin in plugins:
            try:
                await plugin_manager.stop_plugin(plugin.name)
            except Exception as e:
                logger.error(f"Failed to stop plugin {plugin.name}: {str(e)}")
                
        # 清理环境
        # TODO: 实现环境清理逻辑
        
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

@app.post("/api/plugins")
async def create_plugin(plugin_data: Dict):
    """创建新插件"""
    try:
        plugin_name = plugin_data['name']
        plugin_type = plugin_data['type']
        plugin_config = plugin_data['config']
        plugin_code = plugin_data['code']
        
        # 创建插件目录
        plugin_dir = os.path.join('plugins', plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)
        
        # 保存配置文件
        config_path = os.path.join(plugin_dir, 'plugin.yaml')
        with open(config_path, 'w') as f:
            f.write(plugin_config)
            
        # 保存源代码
        code_path = os.path.join(plugin_dir, 'main.py')
        with open(code_path, 'w') as f:
            f.write(plugin_code)
            
        # 重新加载插件
        await plugin_manager.discover_plugins()
        
        return {"status": "success", "message": f"Plugin {plugin_name} created successfully"}
    except Exception as e:
        logger.error(f"Error creating plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/plugins/{plugin_name}")
async def delete_plugin(plugin_name: str):
    """删除插件"""
    try:
        # 如果插件正在运行，先停止它
        try:
            await plugin_manager.stop_plugin(plugin_name)
        except:
            pass
        
        # 删除插件目录
        plugin_dir = os.path.join('plugins', plugin_name)
        if os.path.exists(plugin_dir):
            shutil.rmtree(plugin_dir)
            
        # 从插件管理器中移除插件
        if plugin_name in plugin_manager.plugins:
            del plugin_manager.plugins[plugin_name]
            
        return {"status": "success", "message": f"Plugin {plugin_name} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting plugin {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search(request: SearchRequest) -> SearchResponse:
    """执行搜索"""
    try:
        return await search_coordinator.search(request)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plugins")
async def get_plugins():
    """获取插件列表"""
    try:
        plugins = await plugin_manager.get_active_plugins()
        return {"plugins": plugins}
    except Exception as e:
        logger.error(f"Error getting plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9527)  # 修改 host 为 "0.0.0.0" 