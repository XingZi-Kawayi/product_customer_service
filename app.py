import streamlit as st
from agent.react_agent import ReactAgent

st.set_page_config(
    page_title="智扫通 - 机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🤖 智扫通机器人智能客服</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">您的扫地机器人专属智能助手</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider-custom">', unsafe_allow_html=True)

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
