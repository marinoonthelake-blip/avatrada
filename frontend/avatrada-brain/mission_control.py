import sys, os, uuid, streamlit as st
import google.genai as genai
from dotenv import load_dotenv

# Pathing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.logger import get_logger
from services.chat_manager import get_chat_manager
from services.knowledge_engine import get_knowledge
from services.chat_behavior import get_chat_behavior
from components.sidebar import render_sidebar

load_dotenv(os.path.join(os.getcwd(), '.env'))

# --- KEY DISCOVERY SYSTEM ---
def get_key_vault():
    vault = {}
    # 1. Check Standard Key (if set)
    std = os.environ.get("GOOGLE_API_KEY")
    if std: vault[f"Primary (..{std[-4:]})"] = std
    
    # 2. Check Numbered Keys in .env
    for k, v in os.environ.items():
        if k.startswith("GOOGLE_API_KEY_") and v:
            label = f"{k.replace('GOOGLE_API_KEY_', 'Key ')} (..{v[-4:]})"
            vault[label] = v
    return vault

# --- UPDATED HIERARCHY (v6.4.1) ---
MODEL_HIERARCHY = {
    "Model 3.0 Pro Preview": ["gemini-3-pro-preview", "gemini-exp-1206"],
    "Model 2.5 Pro": ["gemini-2.5-pro"],
    "Gemini Pro Latest": ["models/gemini-pro-latest"],  # <--- NEW ADDITION
    "Model 3 Flash Preview": ["gemini-3-flash-preview", "gemini-2.0-flash-exp"]
}

st.set_page_config(page_title="Avatrada v6.4.1", layout="wide")

# Session State Init
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_title" not in st.session_state: st.session_state.chat_title = "New Conversation"
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "edit_prompt" not in st.session_state: st.session_state.edit_prompt = "" 
if "stop_gen" not in st.session_state: st.session_state.stop_gen = False

logger, cm, ke = get_logger(), get_chat_manager(), get_knowledge()

# --- SIDEBAR: KEY SELECTION ---
with st.sidebar:
    st.header("🔑 Neural Link")
    vault = get_key_vault()
    if not vault:
        st.error("No API Keys found in .env!")
        st.stop()
        
    default_idx = 1 if len(vault) > 1 else 0
    selected_label = st.selectbox("Active API Key", options=list(vault.keys()), index=default_idx)
    ACTIVE_KEY = vault[selected_label]

    if "active_key_label" not in st.session_state:
        st.session_state.active_key_label = selected_label
    elif st.session_state.active_key_label != selected_label:
        st.toast(f"Switched to {selected_label}")
        st.session_state.active_key_label = selected_label

# Initialize Chat with selected key
chat_ops = get_chat_behavior(ACTIVE_KEY, MODEL_HIERARCHY)

instr, doct, lib, cnts = ke.load_context()
selected_tier = render_sidebar("6.4.1", cm, logger, cnts, MODEL_HIERARCHY)

st.title(f"💎 {st.session_state.chat_title}")
chat_placeholder = st.container(height=600)

# 1. RENDER HISTORY
with chat_placeholder:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user" and i == len(st.session_state.messages) - 2:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    parts = msg["content"] if isinstance(msg["content"], list) else [msg["content"]]
                    full_text = ""
                    for p in parts:
                        if isinstance(p, str) and p.startswith("data:image"):
                            if full_text: st.markdown(full_text); full_text = ""
                            st.image(p)
                        else: full_text += str(p) + "\n"
                    if full_text: st.markdown(full_text)
                with col2:
                    if st.button("✏️", key=f"edit_{i}", help="Edit this command"):
                        st.session_state.edit_prompt = full_text.strip()
                        st.session_state.messages = st.session_state.messages[:i]
                        st.rerun()
            else:
                parts = msg["content"] if isinstance(msg["content"], list) else [msg["content"]]
                full_text = ""
                for p in parts:
                    if isinstance(p, str) and p.startswith("data:image"):
                        if full_text: st.markdown(full_text); full_text = ""
                        st.image(p)
                    else: full_text += str(p) + "\n"
                if full_text: st.markdown(full_text)

# 2. INPUT AREA
with st._bottom:
    cols = st.columns([0.85, 0.15])
    with cols[0]:
        default_text = st.session_state.edit_prompt
        if st.session_state.edit_prompt: st.session_state.edit_prompt = ""
        prompt = st.chat_input("Command...", key="main_input") or default_text
        
    with cols[1]:
        files = st.file_uploader("📎", type=['png', 'jpg', 'jpeg', 'pdf'], key=f"up_{st.session_state.uploader_key}", label_visibility="collapsed")

    if prompt:
        if not st.session_state.messages:
            st.session_state.chat_title = prompt[:30]
            st.session_state.current_chat_id = str(uuid.uuid4())
            
        user_msg = [prompt]
        if files:
            if files.type == "application/pdf":
                user_msg.append(f"UPLOADED DOCTRINE: {files.name}")
            else:
                img_b64 = chat_ops.process_image_to_b64(files)
                if img_b64: user_msg.append(img_b64)
            st.session_state.uploader_key += 1
            
        st.session_state.messages.append({"role": "user", "content": user_msg})
        st.rerun()

# 3. EXECUTION LOGIC
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with chat_placeholder:
        with st.chat_message("assistant"):
            with st.spinner(f"🧠 {selected_tier} is thinking..."):
                contents = chat_ops.prepare_recall_payload(st.session_state.messages)
                try:
                    ans = chat_ops.execute_with_fallback(selected_tier, contents, instr, doct, lib, logger)
                    
                    if ans:
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": [str(ans)]})
                        cm.save_chat(st.session_state.current_chat_id, st.session_state.chat_title, st.session_state.messages)
                        st.rerun()
                    else:
                        st.error("❌ Model returned no response.")
                        st.warning("💡 Try switching keys in the 'Neural Link' sidebar dropdown!")
                        
                except Exception as e:
                    st.error(f"❌ System Error: {e}")
