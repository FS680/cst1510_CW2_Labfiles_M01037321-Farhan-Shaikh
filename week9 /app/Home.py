import sys
from pathlib import Path
import hashlib
import streamlit as st

# ============================================================
# Path setup
# ============================================================
ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

APP_ROOT = ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# ============================================================
# Imports
# ============================================================
from db.users import get_user_by_username, insert_user

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)

# ============================================================
# Helper functions
# ============================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_username(username: str):
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not username.isalnum():
        return False, "Username must contain only letters and numbers"
    return True, ""


def validate_password(password: str):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""


def check_password_strength(password: str) -> str:
    score = sum([
        len(password) >= 8,
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in "!@#$%^&*" for c in password)
    ])
    if score == 4:
        return "💪 Strong"
    elif score >= 2:
        return "😐 Medium"
    return "😟 Weak"


def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if user and user[2] == hash_password(password):
        return True, user[3]  # role
    return False, None


def register_user(username: str, password: str, role: str):
    try:
        insert_user(username, hash_password(password), role)
        return True
    except:
        return False


def role_message(role: str) -> str:
    return {
        "admin": "👑 You have full administrative access.",
        "data_analyst": "📊 You can analyze and manage datasets.",
        "user": "👤 You have standard platform access."
    }.get(role, "")

# ============================================================
# Session state
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

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
            st.switch_page("pages/cybersecurity.py")

        if st.button("📊 Data Science Dashboard", use_container_width=True):
            st.switch_page("pages/data_science.py")

        if st.button("💻 IT Operations Dashboard", use_container_width=True):
            st.switch_page("pages/it_operations.py")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
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
            success, role = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
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
            strength = check_password_strength(pw)
            if "Strong" in strength:
                st.success(f"Password Strength: {strength}")
            elif "Medium" in strength:
                st.warning(f"Password Strength: {strength}")
            else:
                st.error(f"Password Strength: {strength}")

        submitted = st.form_submit_button("✨ Create Account", use_container_width=True)

        if submitted:
            ok, msg = validate_username(new_user)
            if not ok:
                st.error(msg)
                st.stop()

            ok, msg = validate_password(pw)
            if not ok:
                st.error(msg)
                st.stop()

            if pw != confirm_pw:
                st.error("Passwords do not match")
                st.stop()

            if register_user(new_user, pw, role):
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
    "<p style='text-align:center;color:#888;'>🔒 Secure authentication using SHA-256</p>",
    unsafe_allow_html=True
)
