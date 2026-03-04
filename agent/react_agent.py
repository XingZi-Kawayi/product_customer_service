"""
ReAct Agent 模块 - 基于 LangGraph 的智能代理
"""
from typing import Generator, Optional, Dict, Any
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage
from model.factory import get_chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (
    rag_summarize,
    get_weather,
    get_user_location,
    get_user_id,
    get_current_month,
    fetch_external_data,
    fill_context_for_report,
)
from memory.memory_manager import MemoryManager
from utils.logger_handler import logger


class ReactAgent:
    def __init__(self, memory_manager: Optional[MemoryManager] = None) -> None:
        try:
            chat_model = get_chat_model()
            if chat_model is None:
                raise RuntimeError("请在环境变量中设置 DASHSCOPE_API_KEY")
            
            self.agent = create_agent(
                model=chat_model,
                tools=[
                    rag_summarize,
                    get_weather,
                    get_user_location,
                    get_user_id,
                    get_current_month,
                    fetch_external_data,
                    fill_context_for_report,
                ],
            )
            
            self.system_prompt = load_system_prompts()
            self.memory = memory_manager
            self.runtime_context: Dict[str, Any] = {"report": False}
            
            logger.info("[ReAct Agent] 初始化成功")
            
        except Exception as e:
            logger.error(f"[ReAct Agent] 初始化失败：{str(e)}")
            raise
    
    def execute_stream(self, query: str) -> Generator[str, None, None]:
        try:
            if self.memory:
                messages = self.memory.get_langchain_messages(
                    system_prompt=self.system_prompt
                )
                messages.append(HumanMessage(content=query))
                input_dict = {"messages": messages}
            else:
                input_dict = {
                    "messages": [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=query),
                    ]
                }
            
            for event in self.agent.stream(
                input_dict,
                stream_mode="updates",
                context=self.runtime_context,
            ):
                for node_name, node_output in event.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if isinstance(msg, AIMessageChunk) and msg.content:
                                yield msg.content
                            elif hasattr(msg, "content") and msg.content and not isinstance(msg, AIMessageChunk):
                                yield msg.content
            
            self.runtime_context["report"] = False
            
        except Exception as e:
            error_msg = f"Agent 执行失败：{str(e)}"
            logger.error(f"[ReAct Agent] {error_msg}", exc_info=True)
            yield error_msg
    
    def set_memory(self, memory_manager: MemoryManager) -> None:
        self.memory = memory_manager
        logger.debug(f"[ReAct Agent] 已设置记忆管理器：{memory_manager.session_id}")
    
    def reset_context(self) -> None:
        self.runtime_context = {"report": False}
        logger.debug("[ReAct Agent] 上下文已重置")


if __name__ == "__main__":
    agent = ReactAgent()
    
    print("用户：给我生成我的使用报告")
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
    print()
