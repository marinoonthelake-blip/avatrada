import streamlit as st
import os
import glob
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

# --- 1. CONFIG & SECRETS ---
load_dotenv()
st.set_page_config(page_title="Avatrada Mission Control", layout="wide", page_icon="💎")

API_KEY = os.environ.get("GEMINI_API_KEY")
LIBRARY_DIR = "library/markdown"
DOCTRINE_DIR = "doctrines"
INSTRUCTIONS_DIR = "system_instructions"

# --- 2. DATA LOADERS ---
def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".md":
            with open(filepath, "r") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            return f"[Unsupported Format: {ext}]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

@st.cache_resource
def load_data():
    # A. Load System Instructions (Modular SOPs)
    instructions_text = ""
    # We sort strictly by filename so you can control order (01_..., 02_...)
    i_files = sorted(glob.glob(os.path.join(os.getcwd(), INSTRUCTIONS_DIR, "*.md")))
    for f in i_files:
        with open(f, "r") as file:
            instructions_text += f"\n\n--- SOP: {os.path.basename(f)} ---\n{file.read()}"

    # B. Load Doctrines (Laws)
    doctrines_text = ""
    d_files = sorted(
        glob.glob(os.path.join(os.getcwd(), DOCTRINE_DIR, "*.pdf")) + 
        glob.glob(os.path.join(os.getcwd(), DOCTRINE_DIR, "*.md"))
    )
    for f in d_files:
        content = extract_text(f)
        doctrines_text += f"\n\n--- DOCTRINE (LAW): {os.path.basename(f)} ---\n{content}"

    # C. Load Library (Knowledge)
    library_text = ""
    l_files = sorted(glob.glob(os.path.join(os.getcwd(), LIBRARY_DIR, "*.md")))
    for f in l_files:
        with open(f, "r") as file:
            library_text += f"\n\n--- REF: {os.path.basename(f)} ---\n{file.read()}"
            
    return instructions_text, doctrines_text, library_text, len(i_files), len(d_files), len(l_files)

instructions, doctrines, library, i_count, d_count, l_count = load_data()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🧠 Neural Config")
    
    selected_model = st.selectbox(
        "Active Model",
        options=[
            "models/gemini-3-pro-preview",
            "models/gemini-3-pro",
            "models/gemini-2.5-pro",
            "models/gemini-pro-latest",
        ],
        index=0
    )
    
    temperature = st.slider("Creativity", 0.0, 1.0, 0.2)
    
    st.divider()
    if d_count > 0:
        st.success(f"📜 **{d_count} Doctrines** Active")
    else:
        st.warning("⚠️ No Doctrines Found")
        
    st.info(f"⚡ **{i_count} SOP Modules** Active")
    st.info(f"📚 **{l_count} Papers** Indexed")
    
    if st.button("🔄 Reload All"):
        st.cache_resource.clear()
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. SAFETY ---
if not API_KEY:
    st.error("❌ GEMINI_API_KEY is missing. Check .env")
    st.stop()

# --- 5. SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = f"""
You are the **Chief Architect of Avatrada**.
You are running on **{selected_model}**.

=== SECTION 1: OPERATIONAL PROTOCOLS (MUST FOLLOW) ===
{instructions}

=== SECTION 2: CORE DOCTRINES (NON-NEGOTIABLE LAW) ===
{doctrines}

=== SECTION 3: RESEARCH LIBRARY (REFERENCE KNOWLEDGE) ===
{library}
"""

# --- 6. CHAT ENGINE ---
client = genai.Client(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💎 Avatrada Mission Control")
st.caption(f"Governance: {d_count} Doctrines | SOP: {i_count} Modules | Engine: {selected_model}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Command the {selected_model} Architect..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        msg_box = st.empty()
        msg_box.markdown("`Consulting Protocols & Doctrines...`")
        
        try:
            history = [
                types.Content(
                    role="model" if m["role"] == "assistant" else "user",
                    parts=[types.Part(text=m["content"])]
                ) for m in st.session_state.messages[:-1]
            ]

            chat = client.chats.create(
                model=selected_model,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=temperature
                ),
                history=history
            )
            
            response = chat.send_message(prompt)
            msg_box.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            msg_box.error(f"Error: {e}")
