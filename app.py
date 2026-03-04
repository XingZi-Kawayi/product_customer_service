import streamlit as st
from agent.react_agent import ReactAgent
from memory.memory_manager import MemoryManager
import os
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
from utils.path_tool import get_abs_path, safe_join
from utils.config_handler import chroma_conf
from utils.logger_handler import logger

os.environ.setdefault('NO_PROXY', '*')

st.set_page_config(
    page_title="智扫通 - 机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .app-header {
        background: linear-gradient(135deg, #0078D4 0%, #00BCF2 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,120,212,0.15);
    }
    .app-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.9);
        margin: 0.2rem 0 0 0;
    }
    .stChatMessage {
        border-radius: 12px !important;
    }
    .sidebar-section {
        margin-bottom: 1.5rem;
    }
    .sidebar-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
        padding-left: 0.3rem;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1rem 0;
    }
    .nav-item {
        padding: 0.7rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 0.95rem;
        color: #374151;
        border: none;
        background: transparent;
        text-align: left;
        width: 100%;
    }
    .nav-item:hover {
        background-color: #F3F4F6;
        color: #111827;
    }
    .nav-item.active {
        background-color: #EFF6FF;
        color: #0078D4;
        font-weight: 500;
    }
    .doc-content {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        line-height: 1.8;
    }
    .doc-content h1, .doc-content h2, .doc-content h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
        color: #111827;
    }
    .doc-content h1 { font-size: 1.8rem; }
    .doc-content h2 { font-size: 1.4rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 0.5rem; }
    .doc-content h3 { font-size: 1.2rem; }
    .doc-content p { margin-bottom: 1rem; color: #374151; }
    .doc-content ul, .doc-content ol { margin-left: 1.5rem; margin-bottom: 1rem; }
    .doc-content li { margin-bottom: 0.5rem; }
    .doc-content strong { color: #111827; }
    .doc-page-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    .pdf-info {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
    .session-info {
        font-size: 0.75rem;
        color: #9CA3AF;
        margin-top: 1rem;
        padding-top: 0.5rem;
        border-top: 1px solid #E5E7EB;
    }
    .button-container {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def get_knowledge_files() -> List[str]:
    try:
        data_path = get_abs_path(chroma_conf["data_path"])
        allowed_types = tuple(chroma_conf["allow_knowledge_file_type"])
        files = []
        if os.path.exists(data_path) and os.path.isdir(data_path):
            for filename in os.listdir(data_path):
                if filename.endswith(allowed_types):
                    files.append(filename)
        return sorted(files)
    except Exception as e:
        logger.error(f"[获取知识文件] 失败：{str(e)}")
        return []


def read_pdf_content(filepath: str) -> Tuple[str, Optional[int]]:
    try:
        reader = PdfReader(filepath)
        text_content = []
        num_pages = len(reader.pages)
        
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text.strip():
                text_content.append(f"\n--- 第 {page_num + 1} 页 ---\n")
                text_content.append(text)
        
        return "\n".join(text_content), num_pages
    except Exception as e:
        logger.error(f"[读取 PDF] 失败 {filepath}: {str(e)}")
        return f"读取 PDF 文件失败：{str(e)}", 0


def read_file_content(filename: str) -> Tuple[str, Optional[int]]:
    try:
        data_path = get_abs_path(chroma_conf["data_path"])
        file_path = safe_join(data_path, filename)
        
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read(), None
        elif filename.endswith(".pdf"):
            return read_pdf_content(file_path)
        else:
            return "不支持的文件格式", None
    except Exception as e:
        logger.error(f"[读取文件] 失败 {filename}: {str(e)}")
        return f"读取文件失败：{str(e)}", None


def text_to_markdown(text: str) -> str:
    lines = text.split("\n")
    processed = []
    for line in lines:
        line = line.rstrip()
        if re.match(r"^---\s*第\s*\d+\s*页\s*---$", line):
            continue
        if re.match(r"^#{1,6}\s", line):
            processed.append(line)
        elif re.match(r"^\s*[0-9]+\.\s", line):
            processed.append(line)
        elif re.match(r"^\s*[*-]\s", line):
            processed.append(line)
        elif line.strip() and not line.startswith(" "):
            processed.append(line)
        else:
            processed.append(line)
    return "\n".join(processed)


def get_file_icon(filename: str) -> str:
    if "故障" in filename or "排除" in filename:
        return "🔧"
    elif "保养" in filename or "维护" in filename:
        return "✨"
    elif "选购" in filename or "指南" in filename:
        return "📋"
    elif "100 问" in filename:
        return "❓"
    elif ".pdf" in filename:
        return "📄"
    else:
        return "📄"


def create_session_id() -> str:
    return f"session_{uuid.uuid4().hex[:8]}"


def init_session_state() -> None:
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "chat"
    
    if "selected_file" not in st.session_state:
        st.session_state["selected_file"] = None
    
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = create_session_id()
    
    if "memory" not in st.session_state:
        st.session_state["memory"] = None
    
    if "agent" not in st.session_state:
        st.session_state["agent"] = None
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    if "loading" not in st.session_state:
        st.session_state["loading"] = False


def switch_session(new_session_id: str) -> None:
    st.session_state["session_id"] = new_session_id
    st.session_state["memory"] = MemoryManager(session_id=new_session_id)
    st.session_state["agent"] = ReactAgent(memory_manager=st.session_state["memory"])
    st.session_state["messages"] = st.session_state["memory"].get_history_messages()
    logger.info(f"[会话切换] 切换到新会话：{new_session_id}")


def clear_current_session() -> None:
    if st.session_state["session_id"]:
        MemoryManager.delete_session(st.session_state["session_id"])
    new_id = create_session_id()
    switch_session(new_id)
    logger.info(f"[会话清除] 已清除当前会话并创建新会话：{new_id}")


if __name__ == "__main__":
    init_session_state()
    
    knowledge_files = get_knowledge_files()
    
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        if st.button(
            "💬 智能客服",
            key="nav_chat",
            use_container_width=True,
            type="primary" if st.session_state["current_view"] == "chat" else "secondary",
        ):
            st.session_state["current_view"] = "chat"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">产品知识库</div>', unsafe_allow_html=True)
        
        if knowledge_files:
            for filename in knowledge_files:
                is_selected = (
                    st.session_state["current_view"] == "docs"
                    and st.session_state.get("selected_file") == filename
                )
                button_key = f"file_{filename}"
                
                label = f"{get_file_icon(filename)} {filename.replace('.txt', '').replace('.pdf', '')}"
                
                if st.button(
                    label,
                    key=button_key,
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state["current_view"] = "docs"
                    st.session_state["selected_file"] = filename
                    st.rerun()
        else:
            st.info("暂无知识库文件")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">会话管理</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 新会话", key="new_session", use_container_width=True):
                clear_current_session()
                st.rerun()
        with col2:
            if st.button("🗑️ 清除历史", key="clear_history", use_container_width=True):
                if st.session_state["memory"]:
                    st.session_state["memory"].clear_history()
                    st.session_state["messages"] = []
                    st.rerun()
        
        st.markdown(
            f'<div class="session-info">会话 ID: {st.session_state["session_id"]}</div>',
            unsafe_allow_html=True,
        )
        
        sessions = MemoryManager.list_sessions()
        if len(sessions) > 1:
            st.selectbox(
                "切换历史会话",
                options=sessions,
                index=sessions.index(st.session_state["session_id"]) if st.session_state["session_id"] in sessions else 0,
                key="session_selector",
                on_change=lambda: switch_session(st.session_state["session_selector"]),
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
<div class="app-header">
    <div class="app-title">🤖 智扫通机器人智能客服</div>
    <div class="app-subtitle">您的扫地机器人专属智能助手</div>
</div>
""", unsafe_allow_html=True)
    
    if st.session_state["current_view"] == "chat":
        if (
            st.session_state["memory"] is None
            or st.session_state["memory"].session_id != st.session_state["session_id"]
        ):
            st.session_state["memory"] = MemoryManager(session_id=st.session_state["session_id"])
            st.session_state["agent"] = ReactAgent(memory_manager=st.session_state["memory"])
            st.session_state["messages"] = st.session_state["memory"].get_history_messages()
        
        if st.session_state["agent"] is None:
            st.session_state["agent"] = ReactAgent(memory_manager=st.session_state["memory"])
        else:
            st.session_state["agent"].set_memory(st.session_state["memory"])
        
        for message in st.session_state["messages"]:
            st.chat_message(message["role"]).write(message["content"])
        
        prompt = st.chat_input("请输入您的问题...")
        
        if prompt:
            st.chat_message("user").write(prompt)
            st.session_state["messages"].append({"role": "user", "content": prompt})
            st.session_state["memory"].add_user_message(prompt)
            
            st.session_state["loading"] = True
            
            response_messages = []
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    for chunk in st.session_state["agent"].execute_stream(prompt):
                        response_messages.append(chunk)
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": full_response}
                    )
                    st.session_state["memory"].add_ai_message(full_response)
                    
                except Exception as e:
                    error_msg = f"抱歉，处理您的请求时出现错误：{str(e)}"
                    logger.error(f"[Agent 执行] 失败：{str(e)}")
                    message_placeholder.markdown(error_msg)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": error_msg}
                    )
                finally:
                    st.session_state["loading"] = False
            
            st.rerun()
    
    else:
        if st.session_state.get("selected_file"):
            filename = st.session_state["selected_file"]
            display_name = filename.replace(".txt", "").replace(".pdf", "")
            
            content, extra_info = read_file_content(filename)
            
            if content and "读取文件失败" not in content:
                st.markdown(
                    f'<div class="doc-page-title">{get_file_icon(filename)} {display_name}</div>',
                    unsafe_allow_html=True,
                )
                
                if filename.endswith(".pdf") and extra_info:
                    st.markdown(
                        f'<div class="pdf-info">📄 PDF 文件，共 {extra_info} 页</div>',
                        unsafe_allow_html=True,
                    )
                
                st.markdown('<div class="doc-content">', unsafe_allow_html=True)
                md_content = text_to_markdown(content)
                st.markdown(md_content)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(content)
        else:
            st.info("👈 请从左侧选择一个文档查看")
