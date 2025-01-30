import os
import importlib.util
import yaml
import sys
from typing import Dict, List, Any
from loguru import logger
from ..models.schemas import PluginInfo

class PluginManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not PluginManager._initialized:
            self.plugins: Dict[str, PluginInfo] = {}
            self.plugin_instances: Dict[str, Any] = {}
            PluginManager._initialized = True
        
    async def discover_plugins(self, plugin_dir: str = "plugins") -> None:
        """扫描并加载插件"""
        logger.info(f"开始扫描插件目录: {plugin_dir}")
        
        loaded_plugins = set()  # 记录本次加载的插件
        
        for item in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, item)
            logger.info(f"检查目录: {plugin_path}")
            
            if os.path.isdir(plugin_path) and not item.startswith('__'):
                config_path = os.path.join(plugin_path, "plugin.yaml")
                if os.path.exists(config_path):
                    try:
                        # 加载配置
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        
                        # 确保插件状态为 running
                        config['status'] = 'running'
                        logger.info(f"加载插件配置: {config}")
                        
                        # 动态导入插件模块
                        module_name = f"plugins.{item}.main"
                        spec = importlib.util.spec_from_file_location(
                            module_name,
                            os.path.join(plugin_path, "main.py")
                        )
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module  # 使用完整的模块路径
                        spec.loader.exec_module(module)
                        
                        # 获取插件类
                        plugin_class_name = "".join(
                            word.capitalize() for word in config['name'].split('_')
                        ) + "Plugin"
                        logger.info(f"查找插件类: {plugin_class_name}")
                        
                        if hasattr(module, plugin_class_name):
                            plugin_class = getattr(module, plugin_class_name)
                            plugin_instance = plugin_class(config['name'], config)
                            
                            # 保存插件信息和实例
                            plugin_info = PluginInfo(
                                name=config['name'],
                                version=config['version'],
                                language=config['language'],
                                type=config['type'],
                                status='running',  # 强制设置状态为 running
                                environment=config.get('environment', {}),
                                communication=config.get('communication', {})
                            )
                            
                            self.plugins[config['name']] = plugin_info
                            self.plugin_instances[config['name']] = plugin_instance
                            loaded_plugins.add(config['name'])
                            
                            # 保存更新后的配置
                            with open(config_path, 'w', encoding='utf-8') as f:
                                yaml.safe_dump(config, f, allow_unicode=True)
                            
                            logger.info(f"成功加载插件: {config['name']} (状态: running)")
                        else:
                            logger.error(f"未找到插件类 {plugin_class_name}")
                            
                    except Exception as e:
                        logger.error(f"加载插件 {item} 失败: {str(e)}")
                        continue
        
        # 移除不再存在的插件
        for plugin_name in list(self.plugins.keys()):
            if plugin_name not in loaded_plugins:
                logger.info(f"移除不存在的插件: {plugin_name}")
                self.plugins.pop(plugin_name)
                self.plugin_instances.pop(plugin_name, None)

        logger.info(f"已加载 {len(self.plugins)} 个插件: {list(self.plugins.keys())}")
        logger.info(f"插件实例: {list(self.plugin_instances.keys())}")
        
    async def search(self, plugin_name: str, keyword: str) -> List[Dict[str, Any]]:
        """使用指定插件执行搜索"""
        if plugin_name not in self.plugin_instances:
            logger.error(f"插件未找到: {plugin_name}")
            return []
        
        try:
            logger.info(f"使用插件 {plugin_name} 搜索关键词: {keyword}")
            plugin = self.plugin_instances[plugin_name]
            results = await plugin.search(keyword)
            
            # 确保每个结果都包含必需的字段
            validated_results = []
            for result in results:
                if isinstance(result, dict) and 'platform' in result and 'content' in result:
                    validated_results.append({
                        'platform': result['platform'],
                        'content': result['content'],
                        'url': result.get('url'),
                        'metadata': result.get('metadata', {})
                    })
                    logger.info(f"找到有效结果: {result['platform']}")
                else:
                    logger.warning(f"插件 {plugin_name} 返回无效结果格式: {result}")
            
            logger.info(f"插件 {plugin_name} 返回 {len(validated_results)} 条有效结果")
            return validated_results
            
        except Exception as e:
            logger.error(f"插件 {plugin_name} 搜索出错: {str(e)}")
            return []
        
    async def get_active_plugins(self) -> List[PluginInfo]:
        """获取所有已加载的插件"""
        logger.info(f"当前已加载插件: {list(self.plugins.keys())}")
        logger.info(f"插件状态: {[(name, info.status) for name, info in self.plugins.items()]}")
        
        # 返回所有插件，不过滤状态
        active_plugins = list(self.plugins.values())
        logger.info(f"返回 {len(active_plugins)} 个插件")
        return active_plugins

    async def start_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """启动插件"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin {plugin_name} not found")
                
            plugin = self.plugins[plugin_name]
            plugin.status = "running"
            
            # 如果插件实例存在，执行健康检查
            if plugin_name in self.plugin_instances:
                plugin_instance = self.plugin_instances[plugin_name]
                is_healthy = await plugin_instance.health_check()
                if not is_healthy:
                    raise Exception("Plugin health check failed")
            
            logger.info(f"Started plugin: {plugin_name}")
            return {"status": "success", "message": f"Plugin {plugin_name} started successfully"}
            
        except Exception as e:
            logger.error(f"Failed to start plugin {plugin_name}: {str(e)}")
            raise
            
    async def stop_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """停止插件"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin {plugin_name} not found")
                
            plugin = self.plugins[plugin_name]
            plugin.status = "stopped"
            
            logger.info(f"Stopped plugin: {plugin_name}")
            return {"status": "success", "message": f"Plugin {plugin_name} stopped successfully"}
            
        except Exception as e:
            logger.error(f"Failed to stop plugin {plugin_name}: {str(e)}")
            raise 