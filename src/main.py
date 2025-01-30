from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.core.search_coordinator import SearchCoordinator
from src.core.plugin_manager import PluginManager
from src.core.environment_manager import EnvironmentManager
from src.core.result_aggregator import ResultAggregator
from src.models.schemas import SearchRequest, SearchResponse
from loguru import logger
import os

# 配置日志
logger.add("logs/app.log", rotation="500 MB", level="INFO")

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
environment_manager = EnvironmentManager()
plugin_manager = PluginManager()
result_aggregator = ResultAggregator()
search_coordinator = SearchCoordinator(
    plugin_manager=plugin_manager,
    environment_manager=environment_manager,
    result_aggregator=result_aggregator
)

# 确保目录存在
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="frontend/templates")

@app.on_event("startup")
async def startup_event():
    """服务启动时执行"""
    try:
        # 加载插件
        await plugin_manager.discover_plugins()
        logger.info("Plugins loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load plugins: {e}")

@app.get("/")
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """仪表盘页面"""
    return templates.TemplateResponse("pages/dashboard.html", {
        "request": request,
        "plugins": await plugin_manager.get_active_plugins()
    })

@app.get("/plugins")
async def plugins_page(request: Request):
    """插件管理页面"""
    return templates.TemplateResponse("pages/plugins.html", {
        "request": request,
        "plugins": await plugin_manager.get_active_plugins()
    })

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
    uvicorn.run(app, host="0.0.0.0", port=8000) 