# 智扫通 - 扫地机器人智能客服系统

一个基于 LangChain + LangGraph + Streamlit 构建的智能客服系统，专为扫地机器人产品设计。

## 功能特性

- **智能对话** - 基于 ReAct Agent 架构，支持多轮对话和上下文理解
- **RAG 检索增强** - 从产品知识库中检索相关信息，提供准确的回答
- **多工具集成** - 支持天气查询、用户信息获取、使用报告生成等多种工具
- **记忆管理** - 自动保存对话历史，支持会话管理
- **知识库管理** - 支持 TXT 和 PDF 格式的知识文档，自动向量化
- **流式响应** - 实时显示 AI 回答，提升用户体验
- **文档查看** - 内置知识库文档查看功能

## 前置要求

- Python 3.9+
- DashScope API Key（通义千问）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository_url>
cd Agent_test
```

### 2. 创建虚拟环境

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

### 5. 准备知识库文件

将产品文档（TXT 或 PDF 格式）放入 `data/` 目录。

### 6. 初始化向量库

```bash
python rag/vector_store.py
```

### 7. 启动应用

```bash
streamlit run app.py
```

访问 `http://localhost:8501`

## 项目结构

```
Agent_test/
├── agent/                  # Agent 相关模块
│   ├── react_agent.py     # ReAct Agent 实现
│   └── tools/             # 工具函数
├── config/                 # 配置文件
├── data/                   # 知识库数据
│   └── external/          # 外部数据
├── memory/                 # 记忆管理
│   └── memory_manager.py
├── model/                  # 模型工厂
│   └── factory.py
├── prompts/                # 提示词模板
├── rag/                    # RAG 服务
│   ├── rag_service.py
│   └── vector_store.py
├── utils/                  # 工具函数
├── app.py                  # Streamlit 主应用
└── requirements.txt        # 依赖列表
```

## 配置说明

### ChromaDB 配置 (config/chroma.yml)

```yaml
collection_name: agent
persist_directory: ./chroma_db
k: 3
chunk_size: 200
chunk_overlap: 20
```

### RAG 配置 (config/rag.yml)

```yaml
chat_model_name: qwen3-max
embedding_model_name: text-embedding-v4
```

## 开发指南

### 添加新工具

在 `agent/tools/agent_tools.py` 中添加：

```python
@tool(description="工具描述")
def new_tool(param1: str) -> str:
    return f"结果：{param1}"
```

### 自定义提示词

1. 在 `prompts/` 目录创建提示词文件
2. 在 `config/prompts.yml` 中配置路径

## 常见问题

**Q: 提示 "DASHSCOPE_API_KEY 未设置"**
A: 检查 `.env` 文件是否正确创建

**Q: 向量库加载失败**
A: 检查 `data/` 目录是否有有效的文档文件

**Q: Streamlit 无法启动**
A: 确认端口 8501 未被占用

## 许可证

MIT License