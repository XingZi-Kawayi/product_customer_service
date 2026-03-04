"""
中间件模块 - Agent 工具监控和提示词切换
"""
from typing import Callable, Dict, Any, Optional
from utils.prompt_loader import load_system_prompts, load_report_prompts
from utils.logger_handler import logger


AgentState = Dict[str, Any]


def monitor_tool(
    tool_name: str,
    tool_args: dict,
    handler: Callable,
    runtime_context: Optional[Dict[str, Any]] = None,
) -> Any:
    logger.info(f"[tool monitor] 执行工具：{tool_name}")
    logger.debug(f"[tool monitor] 参数：{tool_args}")
    
    try:
        result = handler()
        logger.info(f"[tool monitor] 工具{tool_name}执行成功")
        
        if tool_name == "fill_context_for_report" and runtime_context is not None:
            runtime_context["report"] = True
            logger.info("[tool monitor] 已标记报告生成上下文")
        
        return result
        
    except Exception as e:
        logger.error(f"[tool monitor] 工具{tool_name}执行失败：{str(e)}")
        raise


def log_before_model(state: AgentState) -> None:
    try:
        messages = state.get("messages", [])
        msg_count = len(messages)
        logger.info(f"[log_before_model] 即将调用模型，消息数：{msg_count}")
        
        if messages:
            last_msg = messages[-1]
            msg_type = type(last_msg).__name__
            msg_content = str(last_msg.content)[:100].strip()
            logger.debug(f"[log_before_model] 最后消息 [{msg_type}]: {msg_content}...")
    except Exception as e:
        logger.error(f"[log_before_model] 日志记录失败：{str(e)}")


def report_prompt_switch(runtime_context: Optional[Dict[str, Any]] = None) -> str:
    if runtime_context is None:
        return load_system_prompts()
    
    is_report = runtime_context.get("report", False)
    
    if is_report:
        logger.info("[report_prompt_switch] 使用报告生成提示词")
        return load_report_prompts()
    else:
        logger.debug("[report_prompt_switch] 使用系统提示词")
        return load_system_prompts()
