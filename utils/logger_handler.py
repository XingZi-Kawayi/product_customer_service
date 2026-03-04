"""
日志处理模块 - 统一的日志配置和管理
"""
import logging
import os
from typing import Optional
from datetime import datetime


def _get_log_root() -> str:
    import sys
    module = sys.modules.get('utils.path_tool')
    if module and hasattr(module, 'get_abs_path'):
        return module.get_abs_path("logs")
    
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, "logs")


LOG_ROOT = _get_log_root()

try:
    os.makedirs(LOG_ROOT, exist_ok=True)
except Exception:
    LOG_ROOT = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(LOG_ROOT, exist_ok=True)

LOG_FORMATS = {
    "default": logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ),
    "simple": logging.Formatter(
        "%(levelname)s - %(message)s"
    ),
    "detailed": logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
}


class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def get_logger(
    name: str = "agent",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    log_format: str = "default",
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(logging.DEBUG)
    
    if logger_instance.handlers:
        return logger_instance
    
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(LOG_FORMATS.get(log_format, LOG_FORMATS["default"]))
        logger_instance.addHandler(console_handler)
    
    if enable_file:
        if not log_file:
            log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                pass
        
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(file_level)
            file_handler.setFormatter(LOG_FORMATS.get(log_format, LOG_FORMATS["default"]))
            logger_instance.addHandler(file_handler)
        except Exception:
            pass
    
    return logger_instance


logger = get_logger()


def set_global_log_level(level: int) -> None:
    for handler in logging.root.handlers:
        handler.setLevel(level)


if __name__ == "__main__":
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
