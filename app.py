import streamlit as st
from agent.react_agent import ReactAgent
import os
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_conf
import re

st.set_page_config(
    page_title="智扫通 - 机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0078D4 0%, #00BCF2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .divider-custom {
        height: 2px;
        background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
        border: none;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        border-radius: 12px !important;
    }
    .sidebar-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.8rem;
        padding-left: 0.5rem;
    }
    .file-nav-item {
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 0.95rem;
        color: #374151;
        border: none;
        background: transparent;
        text-align: left;
        width: 100%;
    }
    .file-nav-item:hover {
        background-color: #F3F4F6;
        color: #111827;
    }
    .file-nav-item.active {
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
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
    .nav-tab {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
        cursor: pointer;
    }
    .nav-tab.active {
        background-color: #0078D4;
        color: white;
    }
    .nav-tab:not(.active) {
        background-color: #F3F4F6;
        color: #374151;
    }
    .nav-tab:hover:not(.active) {
        background-color: #E5E7EB;
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

def read_file_content(filename):
    data_path = get_abs_path(chroma_conf["data_path"])
    file_path = os.path.join(data_path, filename)
    try:
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif filename.endswith('.pdf'):
            return "📄 PDF 文件预览功能开发中..."
    except Exception as e:
        return f"读取文件失败: {str(e)}"
    return ""

def text_to_markdown(text):
    lines = text.split('\n')
    processed = []
    for line in lines:
        line = line.rstrip()
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

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "chat"

col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
with col1:
    if st.button("💬 智能客服", use_container_width=True, type="primary" if st.session_state["current_page"] == "chat" else "secondary"):
        st.session_state["current_page"] = "chat"
        st.rerun()
with col2:
    if st.button("📚 产品知识库", use_container_width=True, type="primary" if st.session_state["current_page"] == "docs" else "secondary"):
        st.session_state["current_page"] = "docs"
        st.rerun()

st.markdown('<hr class="divider-custom">', unsafe_allow_html=True)

knowledge_files = get_knowledge_files()

if st.session_state["current_page"] == "chat":
    st.markdown('<h1 class="main-title">🤖 智扫通机器人智能客服</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">您的扫地机器人专属智能助手</p>', unsafe_allow_html=True)
    
    if "agent" not in st.session_state:
        st.session_state["agent"] = ReactAgent()
    
    if "message" not in st.session_state:
        st.session_state["message"] = []
    
    for message in st.session_state["message"]:
        st.chat_message(message["role"]).write(message["content"])
    
    prompt = st.chat_input("请输入您的问题...")
    
    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["message"].append({"role": "user", "content": prompt})
        
        response_messages = []
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            for chunk in st.session_state["agent"].execute_stream(prompt):
                response_messages.append(chunk)
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        st.session_state["message"].append({"role": "assistant", "content": full_response})
        st.rerun()

else:
    st.markdown('<h1 class="main-title">📚 产品知识库</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">查看扫地机器人产品相关文档</p>', unsafe_allow_html=True)
    
    if "selected_file" not in st.session_state and knowledge_files:
        st.session_state["selected_file"] = knowledge_files[0]
    
    with st.sidebar:
        st.markdown('<div class="sidebar-header">文档列表</div>', unsafe_allow_html=True)
        
        if knowledge_files:
            for filename in knowledge_files:
                is_selected = st.session_state.get("selected_file") == filename
                button_key = f"file_{filename}"
                
                label = f"{get_file_icon(filename)} {filename.replace('.txt', '').replace('.pdf', '')}"
                
                if st.button(
                    label,
                    key=button_key,
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state["selected_file"] = filename
                    st.rerun()
        else:
            st.info("暂无知识库文件")
    
    if st.session_state.get("selected_file"):
        filename = st.session_state["selected_file"]
        display_name = filename.replace('.txt', '').replace('.pdf', '')
        
        content = read_file_content(filename)
        
        if content and "PDF 文件预览功能开发中" not in content:
            st.markdown(f"### {get_file_icon(filename)} {display_name}")
            st.markdown('<div class="doc-content">', unsafe_allow_html=True)
            md_content = text_to_markdown(content)
            st.markdown(md_content)
            st.markdown('</div>', unsafe_allow_html=True)
        elif "PDF 文件预览功能开发中" in content:
            st.info(content)
    else:
        st.info("👈 请从左侧选择一个文档查看")
