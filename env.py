# test_env.py
import os

# 读取环境变量
api_key = os.getenv("DASHSCOPE_API_KEY")

# 打印检测结果
print("读取到的 DASHSCOPE_API_KEY：", api_key)
print("环境变量是否存在：", "DASHSCOPE_API_KEY" in os.environ)

