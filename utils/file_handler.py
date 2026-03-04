"""
文件处理模块 - 文档加载和文件操作工具
"""
import os
import hashlib
from typing import List, Optional, Tuple
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.logger_handler import logger


def get_file_md5_hex(filepath: str) -> Optional[str]:
    if not os.path.exists(filepath):
        logger.error(f"[md5 计算] 文件{filepath}不存在")
        return None
    
    if not os.path.isfile(filepath):
        logger.error(f"[md5 计算] 路径{filepath}不是文件")
        return None
    
    md5_obj = hashlib.md5()
    chunk_size = 8192
    
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        
        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算文件{filepath}md5 失败：{str(e)}")
        return None


def listdir_with_allowed_type(
    path: str,
    allowed_types: Tuple[str, ...]
) -> List[str]:
    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] {path}不是文件夹")
        return []
    
    files = []
    try:
        for f in os.listdir(path):
            if f.endswith(allowed_types):
                files.append(os.path.join(path, f))
        return files
    except Exception as e:
        logger.error(f"[listdir_with_allowed_type] 读取目录失败：{str(e)}")
        return []


def pdf_loader(filepath: str, passwd: Optional[str] = None) -> List[Document]:
    if not os.path.exists(filepath):
        logger.error(f"[pdf_loader] 文件不存在：{filepath}")
        return []
    
    try:
        loader = PyPDFLoader(filepath, password=passwd)
        return loader.load()
    except Exception as e:
        logger.error(f"[pdf_loader] 加载 PDF 失败：{str(e)}")
        return []


def txt_loader(filepath: str) -> List[Document]:
    if not os.path.exists(filepath):
        logger.error(f"[txt_loader] 文件不存在：{filepath}")
        return []
    
    try:
        loader = TextLoader(filepath, encoding="utf-8")
        return loader.load()
    except UnicodeDecodeError as e:
        logger.warning(f"[txt_loader] UTF-8 解码失败，尝试 GBK 编码：{str(e)}")
        try:
            loader = TextLoader(filepath, encoding="gbk")
            return loader.load()
        except Exception as e2:
            logger.error(f"[txt_loader] GBK 解码也失败：{str(e2)}")
            return []
    except Exception as e:
        logger.error(f"[txt_loader] 加载 TXT 文件失败：{str(e)}")
        return []
