import asyncio
import time
from typing import Dict, Optional
from loguru import logger

class RateLimiter:
    def __init__(self, requests_per_minute: int, burst_size: int, min_interval: float):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.min_interval = min_interval
        self.tokens = burst_size
        self.last_update = time.time()
        self.last_request = time.time()
        self.lock = asyncio.Lock()
        self.total_requests = 0
        self.start_time = time.time()

    async def acquire(self):
        """
        获取一个请求令牌，如果没有可用令牌则等待
        """
        async with self.lock:
            while True:
                now = time.time()
                
                # 记录和显示访问频率统计
                self.total_requests += 1
                running_time = now - self.start_time
                current_rate = self.total_requests / (running_time / 60)
                
                logger.info(
                    f"Request stats:\n"
                    f"  Total requests: {self.total_requests}\n"
                    f"  Running time: {running_time:.2f} seconds\n"
                    f"  Current rate: {current_rate:.2f} requests/minute\n"
                    f"  Available tokens: {self.tokens}\n"
                    f"  Time since last request: {now - self.last_request:.2f} seconds"
                )

                # 计算需要等待的时间
                time_since_last_request = now - self.last_request
                if time_since_last_request < self.min_interval:
                    wait_time = self.min_interval - time_since_last_request
                    logger.warning(f"Rate limit: waiting {wait_time:.2f} seconds for minimum interval")
                    await asyncio.sleep(wait_time)
                    continue

                # 更新令牌桶
                time_passed = now - self.last_update
                new_tokens = int(time_passed * (self.requests_per_minute / 60))
                self.tokens = min(self.burst_size, self.tokens + new_tokens)
                self.last_update = now

                if self.tokens > 0:
                    self.tokens -= 1
                    self.last_request = now
                    return
                
                # 计算等待时间
                wait_time = 60 / self.requests_per_minute
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

class RateLimiterManager:
    def __init__(self, global_config: Dict, plugin_configs: Dict[str, Dict] = None):
        self.limiters: Dict[str, RateLimiter] = {}
        self.global_config = global_config
        self.plugin_configs = plugin_configs or {}  # 如果没有提供插件配置，使用空字典
        self.default_config = global_config.get('default', {
            'requests_per_minute': 20,
            'burst_size': 5,
            'min_interval': 3
        })
        self.enforce_conservative = global_config.get('enforce_conservative_rate', True)

    def get_limiter(self, plugin_name: str) -> RateLimiter:
        """
        获取或创建插件的频率限制器
        """
        if plugin_name not in self.limiters:
            plugin_config = self.plugin_configs.get(plugin_name, {}).get('rate_limits', {})
            
            # 如果启用了保守频率限制，确保插件配置不超过默认限制
            if self.enforce_conservative:
                config = {
                    'requests_per_minute': min(
                        plugin_config.get('requests_per_minute', 0),
                        self.default_config['requests_per_minute']
                    ),
                    'burst_size': min(
                        plugin_config.get('burst_size', 0),
                        self.default_config['burst_size']
                    ),
                    'min_interval': max(
                        plugin_config.get('min_interval', 0),
                        self.default_config['min_interval']
                    )
                }
            else:
                config = plugin_config if plugin_config else self.default_config
            
            self.limiters[plugin_name] = RateLimiter(
                requests_per_minute=config['requests_per_minute'],
                burst_size=config['burst_size'],
                min_interval=config['min_interval']
            )
        return self.limiters[plugin_name] 