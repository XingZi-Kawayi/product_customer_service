"""
Agent 工具模块 - 提供 ReAct Agent 可用的工具函数
"""
import os
from typing import Dict, Optional
from langchain_core.tools import tool
from utils.logger_handler import logger
from utils.config_handler import get_agent_config
from utils.path_tool import get_abs_path
from rag.rag_service import get_rag_service
import random


class ToolDataStore:
    _user_ids: tuple = ("1001", "1002", "1003", "1004", "1005", 
                        "1006", "1007", "1008", "1009", "1010")
    _months: tuple = ("2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
                      "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12")
    _cities: tuple = ("深圳", "合肥", "杭州")
    _external_data: Dict[str, Dict[str, Dict[str, str]]] = {}
    _data_loaded: bool = False
    
    @classmethod
    def get_user_id(cls) -> str:
        return random.choice(cls._user_ids)
    
    @classmethod
    def get_month(cls) -> str:
        return random.choice(cls._months)
    
    @classmethod
    def get_city(cls) -> str:
        return random.choice(cls._cities)
    
    @classmethod
    def load_external_data(cls, data_path: str) -> bool:
        if cls._data_loaded:
            return True
        
        if not os.path.exists(data_path):
            logger.error(f"[外部数据] 文件不存在：{data_path}")
            return False
        
        try:
            cls._external_data.clear()
            
            with open(data_path, "r", encoding="utf-8") as f:
                for line in f.readlines()[1:]:
                    arr = line.strip().split(",")
                    if len(arr) < 6:
                        continue
                    
                    user_id = arr[0].replace('"', "")
                    feature = arr[1].replace('"', "")
                    efficiency = arr[2].replace('"', "")
                    consumables = arr[3].replace('"', "")
                    comparison = arr[4].replace('"', "")
                    time = arr[5].replace('"', "")
                    
                    if user_id not in cls._external_data:
                        cls._external_data[user_id] = {}
                    
                    cls._external_data[user_id][time] = {
                        "特征": feature,
                        "效率": efficiency,
                        "耗材": consumables,
                        "对比": comparison,
                    }
            
            cls._data_loaded = True
            logger.info(f"[外部数据] 加载成功，共 {len(cls._external_data)} 个用户")
            return True
            
        except Exception as e:
            logger.error(f"[外部数据] 加载失败：{str(e)}")
            return False
    
    @classmethod
    def get_external_data(cls, user_id: str, month: str) -> Optional[Dict[str, str]]:
        if not cls._data_loaded:
            return None
        
        user_data = cls._external_data.get(user_id)
        if not user_data:
            return None
        
        return user_data.get(month)
    
    @classmethod
    def clear(cls) -> None:
        cls._external_data.clear()
        cls._data_loaded = False


_rag_service: Optional[object] = None


def _get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = get_rag_service()
    return _rag_service


@tool(description="从向量存储中检索参考资料并总结回答用户问题")
def rag_summarize(query: str) -> str:
    try:
        service = _get_rag_service()
        return service.rag_summarize(query)
    except Exception as e:
        logger.error(f"[rag_summarize] 执行失败：{str(e)}")
        return f"检索失败：{str(e)}"


@tool(description="获取指定城市的天气信息，返回天气、气温、湿度、风向、AQI 等")
def get_weather(city: str) -> str:
    try:
        return f"城市{city}天气为晴天，气温 26 摄氏度，空气湿度 50%，南风 1 级，AQI21，最近 6 小时降雨概率极低"
    except Exception as e:
        logger.error(f"[get_weather] 执行失败：{str(e)}")
        return f"天气查询失败：{str(e)}"


@tool(description="获取用户所在城市的名称")
def get_user_location() -> str:
    return ToolDataStore.get_city()


@tool(description="获取用户的 ID")
def get_user_id() -> str:
    return ToolDataStore.get_user_id()


@tool(description="获取当前月份，格式为 YYYY-MM")
def get_current_month() -> str:
    return ToolDataStore.get_month()


@tool(description="从外部系统获取指定用户在指定月份的使用记录，返回包含特征、效率、耗材、对比信息的字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    config = get_agent_config()
    data_path_key = config.get("external_data_path", "data/external/records.csv")
    data_path = get_abs_path(data_path_key)
    
    if not ToolDataStore.load_external_data(data_path):
        return "外部数据加载失败"
    
    data = ToolDataStore.get_external_data(user_id, month)
    
    if data:
        return str(data)
    else:
        logger.warning(f"[fetch_external_data] 未找到用户{user_id}在{month}的数据")
        return ""


@tool(description="无入参，调用后触发中间件为报告生成场景动态注入上下文信息")
def fill_context_for_report() -> str:
    return "fill_context_for_report 已调用"


def get_tool_list():
    return [
        rag_summarize,
        get_weather,
        get_user_location,
        get_user_id,
        get_current_month,
        fetch_external_data,
        fill_context_for_report,
    ]


if __name__ == "__main__":
    print(get_user_id())
    print(get_current_month())
    print(get_weather("深圳"))
