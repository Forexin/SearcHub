import asyncio
import aiohttp
import json
import os
from plugins.jin10_rss.main import Jin10RSSPlugin

async def test_jin10():
    # 保存当前目录
    original_dir = os.getcwd()
    
    try:
        # 切换到插件目录
        plugin_dir = os.path.join(os.getcwd(), 'plugins', 'jin10_rss')
        os.chdir(plugin_dir)
        
        # 创建插件实例
        plugin = Jin10RSSPlugin()
        
        # 测试搜索功能
        result = await plugin.search("塔斯社")
        
        # 格式化输出结果
        print("\n=== 搜索结果 ===")
        print(f"总匹配条数: {result['metadata']['matched_entries']}")
        print("\n--- 内容列表 ---")
        for item in result['content']:
            print("\n条目:")
            print(f"标题: {item['title']}")
            print(f"描述: {item['description']}")
            print(f"链接: {item['link']}")
            print(f"发布时间: {item['published']}")
            print(f"作者: {item['author']}")
            print("-" * 50)
        
        print("\n=== 元数据 ===")
        print(f"数据源: {result['metadata']['source']}")
        print(f"时间戳: {result['metadata']['timestamp']}")
        print(f"Feed标题: {result['metadata']['feed_title']}")
        print(f"Feed描述: {result['metadata']['feed_description']}")
        
    finally:
        # 恢复原始目录
        os.chdir(original_dir)

if __name__ == "__main__":
    # 确保插件目录存在
    plugin_dir = os.path.join(os.getcwd(), 'plugins', 'jin10_rss')
    if not os.path.exists(plugin_dir):
        print(f"错误: 插件目录不存在: {plugin_dir}")
        exit(1)
        
    # 确保配置文件存在
    config_file = os.path.join(plugin_dir, 'plugin.yaml')
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在: {config_file}")
        exit(1)
    
    asyncio.run(test_jin10()) 