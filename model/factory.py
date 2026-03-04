"""
模型工厂模块 - 提供统一的模型创建接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, Dict
from functools import lru_cache
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from utils.config_handler import get_rag_config
import os

os.environ.setdefault('NO_PROXY', '*')


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Union[Embeddings, BaseChatModel]]:
        pass


class ChatModelFactory(BaseModelFactory):
    _instances: Dict[str, ChatTongyi] = {}
    _config_cache: Optional[Dict] = None
    
    def _get_config(self) -> Dict:
        if self._config_cache is None:
            self._config_cache = get_rag_config()
        return self._config_cache
    
    def generator(self) -> Optional[ChatTongyi]:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return None
        
        config = self._get_config()
        model_name = config.get("chat_model_name", "qwen-max")
        cache_key = f"{model_name}"
        
        if cache_key not in self._instances:
            self._instances[cache_key] = ChatTongyi(
                model=model_name,
                dashscope_api_key=api_key,
                streaming=True,
                max_retries=3,
            )
        
        return self._instances[cache_key]
    
    @classmethod
    def invalidate_cache(cls) -> None:
        cls._config_cache = None
        cls._instances.clear()


class EmbeddingsFactory(BaseModelFactory):
    _instances: Dict[str, DashScopeEmbeddings] = {}
    _config_cache: Optional[Dict] = None
    
    def _get_config(self) -> Dict:
        if self._config_cache is None:
            self._config_cache = get_rag_config()
        return self._config_cache
    
    def generator(self) -> Optional[DashScopeEmbeddings]:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return None
        
        config = self._get_config()
        model_name = config.get("embedding_model_name", "text-embedding-v2")
        cache_key = f"{model_name}"
        
        if cache_key not in self._instances:
            self._instances[cache_key] = DashScopeEmbeddings(
                model=model_name,
                dashscope_api_key=api_key,
            )
        
        return self._instances[cache_key]
    
    @classmethod
    def invalidate_cache(cls) -> None:
        cls._config_cache = None
        cls._instances.clear()


@lru_cache(maxsize=2)
def get_chat_model() -> Optional[ChatTongyi]:
    return ChatModelFactory().generator()


@lru_cache(maxsize=2)
def get_embed_model() -> Optional[DashScopeEmbeddings]:
    return EmbeddingsFactory().generator()


def invalidate_model_cache() -> None:
    get_chat_model.cache_clear()
    get_embed_model.cache_clear()
    ChatModelFactory.invalidate_cache()
    EmbeddingsFactory.invalidate_cache()


if __name__ == "__main__":
    model = get_chat_model()
    if model:
        print(f"模型加载成功：{model.model_name}")
    else:
        print("模型加载失败，请检查 DASHSCOPE_API_KEY 环境变量")
