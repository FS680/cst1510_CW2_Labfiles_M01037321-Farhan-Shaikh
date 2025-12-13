import sys
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ============================================================
# Path setup
# ============================================================
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


APP_ROOT = Path(__file__).resolve().parent.parent  # points to app/
load_dotenv(APP_ROOT / ".env")  # ensure exact path


API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ OPENAI_API_KEY not found in .env")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

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

SYSTEM_PROMPTS = {
    "Cybersecurity": """You are a cybersecurity expert assistant.
Analyze incidents, threats, vulnerabilities, and provide technical guidance.""",

    "Data Science": """You are a data science expert assistant.
Help with data analysis, visualization strategies, and statistical insights.""",

    "IT Operations": """You are an IT operations expert assistant.
Help troubleshoot issues, optimize systems, and manage tickets."""
}

system_prompt = SYSTEM_PROMPTS[domain]

# ============================================================
# Clear Chat
# ============================================================
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# ============================================================
# Chat Session State
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# If domain changes → reset system prompt
if st.session_state.messages[0]["content"] != system_prompt:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# ============================================================
# Page UI
# ============================================================
st.title("🤖 AI Assistant")
st.caption(f"Domain: **{domain}** | Model: **GPT-4.1-mini**")

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# User Input
# ============================================================
user_input = st.chat_input("Ask something...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=st.session_state.messages,
                temperature=0.4
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
