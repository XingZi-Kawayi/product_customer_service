import streamlit as st
from agent.react_agent import ReactAgent
from memory.memory_manager import MemoryManager
import os
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_conf
import re
from pypdf import PdfReader

st.set_page_config(
    page_title="智扫通 - 机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .memory-button {
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        border: 1px solid #E5E7EB;
        background: white;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .memory-button:hover {
        background-color: #F3F4F6;
        border-color: #D1D5DB;
    }
    .memory-button.danger {
        border-color: #FECACA;
        color: #DC2626;
    }
    .memory-button.danger:hover {
        background-color: #FEE2E2;
    }
</style>
""", unsafe_allow_html=True)

def get_knowledge_files():
    data_path = get_abs_path(chroma_conf["data_path"])
    allowed_types = tuple(chroma_conf["allow_knowledge_file_type"])
    files = []
    if os.path.exists(data_path):
        for filename in os.listdir(data_path):
            if filename.endswith(allowed_types):
                files.append(filename)
    return sorted(files)

def read_pdf_content(filepath):
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
        return f"读取 PDF 文件失败: {str(e)}", 0

def read_file_content(filename):
    data_path = get_abs_path(chroma_conf["data_path"])
    file_path = os.path.join(data_path, filename)
    try:
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), None
        elif filename.endswith('.pdf'):
            return read_pdf_content(file_path)
    except Exception as e:
        return f"读取文件失败: {str(e)}", None
    return "", None

def text_to_markdown(text):
    lines = text.split('\n')
    processed = []
    for line in lines:
        line = line.rstrip()
        if re.match(r'^---\s*第\s*\d+\s*页\s*---$', line):
            continue
        if re.match(r'^#{1,6}\s', line):
            processed.append(line)
        elif re.match(r'^\s*[0-9]+\.\s', line):
            processed.append(line)
        elif re.match(r'^\s*[*-]\s', line):
            processed.append(line)
        elif line.strip() and not line.startswith(' '):
            processed.append(line)
        else:
            processed.append(line)
    return '\n'.join(processed)

def get_file_icon(filename):
    if '故障' in filename or '排除' in filename:
        return '🔧'
    elif '保养' in filename or '维护' in filename:
        return '✨'
    elif '选购' in filename or '指南' in filename:
        return '📋'
    elif '100问' in filename:
        return '❓'
    elif '.pdf' in filename:
        return '📄'
    else:
        return '📄'

if "current_view" not in st.session_state:
    st.session_state["current_view"] = "chat"

if "selected_file" not in st.session_state:
    st.session_state["selected_file"] = None

if "session_id" not in st.session_state:
    st.session_state["session_id"] = "default"

if "memory_enabled" not in st.session_state:
    st.session_state["memory_enabled"] = True

knowledge_files = get_knowledge_files()

with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    
    if st.button(
        "💬 智能客服",
        key="nav_chat",
        use_container_width=True,
        type="primary" if st.session_state["current_view"] == "chat" else "secondary"
    ):
        st.session_state["current_view"] = "chat"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">产品知识库</div>', unsafe_allow_html=True)
    
    if knowledge_files:
        for filename in knowledge_files:
            is_selected = st.session_state["current_view"] == "docs" and st.session_state.get("selected_file") == filename
            button_key = f"file_{filename}"
            
            label = f"{get_file_icon(filename)} {filename.replace('.txt', '').replace('.pdf', '')}"
            
            if st.button(
                label,
                key=button_key,
                use_container_width=True,
                type="secondary"
            ):
                st.session_state["current_view"] = "docs"
                st.session_state["selected_file"] = filename
                st.rerun()
    else:
        st.info("暂无知识库文件")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">对话记忆</div>', unsafe_allow_html=True)
    
    st.session_state["memory_enabled"] = st.checkbox(
        "启用对话记忆",
        value=st.session_state["memory_enabled"]
    )
    
    sessions = MemoryManager.list_sessions()
    if sessions:
        st.selectbox(
            "选择会话",
            options=sessions,
            index=sessions.index(st.session_state["session_id"]) if st.session_state["session_id"] in sessions else 0,
            key="session_id"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 新会话", use_container_width=True):
            import uuid
            st.session_state["session_id"] = f"session_{uuid.uuid4().hex[:8]}"
            st.rerun()
    
    with col2:
        if st.button("🗑️ 清空历史", use_container_width=True, type="secondary"):
            MemoryManager.delete_session(st.session_state["session_id"])
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <div class="app-title">🤖 智扫通机器人智能客服</div>
    <div class="app-subtitle">您的扫地机器人专属智能助手</div>
</div>
""", unsafe_allow_html=True)

if st.session_state["current_view"] == "chat":
    if "memory" not in st.session_state or st.session_state["memory"].session_id != st.session_state["session_id"]:
        st.session_state["memory"] = MemoryManager(session_id=st.session_state["session_id"])
    
    if "agent" not in st.session_state:
        st.session_state["agent"] = ReactAgent(memory_manager=st.session_state["memory"])
    else:
        st.session_state["agent"].set_memory(st.session_state["memory"])
    
    if "message" not in st.session_state:
        st.session_state["message"] = st.session_state["memory"].get_history_messages()
    
    for message in st.session_state["message"]:
        st.chat_message(message["role"]).write(message["content"])
    
    prompt = st.chat_input("请输入您的问题...")
    
    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["message"].append({"role": "user", "content": prompt})
        
        if st.session_state["memory_enabled"]:
            st.session_state["memory"].add_user_message(prompt)
        
        response_messages = []
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            for chunk in st.session_state["agent"].execute_stream(prompt, use_memory=st.session_state["memory_enabled"]):
                response_messages.append(chunk)
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        st.session_state["message"].append({"role": "assistant", "content": full_response})
        
        if st.session_state["memory_enabled"]:
            st.session_state["memory"].add_ai_message(full_response)
        
        st.rerun()

else:
    if st.session_state.get("selected_file"):
        filename = st.session_state["selected_file"]
        display_name = filename.replace('.txt', '').replace('.pdf', '')
        
        content, extra_info = read_file_content(filename)
        
        if content and "读取文件失败" not in content:
            st.markdown(f'<div class="doc-page-title">{get_file_icon(filename)} {display_name}</div>', unsafe_allow_html=True)
            
            if filename.endswith('.pdf') and extra_info:
                st.markdown(f'<div class="pdf-info">📄 PDF 文件，共 {extra_info} 页</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="doc-content">', unsafe_allow_html=True)
            md_content = text_to_markdown(content)
            st.markdown(md_content)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error(content)
    else:
        st.info("👈 请从左侧选择一个文档查看")
