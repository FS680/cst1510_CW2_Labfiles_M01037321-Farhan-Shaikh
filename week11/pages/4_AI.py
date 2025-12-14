"""AI Assistant Dashboard - Refactored with OOP."""

import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import os

# ============================================================
# Path setup
# ============================================================
from pathlib import Path
from services.database_manager import DatabaseManager

# Absolute path to week11 root
ROOT = Path(__file__).resolve().parent.parent  # pages/ -> week11/

# Full path to DB
DB_PATH = ROOT / "database" / "platform.db"

# Connect DB
db = DatabaseManager(str(DB_PATH))


# ============================================================
# Load environment variables
# ============================================================
# Load from week11/.streamlit/.env
ENV_PATH = ROOT / ".streamlit" / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ OPENAI_API_KEY not found in .env")
    st.stop()

# ============================================================
# OOP Imports
# ============================================================
from services.ai_assistant import AIAssistant

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# Domain System Prompts
# ============================================================
SYSTEM_PROMPTS = {
    "Cybersecurity": """You are a cybersecurity expert assistant.
Analyze incidents, threats, vulnerabilities, and provide technical guidance.""",

    "Data Science": """You are a data science expert assistant.
Help with data analysis, visualization strategies, and statistical insights.""",

    "IT Operations": """You are an IT operations expert assistant.
Help troubleshoot issues, optimize systems, and manage tickets."""
}

# ============================================================
# Sidebar – Domain Selection
# ============================================================
st.sidebar.title("🧠 AI Domain")

domain = st.sidebar.selectbox(
    "Select Expertise",
    [
        "Cybersecurity",
        "Data Science",
        "IT Operations"
    ]
)

# ============================================================
# Initialize AI Assistant (Using OOP)
# ============================================================
# Initialize AI assistants in session state (one per domain)
if "ai_assistants" not in st.session_state:
    st.session_state.ai_assistants = {}
    for dom in ["Cybersecurity", "Data Science", "IT Operations"]:
        assistant = AIAssistant(
            api_key=API_KEY,
            domain=dom,
            model="gpt-4.1-mini"
        )
        st.session_state.ai_assistants[dom] = assistant

# Get current assistant based on selected domain
assistant = st.session_state.ai_assistants[domain]

# ============================================================
# Clear Chat
# ============================================================
if st.sidebar.button("🧹 Clear Chat"):
    assistant.clear_history()
    st.rerun()

# ============================================================
# Page UI
# ============================================================
st.title("🤖 AI Assistant")
st.caption(f"Domain: **{domain}** | Model: **GPT-4 Turbo**")

# ============================================================
# Display Chat History (Using Object Methods)
# ============================================================
# Get chat history from assistant (excluding system message)
chat_history = assistant.get_history()

for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# User Input
# ============================================================
user_input = st.chat_input("Ask something...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response using AIAssistant service
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Use AIAssistant's send_message method
                reply = assistant.send_message(user_input, temperature=0.4)
                st.markdown(reply)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()

    # Rerun to update chat display
    st.rerun()
