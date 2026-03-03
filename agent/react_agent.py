from langgraph.prebuilt import create_react_agent as create_agent
from model.factory import get_chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
from langchain_core.messages import AIMessageChunk


class ReactAgent:
    def __init__(self):
        chat_model = get_chat_model()
        if chat_model is None:
            raise RuntimeError("请在环境变量中设置 DASHSCOPE_API_KEY")
        self.agent = create_agent(
            model=chat_model,
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report],
        )
        self.system_prompt = load_system_prompts()

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query},
            ]
        }

        for event in self.agent.stream(input_dict, stream_mode="updates", context={"report": False}):
            for node_name, node_output in event.items():
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, AIMessageChunk) and msg.content:
                            yield msg.content
                        elif hasattr(msg, "content") and msg.content and not isinstance(msg, AIMessageChunk):
                            yield msg.content


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
