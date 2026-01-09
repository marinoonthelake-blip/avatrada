import streamlit as st
from datetime import datetime

class AvatradaLogger:
    def __init__(self):
        if "logs" not in st.session_state:
            st.session_state.logs = []

    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {"time": timestamp, "level": level, "message": message}
        st.session_state.logs = [entry] + st.session_state.logs[:49]

    def info(self, msg): self.log("INFO", msg)
    def success(self, msg): self.log("SUCCESS", msg)
    def warning(self, msg): self.log("WARNING", msg)
    def error(self, msg): self.log("ERROR", msg)
    def trigger(self, msg): self.log("TRIGGER", msg)

def get_logger():
    return AvatradaLogger()
