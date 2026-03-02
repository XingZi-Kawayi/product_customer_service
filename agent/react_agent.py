from langgraph.prebuilt import create_react_agent as create_agent
from model.factory import get_chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)


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

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
