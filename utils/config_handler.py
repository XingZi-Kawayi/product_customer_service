"""
配置处理模块 - 支持缓存的 YAML 配置加载器
"""
from typing import Any, Dict
from functools import lru_cache
from utils.path_tool import get_abs_path
import yaml
import os


class ConfigCache:
    _cache: Dict[str, Any] = {}
    _file_mtimes: Dict[str, float] = {}
    
    @classmethod
    def is_modified(cls, file_path: str) -> bool:
        try:
            current_mtime = os.path.getmtime(file_path)
            return cls._file_mtimes.get(file_path, 0) != current_mtime
        except OSError:
            return True
    
    @classmethod
    def update_mtime(cls, file_path: str) -> None:
        try:
            cls._file_mtimes[file_path] = os.path.getmtime(file_path)
        except OSError:
            pass
    
    @classmethod
    def invalidate(cls, file_path: str = None) -> None:
        if file_path:
            cls._cache.pop(file_path, None)
            cls._file_mtimes.pop(file_path, None)
        else:
            cls._cache.clear()
            cls._file_mtimes.clear()


@lru_cache(maxsize=4)
def _load_yaml_cached(config_path: str, encoding: str) -> Dict[str, Any]:
    abs_path = get_abs_path(config_path)
    if ConfigCache.is_modified(abs_path):
        _load_yaml_cached.cache_clear()
    
    with open(abs_path, "r", encoding=encoding) as f:
        config = yaml.safe_load(f)
    
    ConfigCache.update_mtime(abs_path)
    ConfigCache._cache[abs_path] = config
    return config


def load_rag_config(
    config_path: str = "config/rag.yml",
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    return _load_yaml_cached(get_abs_path(config_path), encoding)


def load_chroma_config(
    config_path: str = "config/chroma.yml",
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    return _load_yaml_cached(get_abs_path(config_path), encoding)


def load_prompts_config(
    config_path: str = "config/prompts.yml",
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    return _load_yaml_cached(get_abs_path(config_path), encoding)


def load_agent_config(
    config_path: str = "config/agent.yml",
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    return _load_yaml_cached(get_abs_path(config_path), encoding)


def get_rag_config() -> Dict[str, Any]:
    return load_rag_config()


def get_chroma_config() -> Dict[str, Any]:
    return load_chroma_config()


def get_prompts_config() -> Dict[str, Any]:
    return load_prompts_config()


def get_agent_config() -> Dict[str, Any]:
    return load_agent_config()


# 向后兼容：导出全局配置变量
rag_conf = get_rag_config()
chroma_conf = get_chroma_config()
prompts_conf = get_prompts_config()
agent_conf = get_agent_config()


def invalidate_config_cache(config_path: str = None) -> None:
    if config_path:
        abs_path = get_abs_path(config_path)
        ConfigCache.invalidate(abs_path)
        _load_yaml_cached.cache_clear()
    else:
        ConfigCache.invalidate()
        _load_yaml_cached.cache_clear()


if __name__ == "__main__":
    print(load_rag_config()["chat_model_name"])
