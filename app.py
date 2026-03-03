import streamlit as st
from agent.react_agent import ReactAgent
import os
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_conf

st.set_page_config(
    page_title="智扫通 - 机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0078D4 0%, #00BCF2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .divider-custom {
        height: 3px;
        background: linear-gradient(90deg, transparent, #0078D4, transparent);
        border: none;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        border-radius: 12px !important;
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0078D4;
        margin-bottom: 1rem;
    }
    .file-item {
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .file-item:hover {
        background-color: #E8F4FD;
    }
    .file-item.selected {
        background-color: #D0E8FF;
        font-weight: 600;
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

with st.sidebar:
    st.markdown('<p class="sidebar-title">📚 产品知识库</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    knowledge_files = get_knowledge_files()
    
    if knowledge_files:
        if "selected_file" not in st.session_state:
            st.session_state["selected_file"] = None
        
        st.markdown("**选择文件查看:**")
        for filename in knowledge_files:
            is_selected = st.session_state.get("selected_file") == filename
            button_key = f"file_{filename}"
            
            if st.button(
                f"📄 {filename}",
                key=button_key,
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state["selected_file"] = filename
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get("selected_file"):
            st.markdown(f"**📖 当前查看:** {st.session_state['selected_file']}")
    else:
        st.info("暂无知识库文件")

st.markdown('<h1 class="main-title">🤖 智扫通机器人智能客服</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">您的扫地机器人专属智能助手</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider-custom">', unsafe_allow_html=True)

if st.session_state.get("selected_file"):
    with st.expander(f"📖 查看: {st.session_state['selected_file']}", expanded=True):
        content = read_file_content(st.session_state["selected_file"])
        st.text_area("", content, height=400, disabled=True)
    st.markdown("---")

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
