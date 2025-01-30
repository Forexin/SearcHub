from typing import List, Dict, Any
import re
from loguru import logger
from ..models.schemas import SearchResult

class ResultAggregator:
    def __init__(self):
        self.results: List[SearchResult] = []

    async def add_result(self, platform: str, raw_result: Dict[str, Any], keyword: str):
        """
        添加并处理搜索结果
        """
        try:
            # 提取相关内容
            processed_content = self._extract_relevant_content(raw_result.get('content', ''), keyword)
            
            if processed_content:
                result = SearchResult(
                    platform=platform,
                    content=processed_content,
                    url=raw_result.get('url'),
                    metadata=raw_result.get('metadata', {})
                )
                self.results.append(result)
                
        except Exception as e:
            logger.error(f"Error processing result from {platform}: {str(e)}")

    def _extract_relevant_content(self, content: str, keyword: str) -> str:
        """
        从内容中提取与关键词相关的部分
        """
        # 将关键词分词（处理多关键词情况）
        keywords = keyword.split()
        
        # 找到包含关键词的段落
        paragraphs = content.split('\n')
        relevant_paragraphs = []
        
        for para in paragraphs:
            if any(keyword.lower() in para.lower() for keyword in keywords):
                # 提取关键词所在句子及其上下文
                sentences = re.split('[.!?。！？]', para)
                for i, sentence in enumerate(sentences):
                    if any(keyword.lower() in sentence.lower() for keyword in keywords):
                        # 获取上下文（前后各一句）
                        start = max(0, i - 1)
                        end = min(len(sentences), i + 2)
                        context = ' '.join(sentences[start:end]).strip()
                        if context and context not in relevant_paragraphs:
                            relevant_paragraphs.append(context)
        
        return '\n'.join(relevant_paragraphs)

    def get_aggregated_results(self) -> List[SearchResult]:
        """
        获取聚合后的结果
        """
        # 按平台分组并排序
        sorted_results = sorted(self.results, key=lambda x: x.platform)
        return sorted_results

    def clear_results(self):
        """
        清除所有结果
        """
        self.results.clear()

    async def process_batch_results(self, batch_results: List[Dict[str, Any]], keyword: str):
        """
        批量处理搜索结果
        """
        for result in batch_results:
            await self.add_result(
                platform=result.get('platform', 'unknown'),
                raw_result=result,
                keyword=keyword
            ) 