import streamlit as st

def render_sidebar(version, cm, logger, knowledge_counts, model_hierarchy):
    with st.sidebar:
        st.title("🧠 Neural Config")
        st.caption(f"Build: {version}")
        selected_tier = st.selectbox("Intelligence Tier", options=list(model_hierarchy.keys()))
        
        if "doctrine_lock" not in st.session_state: st.session_state.doctrine_lock = True
        st.session_state.doctrine_lock = st.toggle("🔒 Doctrine Lock", value=st.session_state.doctrine_lock)
        
        if st.button("➕ New Session", use_container_width=True):
            st.session_state.messages, st.session_state.chat_title, st.session_state.current_chat_id = [], "New Conversation", None
            st.rerun()

        st.divider()
        st.subheader("📁 Saved Chats")
        if st.session_state.current_chat_id:
            new_title = st.text_input("Rename Current Session", value=st.session_state.chat_title)
            if new_title != st.session_state.chat_title:
                cm.rename_chat(st.session_state.current_chat_id, new_title)
                st.session_state.chat_title = new_title
                st.rerun()

        saved_chats = cm.list_chats()
        for chat in saved_chats:
            col1, col2 = st.columns([0.8, 0.2])
            if col1.button(f"💬 {chat['title'][:18]}", key=f"c_{chat['id']}", use_container_width=True):
                data = cm.load_chat(chat['id'])
                st.session_state.current_chat_id, st.session_state.messages, st.session_state.chat_title = data['id'], data['messages'], data['title']
                st.session_state.just_loaded = True 
                st.rerun()
            if col2.button("🗑️", key=f"d_{chat['id']}"):
                cm.delete_chat(chat['id'])
                st.rerun()

        st.divider()
        st.success(f"📜 {knowledge_counts.get('doctrines', 0)} Doctrines")
        st.info(f"📚 {knowledge_counts.get('library', 0)} Library Papers")
        st.warning(f"🗺️ {knowledge_counts.get('states', 0)} State Maps")
    return selected_tier
