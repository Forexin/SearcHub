import os
import sys
import subprocess
import venv  # 使用 venv 替代 virtualenv
import json
from typing import Dict, Optional
import yaml
from loguru import logger

class EnvironmentManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.environments: Dict[str, str] = {}  # 环境名称 -> 环境路径的映射
        self.shared_envs: Dict[str, str] = {}  # 共享环境名称 -> 环境路径的映射
        self.env_base_path = os.path.join(os.getcwd(), ".environments")
        os.makedirs(self.env_base_path, exist_ok=True)

    def _load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def setup_environment(self, plugin_info: dict) -> str:
        """
        为插件设置运行环境
        返回环境路径
        """
        env_name = f"{plugin_info['name']}_{plugin_info['version']}"
        
        # 检查是否已存在环境
        if env_name in self.environments:
            return self.environments[env_name]

        try:
            # 确定环境类型和依赖
            runtime = plugin_info['environment']['runtime']
            dependencies = plugin_info['environment'].get('dependencies', [])

            # 创建环境
            env_path = await self._create_environment(env_name, runtime)
            
            # 安装依赖
            await self._install_dependencies(env_path, dependencies)
            
            # 记录环境路径
            self.environments[env_name] = env_path
            
            return env_path
        
        except Exception as e:
            logger.error(f"Failed to setup environment for {env_name}: {str(e)}")
            raise

    async def setup_shared_environment(self, name: str, version: str) -> str:
        """
        设置共享环境
        """
        env_key = f"{name}_{version}"
        if env_key in self.shared_envs:
            return self.shared_envs[env_key]

        env_path = os.path.join(self.env_base_path, f"shared_{env_key}")
        
        try:
            if not os.path.exists(env_path):
                # 创建虚拟环境
                venv.create(env_path, with_pip=True)
                
                # 安装指定版本的包
                pip_path = os.path.join(env_path, "bin", "pip")
                if not os.path.exists(pip_path):
                    pip_path = os.path.join(env_path, "Scripts", "pip.exe")  # Windows路径
                subprocess.run([pip_path, "install", f"{name}=={version}"], check=True)
            
            self.shared_envs[env_key] = env_path
            return env_path
            
        except Exception as e:
            logger.error(f"Failed to setup shared environment {env_key}: {str(e)}")
            raise

    async def _create_environment(self, env_name: str, runtime: str) -> str:
        """
        创建特定运行时的环境
        """
        env_path = os.path.join(self.env_base_path, env_name)
        
        if runtime.startswith("python"):
            # 使用 venv 创建环境
            venv.create(env_path, with_pip=True)
            logger.info(f"Created Python virtual environment at {env_path}")
        elif runtime.startswith("node"):
            # TODO: 实现Node.js环境创建
            pass
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")
            
        return env_path

    async def _install_dependencies(self, env_path: str, dependencies: list):
        """
        在指定环境中安装依赖
        """
        pip_path = os.path.join(env_path, "bin", "pip")
        if not os.path.exists(pip_path):
            pip_path = os.path.join(env_path, "Scripts", "pip.exe")  # Windows路径
            
        for dep in dependencies:
            try:
                subprocess.run([pip_path, "install", dep], check=True)
                logger.info(f"Installed dependency: {dep}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependency {dep}: {str(e)}")
                raise

    async def cleanup_environment(self, env_name: str):
        """
        清理特定环境
        """
        if env_name in self.environments:
            env_path = self.environments[env_name]
            # TODO: 实现环境清理逻辑
            del self.environments[env_name] 