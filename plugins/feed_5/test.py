import asyncio
import os
import yaml
from main import *  # 导入插件类

async def test_plugin():
    try:
        # 读取配置文件
        with open("plugin.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 创建插件实例
        plugin_class = [cls for cls in globals().values() 
                       if isinstance(cls, type) and cls.__name__.endswith("Plugin")][0]
        plugin = plugin_class(config["name"], config)
        
        # 测试健康检查
        print("\n=== 测试健康检查 ===")
        is_healthy = await plugin.health_check()
        print(f"健康状态: {'正常' if is_healthy else '异常'}")
        
        # 测试搜索功能
        print("\n=== 测试搜索功能 ===")
        keywords = ["测试", "news", "市场"]
        
        for keyword in keywords:
            print(f"\n搜索关键词: {keyword}")
            results = await plugin.search(keyword)
            
            if results:
                print(f"找到 {len(results)} 条结果:")
                for i, result in enumerate(results, 1):
                    print(f"\n--- 结果 {i} ---")
                    print(f"平台: {result['platform']}")
                    print(f"内容: {result['content'][:100]}...")
                    print(f"链接: {result['url']}")
                    if 'metadata' in result:
                        metadata = result['metadata']
                        print(f"标题: {metadata.get('title', 'N/A')}")
                        print(f"时间: {metadata.get('published', 'N/A')}")
                        print(f"作者: {metadata.get('author', 'N/A')}")
                        print(f"来源: {metadata.get('source', 'N/A')}")
            else:
                print("未找到相关结果")
                
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 确保在插件目录中运行测试
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(test_plugin())
