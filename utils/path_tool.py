"""
安全路径处理工具 - 防止路径遍历攻击
"""
import os
from pathlib import Path
from typing import Optional, List


def get_project_root() -> str:
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root


def get_base_dir() -> str:
    return get_project_root()


def is_safe_path(path: str, allowed_bases: Optional[List[str]] = None) -> bool:
    if allowed_bases is None:
        allowed_bases = [get_base_dir()]
    
    try:
        abs_path = os.path.abspath(path)
        resolved_path = os.path.realpath(abs_path)
        
        for base_dir in allowed_bases:
            base_resolved = os.path.realpath(os.path.abspath(base_dir))
            if resolved_path.startswith(base_resolved + os.sep) or resolved_path == base_resolved:
                return True
        
        return False
    except Exception:
        return False


def get_abs_path(relative_path: str) -> str:
    if not relative_path:
        raise ValueError("路径不能为空")
    
    if os.path.isabs(relative_path):
        if is_safe_path(relative_path):
            return os.path.normpath(relative_path)
        else:
            raise ValueError(f"不允许访问的绝对路径：{relative_path}")
    
    project_root = get_project_root()
    abs_path = os.path.normpath(os.path.join(project_root, relative_path))
    
    if is_safe_path(abs_path):
        return abs_path
    else:
        raise ValueError(f"路径遍历攻击检测：{relative_path}")


def safe_join(base_path: str, *paths: str) -> str:
    base_abs = get_abs_path(base_path) if not os.path.isabs(base_path) else base_path
    
    if not is_safe_path(base_abs):
        raise ValueError(f"基础路径不安全：{base_path}")
    
    result_path = base_abs
    for path in paths:
        if os.path.isabs(path):
            raise ValueError(f"不允许拼接绝对路径：{path}")
        if ".." in path:
            raise ValueError(f"路径包含非法字符：{path}")
        result_path = os.path.join(result_path, path)
    
    result_path = os.path.normpath(result_path)
    
    if is_safe_path(result_path):
        return result_path
    else:
        raise ValueError(f"拼接后路径不安全：{result_path}")


def get_relative_path(path: str, base: Optional[str] = None) -> str:
    if base is None:
        base = get_base_dir()
    
    abs_path = get_abs_path(path)
    abs_base = get_abs_path(base)
    
    try:
        return os.path.relpath(abs_path, abs_base)
    except ValueError as e:
        raise


if __name__ == "__main__":
    print(get_abs_path("config/rag.yml"))
    print(get_abs_path("./data"))
    print(safe_join("data", "external", "records.csv"))
