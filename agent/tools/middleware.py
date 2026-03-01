from typing import Callable, Dict, Any
from utils.prompt_loader import load_system_prompts, load_report_prompts
from utils.logger_handler import logger

# AgentState 在旧版本中是字典类型
AgentState = Dict[str, Any]


def monitor_tool(
        tool_name: str,
        tool_args: dict,
        handler: Callable,
        runtime_context: dict = None,
):
    logger.info(f"[tool monitor]执行工具：{tool_name}")
    logger.info(f"[tool monitor]传入参数：{tool_args}")

    try:
        result = handler()
        logger.info(f"[tool monitor]工具{tool_name}调用成功")

        if tool_name == "fill_context_for_report" and runtime_context:
            runtime_context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{tool_name}调用失败，原因：{str(e)}")
        raise e


def log_before_model(state: AgentState):
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")


def report_prompt_switch(runtime_context: dict = None):
    is_report = runtime_context.get("report", False) if runtime_context else False
    if is_report:
        return load_report_prompts()
    return load_system_prompts()
