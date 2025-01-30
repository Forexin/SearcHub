import os
import yaml
import shutil
from typing import Dict, Any
import re

class PluginGenerator:
    def __init__(self):
        self.template_dir = "plugins/example"
        self.plugins_dir = "plugins"
        
    def generate_plugin(self, yaml_path: str, code_snippet: str) -> str:
        """
        根据yaml配置和代码片段生成插件
        
        Args:
            yaml_path: plugin.yaml 文件路径
            code_snippet: 包含请求代码的字符串，如 "response = requests.get('http://example.com')"
        
        Returns:
            str: 生成的插件路径
        """
        try:
            # 读取yaml配置
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 验证必要的配置项
            self._validate_config(config)
            
            # 创建插件目录
            plugin_name = config['name']
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            os.makedirs(plugin_path, exist_ok=True)
            
            # 复制yaml文件
            shutil.copy2(yaml_path, os.path.join(plugin_path, 'plugin.yaml'))
            
            # 生成main.py
            self._generate_main_py(plugin_path, config, code_snippet)
            
            print(f"Successfully generated plugin: {plugin_name}")
            return plugin_path
            
        except Exception as e:
            print(f"Error generating plugin: {str(e)}")
            raise
    
    def _validate_config(self, config: Dict[str, Any]):
        """验证配置文件的必要字段"""
        required_fields = ['name', 'version', 'language', 'type', 'environment', 'communication']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")
                
        if 'source' not in config:
            raise ValueError("Missing 'source' configuration")
            
        if 'port' not in config['communication']:
            raise ValueError("Missing 'port' in communication config")
    
    def _generate_main_py(self, plugin_path: str, config: Dict[str, Any], code_snippet: str):
        """生成main.py文件"""
        # 从代码片段中提取导入语句
        imports = self._extract_imports(code_snippet)
        
        # 准备模板变量
        template_vars = {
            'plugin_name': config['name'],
            'plugin_class_name': ''.join(word.capitalize() for word in config['name'].split('_')),
            'imports': imports,
            'code_snippet': code_snippet
        }
        
        # 读取基础模板
        with open(os.path.join(self.template_dir, 'main.py'), 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换模板中的变量
        code = template.replace('ExamplePlugin', template_vars['plugin_class_name'])
        code = code.replace('example_plugin', template_vars['plugin_name'])
        
        # 添加导入语句
        import_section = '\n'.join(imports)
        code = code.replace('from example.main import RSSPluginBase', 
                          f'from example.main import RSSPluginBase\n{import_section}')
        
        # 在fetch_rss方法中添加代码片段
        code = self._insert_code_snippet(code, code_snippet)
        
        # 写入文件
        with open(os.path.join(plugin_path, 'main.py'), 'w', encoding='utf-8') as f:
            f.write(code)
    
    def _extract_imports(self, code_snippet: str) -> list:
        """从代码片段中提取import语句"""
        imports = []
        for line in code_snippet.split('\n'):
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def _insert_code_snippet(self, template: str, code_snippet: str) -> str:
        """在模板中插入代码片段"""
        # 移除代码片段中的import语句
        code_lines = []
        for line in code_snippet.split('\n'):
            if not line.strip().startswith(('import ', 'from ')):
                code_lines.append(f'            {line}')
        
        code_to_insert = '\n'.join(code_lines)
        
        # 在fetch_rss方法中插入代码
        return template.replace(
            'async with session.get(url, headers=self.headers) as response:',
            code_to_insert
        )

def main():
    """命令行接口"""
    import argparse
    parser = argparse.ArgumentParser(description='Generate a new plugin from yaml config and code snippet')
    parser.add_argument('yaml_path', help='Path to the plugin.yaml file')
    parser.add_argument('code_file', help='Path to the file containing the request code snippet')
    args = parser.parse_args()
    
    # 读取代码片段
    with open(args.code_file, 'r', encoding='utf-8') as f:
        code_snippet = f.read()
    
    # 生成插件
    generator = PluginGenerator()
    generator.generate_plugin(args.yaml_path, code_snippet)

if __name__ == '__main__':
    main() 