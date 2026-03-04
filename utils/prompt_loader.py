"""
提示词加载模块 - 从配置文件加载提示词
"""
from typing import Optional
from utils.config_handler import get_prompts_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


prompts_conf = get_prompts_config()


def load_system_prompts() -> str:
    try:
        main_prompt_path = prompts_conf.get("main_prompt_path")
        if not main_prompt_path:
            raise KeyError("配置中缺少 main_prompt_path 配置项")
        
        system_prompt_path = get_abs_path(main_prompt_path)
        
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"[load_system_prompts] 提示词文件不存在：{system_prompt_path}")
        raise
    except KeyError as e:
        logger.error(f"[load_system_prompts] 配置错误：{str(e)}")
        raise
    except Exception as e:
        logger.error(f"[load_system_prompts] 读取系统提示词失败：{str(e)}")
        raise


def load_rag_prompts() -> str:
    try:
        rag_prompt_path_key = prompts_conf.get("rag_summarize_prompt_path")
        if not rag_prompt_path_key:
            raise KeyError("配置中缺少 rag_summarize_prompt_path 配置项")
        
        rag_prompt_path = get_abs_path(rag_prompt_path_key)
        
        with open(rag_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"[load_rag_prompts] 提示词文件不存在：{rag_prompt_path}")
        raise
    except KeyError as e:
        logger.error(f"[load_rag_prompts] 配置错误：{str(e)}")
        raise
    except Exception as e:
        logger.error(f"[load_rag_prompts] 读取 RAG 提示词失败：{str(e)}")
        raise


def load_report_prompts() -> str:
    try:
        report_prompt_path_key = prompts_conf.get("report_prompt_path")
        if not report_prompt_path_key:
            raise KeyError("配置中缺少 report_prompt_path 配置项")
        
        report_prompt_path = get_abs_path(report_prompt_path_key)
        
        with open(report_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"[load_report_prompts] 提示词文件不存在：{report_prompt_path}")
        raise
    except KeyError as e:
        logger.error(f"[load_report_prompts] 配置错误：{str(e)}")
        raise
    except Exception as e:
        logger.error(f"[load_report_prompts] 读取报告提示词失败：{str(e)}")
        raise


if __name__ == "__main__":
    print(load_report_prompts())
