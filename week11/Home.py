"""Home.py - Multi-Domain Intelligence Platform with OOP"""

import sys
from pathlib import Path
import streamlit as st

# ============================================================
# Path setup
# ============================================================
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
# OOP Imports
# ============================================================
from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="🔐",
    layout="centered"
)

# ============================================================
# Initialize Services
# ============================================================
@st.cache_resource
def get_services():
    """Initialize and cache database and auth services."""
    db_path = ROOT / "database" / "platform.db"

    if not db_path.exists():
        st.error(f"❌ Database file not found at: {db_path}")
        st.stop()

    db = DatabaseManager(str(db_path))
    db.connect()
    auth = AuthManager(db)
    return db, auth

db_manager, auth_manager = get_services()

# ============================================================
# Session state
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ============================================================
# Helper function
# ============================================================
def role_message(role: str) -> str:
    """Return a role-specific welcome message."""
    return {
        "admin": "👑 You have full administrative access.",
        "data_analyst": "📊 You can analyze and manage datasets.",
        "user": "👤 You have standard platform access."
    }.get(role, "")

# ============================================================
# Styling
# ============================================================
st.markdown("""
<style>
.big-title {
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
}
.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}
.welcome-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header
# ============================================================
st.markdown('<h1 class="big-title">🔐 Intelligence Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Secure role-based access system</p>', unsafe_allow_html=True)

# ============================================================
# Logged-in view
# ============================================================
if st.session_state.logged_in:
    st.markdown(f"""
        <div class="welcome-box">
            <h2>👋 Welcome, {st.session_state.username}!</h2>
            <p style="margin-top: 0.5rem; opacity: 0.9;">
                {role_message(st.session_state.role)}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.success("✅ Logged in successfully")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### 🚀 Dashboards")

        if st.button("🛡️ Cybersecurity Dashboard", use_container_width=True):
            st.switch_page("pages/1_Cybersecurity.py")

        if st.button("📊 Data Science Dashboard", use_container_width=True):
            st.switch_page("pages/2_Datascience.py")

        if st.button("💻 IT Operations Dashboard", use_container_width=True):
            st.switch_page("pages/3_IT.py")

        if st.button("🤖 AI Assistant", use_container_width=True):
            st.switch_page("pages/4_AI.py")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.current_user = None
            st.rerun()

    st.stop()

# ============================================================
# Auth tabs
# ============================================================
st.divider()
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# -------------------- LOGIN --------------------
with tab_login:
    st.markdown("### Sign in to your account")

    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        submitted = st.form_submit_button("🚀 Login", use_container_width=True)

        if submitted:
            # Use AuthManager to login (returns User object or None)
            user = auth_manager.login_user(username, password)

            if user is not None:
                st.session_state.logged_in = True
                st.session_state.username = user.get_username()
                st.session_state.role = user.get_role()
                st.session_state.current_user = user
                st.success("✅ Login successful")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

# -------------------- REGISTER --------------------
with tab_register:
    st.markdown("### Create a new account")

    with st.form("register_form", clear_on_submit=True):
        new_user = st.text_input("👤 Username")
        pw = st.text_input("🔒 Password", type="password")
        confirm_pw = st.text_input("🔒 Confirm Password", type="password")

        role = st.selectbox(
            "👔 Select Role",
            ["user", "data_analyst", "admin"]
        )

        if pw:
            strength = auth_manager.check_password_strength(pw)
            if strength == "Strong":
                st.success(f"Password Strength: 💪 {strength}")
            elif strength == "Medium":
                st.warning(f"Password Strength: 😐 {strength}")
            else:
                st.error(f"Password Strength: 😟 {strength}")

        submitted = st.form_submit_button("✨ Create Account", use_container_width=True)

        if submitted:
            # Validate username using AuthManager
            ok, msg = auth_manager.validate_username(new_user)
            if not ok:
                st.error(msg)
                st.stop()

            # Validate password using AuthManager
            ok, msg = auth_manager.validate_password(pw)
            if not ok:
                st.error(msg)
                st.stop()

            # Check password match
            if pw != confirm_pw:
                st.error("Passwords do not match")
                st.stop()

            # Register user using AuthManager
            if auth_manager.register_user(new_user, pw, role):
                st.success(f"✅ Account created for **{new_user}**")
                st.info("👉 Switch to Login tab to sign in")
                st.balloons()
            else:
                st.error("❌ Username already exists")

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#888;'>🔒 Secure authentication using bcrypt</p>",
    unsafe_allow_html=True
)
