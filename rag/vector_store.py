"""
向量存储服务 - Chroma 向量库管理（单例模式）
"""
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from utils.config_handler import get_chroma_config
from model.factory import get_embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path, safe_join
from utils.file_handler import (
    pdf_loader,
    txt_loader,
    listdir_with_allowed_type,
    get_file_md5_hex
)
from utils.logger_handler import logger
import os


class MD5Store:
    def __init__(self, store_path: str) -> None:
        self.store_path = store_path
        self._md5_set: set = set()
        self._load()
    
    def _load(self) -> None:
        if not os.path.exists(self.store_path):
            return
        
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                self._md5_set = {line.strip() for line in f if line.strip()}
            logger.debug(f"[MD5 存储] 已加载 {len(self._md5_set)} 个 MD5 记录")
        except Exception as e:
            logger.error(f"[MD5 存储] 加载失败：{str(e)}")
            self._md5_set = set()
    
    def contains(self, md5_hex: str) -> bool:
        return md5_hex in self._md5_set
    
    def add(self, md5_hex: str) -> None:
        if md5_hex not in self._md5_set:
            self._md5_set.add(md5_hex)
            try:
                with open(self.store_path, "a", encoding="utf-8") as f:
                    f.write(md5_hex + "\n")
            except Exception as e:
                logger.error(f"[MD5 存储] 保存失败：{str(e)}")
    
    def clear(self) -> None:
        self._md5_set.clear()
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                pass
        except Exception as e:
            logger.error(f"[MD5 存储] 清空失败：{str(e)}")


class VectorStoreService:
    _instance: Optional["VectorStoreService"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        try:
            config = get_chroma_config()
            embed = get_embed_model()
            
            if embed is None:
                raise RuntimeError("嵌入模型初始化失败")
            
            persist_dir = config.get("persist_directory", "./chroma_db")
            if not os.path.isabs(persist_dir):
                persist_dir = get_abs_path(persist_dir)
            
            self.vector_store = Chroma(
                collection_name=config.get("collection_name", "agent"),
                embedding_function=embed,
                persist_directory=persist_dir,
            )
            
            self.spliter = RecursiveCharacterTextSplitter(
                chunk_size=config.get("chunk_size", 200),
                chunk_overlap=config.get("chunk_overlap", 20),
                separators=config.get("separators", ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]),
                length_function=len,
            )
            
            md5_store_path = config.get("md5_hex_store", "md5.text")
            if not os.path.isabs(md5_store_path):
                md5_store_path = get_abs_path(md5_store_path)
            self.md5_store = MD5Store(md5_store_path)
            
            self._initialized = True
            logger.info("[向量库服务] 初始化成功")
            
        except Exception as e:
            logger.error(f"[向量库服务] 初始化失败：{str(e)}")
            raise
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        config = get_chroma_config()
        k = config.get("k", 3)
        
        if search_kwargs:
            k = search_kwargs.get("k", k)
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def _get_file_documents(self, read_path: str) -> List[Document]:
        if read_path.endswith(".txt"):
            return txt_loader(read_path)
        elif read_path.endswith(".pdf"):
            return pdf_loader(read_path)
        return []
    
    def load_document(self) -> int:
        config = get_chroma_config()
        data_path = config.get("data_path", "data")
        if not os.path.isabs(data_path):
            data_path = get_abs_path(data_path)
        
        allowed_types = tuple(config.get("allow_knowledge_file_type", ["txt", "pdf"]))
        allowed_files = listdir_with_allowed_type(data_path, allowed_types)
        
        if not allowed_files:
            logger.warning(f"[加载知识库] 在{data_path}中未找到允许的文件类型：{allowed_types}")
            return 0
        
        loaded_count = 0
        
        for file_path in allowed_files:
            md5_hex = get_file_md5_hex(file_path)
            
            if not md5_hex:
                logger.warning(f"[加载知识库] 无法计算文件 MD5：{file_path}")
                continue
            
            if self.md5_store.contains(md5_hex):
                logger.info(f"[加载知识库] 文件已存在：{file_path}，跳过")
                continue
            
            try:
                documents = self._get_file_documents(file_path)
                
                if not documents:
                    logger.warning(f"[加载知识库] 文件无有效内容：{file_path}")
                    self.md5_store.add(md5_hex)
                    continue
                
                split_documents = self.spliter.split_documents(documents)
                
                if not split_documents:
                    logger.warning(f"[加载知识库] 文件分片后无内容：{file_path}")
                    self.md5_store.add(md5_hex)
                    continue
                
                self.vector_store.add_documents(split_documents)
                self.md5_store.add(md5_hex)
                loaded_count += 1
                
                logger.info(f"[加载知识库] 成功加载：{file_path}")
                
            except Exception as e:
                logger.error(f"[加载知识库] 加载失败 {file_path}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"[加载知识库] 本次加载完成，共加载 {loaded_count} 个文件")
        return loaded_count


def get_vector_store_service() -> VectorStoreService:
    return VectorStoreService()


if __name__ == "__main__":
    vs = VectorStoreService()
    count = vs.load_document()
    print(f"加载完成，共加载 {count} 个文件")
    
    retriever = vs.get_retriever()
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("-" * 20)
