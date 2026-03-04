"""
RAG 服务模块 - 检索增强生成服务（单例模式 + 缓存）
"""
from typing import List, Optional, Dict
from functools import lru_cache
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from model.factory import get_chat_model
from utils.logger_handler import logger


class RagQueryCache:
    _cache: Dict[str, str] = {}
    _max_size = 100
    
    @classmethod
    def get(cls, query: str) -> Optional[str]:
        return cls._cache.get(query)
    
    @classmethod
    def set(cls, query: str, result: str) -> None:
        if len(cls._cache) >= cls._max_size:
            cls._cache.pop(next(iter(cls._cache)), None)
        cls._cache[query] = result
    
    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()


def _print_prompt(prompt: PromptTemplate) -> PromptTemplate:
    logger.debug(f"[RAG Prompt] {'='*20}")
    logger.debug(f"[RAG Prompt] {prompt.to_string()}")
    logger.debug(f"[RAG Prompt] {'='*20}")
    return prompt


class RagSummarizeService:
    _instance: Optional["RagSummarizeService"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "RagSummarizeService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        try:
            self.vector_store = VectorStoreService()
            self.retriever = self.vector_store.get_retriever()
            self.prompt_text = load_rag_prompts()
            self.prompt_template = PromptTemplate.from_template(self.prompt_text)
            self.model = get_chat_model()
            self.chain = None
            self._initialized = True
            logger.info("[RAG 服务] 初始化成功")
        except Exception as e:
            logger.error(f"[RAG 服务] 初始化失败：{str(e)}")
            raise
    
    def _init_chain(self) -> Optional:
        if self.model is None:
            return None
        try:
            chain = self.prompt_template | _print_prompt | self.model | StrOutputParser()
            return chain
        except Exception as e:
            logger.error(f"[RAG 服务] 创建链失败：{str(e)}")
            return None
    
    def get_chain(self) -> Optional:
        if self.chain is None:
            self.chain = self._init_chain()
        return self.chain
    
    def retriever_docs(self, query: str) -> List[Document]:
        try:
            return self.retriever.invoke(query)
        except Exception as e:
            logger.error(f"[RAG 服务] 检索失败：{str(e)}")
            return []
    
    def rag_summarize(self, query: str) -> str:
        cached_result = RagQueryCache.get(query)
        if cached_result:
            logger.debug(f"[RAG 服务] 使用缓存结果：{query[:50]}...")
            return cached_result
        
        chain = self.get_chain()
        if chain is None:
            error_msg = "RAG 服务不可用：模型未初始化或 DASHSCOPE_API_KEY 未设置"
            logger.error(error_msg)
            return error_msg
        
        try:
            context_docs = self.retriever_docs(query)
            
            if not context_docs:
                logger.warning(f"[RAG 服务] 未找到相关文档：{query[:50]}...")
                return f"未找到与'{query}'相关的参考资料，请尝试其他问题。"
            
            context = ""
            for idx, doc in enumerate(context_docs, 1):
                context += f"【参考资料{idx}】：{doc.page_content} | 来源：{doc.metadata.get('source', 'unknown')}\n"
            
            result = chain.invoke({
                "input": query,
                "context": context,
            })
            
            RagQueryCache.set(query, result)
            logger.info(f"[RAG 服务] 成功处理查询：{query[:50]}...")
            return result
            
        except Exception as e:
            error_msg = f"RAG 总结失败：{str(e)}"
            logger.error(f"[RAG 服务] {error_msg}")
            return error_msg
    
    @classmethod
    def clear_cache(cls) -> None:
        RagQueryCache.clear()
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
        cls._initialized = False


@lru_cache(maxsize=1)
def get_rag_service() -> RagSummarizeService:
    return RagSummarizeService()


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize("小户型适合哪些扫地机器人"))
