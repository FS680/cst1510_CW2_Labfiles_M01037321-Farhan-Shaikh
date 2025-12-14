import sys
from pathlib import Path
from datetime import datetime
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
# OOP Imports
# ============================================================
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ============================================================
# Auth check
# ============================================================
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

# ============================================================
# Initialize Services
# ============================================================
@st.cache_resource
def get_database():
    """Initialize and cache database service."""
    db = DatabaseManager(str(ROOT / "database" / "platform.db"))
    db.connect()
    return db

db_manager = get_database()

# ============================================================
# Data Retrieval Functions (Using OOP)
# ============================================================
def get_all_incidents() -> list[SecurityIncident]:
    """Fetch all incidents and convert to SecurityIncident objects."""
    # Check which table exists (security_incidents or cyber_incidents)
    try:
        rows = db_manager.fetch_all(
            "SELECT id, date, incident_type, severity, status, description, reported_by FROM security_incidents"
        )
    except:
        # Try alternate table name
        rows = db_manager.fetch_all(
            "SELECT id, date, incident_type, severity, status, description, reported_by FROM cyber_incidents"
        )

    incidents = []
    for row in rows:
        incident = SecurityIncident(
            incident_id=row["id"],
            date=row["date"],
            incident_type=row["incident_type"],
            severity=row["severity"],
            status=row["status"],
            description=row["description"],
            reported_by=row["reported_by"] if row["reported_by"] else None
        )
        incidents.append(incident)

    return incidents

def insert_incident(date: str, incident_type: str, severity: str, status: str,
                   description: str, reported_by: str) -> None:
    """Insert a new incident into the database."""
    # Try security_incidents first, fall back to cyber_incidents
    try:
        db_manager.execute_query(
            """INSERT INTO security_incidents
               (date, incident_type, severity, status, description, reported_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date, incident_type, severity, status, description, reported_by)
        )
    except:
        db_manager.execute_query(
            """INSERT INTO cyber_incidents
               (date, incident_type, severity, status, description, reported_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date, incident_type, severity, status, description, reported_by)
        )

def update_incident_status(incident_id: int, new_status: str) -> None:
    """Update the status of an incident."""
    try:
        db_manager.execute_query(
            "UPDATE security_incidents SET status = ? WHERE id = ?",
            (new_status, incident_id)
        )
    except:
        db_manager.execute_query(
            "UPDATE cyber_incidents SET status = ? WHERE id = ?",
            (new_status, incident_id)
        )

def delete_incident(incident_id: int) -> None:
    """Delete an incident from the database."""
    try:
        db_manager.execute_query(
            "DELETE FROM security_incidents WHERE id = ?",
            (incident_id,)
        )
    except:
        db_manager.execute_query(
            "DELETE FROM cyber_incidents WHERE id = ?",
            (incident_id,)
        )

# ============================================================
# Header
# ============================================================
st.markdown("""
<h1 style='text-align:center;color:#FF4B4B;'>🛡️ Cybersecurity Command Center</h1>
<p style='text-align:center;color:#666;'>Incident monitoring and response management</p>
<hr>
""", unsafe_allow_html=True)

# ============================================================
# Fetch Data using OOP
# ============================================================
incidents = get_all_incidents()

# Convert to DataFrame for visualization (we still use pandas for Plotly)
df = pd.DataFrame([
    {
        "id": inc.get_id(),
        "date": inc.get_date(),
        "incident_type": inc.get_incident_type(),
        "severity": inc.get_severity(),
        "status": inc.get_status(),
        "description": inc.get_description(),
        "reported_by": inc.get_reported_by(),
        "severity_level": inc.get_severity_level()
    }
    for inc in incidents
])

# ============================================================
# Overview Metrics
# ============================================================
st.subheader("📊 Security Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents", len(incidents))

with col2:
    critical_count = sum(1 for inc in incidents if inc.is_critical())
    st.metric("Critical Incidents", critical_count)

with col3:
    open_count = sum(1 for inc in incidents if inc.is_open())
    st.metric("Open Cases", open_count)

with col4:
    investigating = len([inc for inc in incidents if inc.get_status() == "Investigating"])
    st.metric("Under Investigation", investigating)

st.divider()

# ============================================================
# Visualizations
# ============================================================
if not df.empty:
    col1, col2 = st.columns(2)

    # -------- Severity Breakdown --------
    with col1:
        st.markdown("### ⚠️ Severity Breakdown")

        sev_counts = df["severity"].value_counts().reset_index()
        sev_counts.columns = ["severity", "count"]

        fig1 = px.pie(
            sev_counts,
            names="severity",
            values="count",
            hole=0.45
        )
        fig1.update_traces(textinfo="label+percent")
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    # -------- Status Funnel --------
    with col2:
        st.markdown("### 📊 Incident Status Flow")

        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]

        fig2 = go.Figure(go.Funnel(
            y=status_counts["status"],
            x=status_counts["count"],
            textinfo="value+percent initial"
        ))
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================================================
# Incident Table (Using Object Methods)
# ============================================================
st.subheader("🔍 Incident Records")

if incidents:
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search = st.text_input("🔎 Search incidents")

    with col2:
        severity_filter = st.selectbox("Severity", ["All"] + df["severity"].unique().tolist())

    with col3:
        status_filter = st.selectbox("Status", ["All"] + df["status"].unique().tolist())

    # Filter incidents using object methods
    filtered_incidents = incidents.copy()

    if search:
        filtered_incidents = [
            inc for inc in filtered_incidents
            if search.lower() in inc.get_incident_type().lower() or
               search.lower() in inc.get_description().lower()
        ]

    if severity_filter != "All":
        filtered_incidents = [inc for inc in filtered_incidents if inc.get_severity() == severity_filter]

    if status_filter != "All":
        filtered_incidents = [inc for inc in filtered_incidents if inc.get_status() == status_filter]

    # Convert filtered incidents to DataFrame for display
    filtered_df = pd.DataFrame([
        {
            "ID": inc.get_id(),
            "Date": inc.get_date(),
            "Type": inc.get_incident_type(),
            "Severity": inc.get_severity(),
            "Status": inc.get_status(),
            "Description": inc.get_description()[:50] + "...",
            "Reported By": inc.get_reported_by() or "N/A"
        }
        for inc in filtered_incidents
    ])

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=300
    )

    st.caption(f"Showing {len(filtered_incidents)} of {len(incidents)} incidents")
else:
    st.info("No incidents found")

st.divider()

# ============================================================
# Incident Management
# ============================================================
st.subheader("⚙️ Incident Management")

tab1, tab2, tab3 = st.tabs(["➕ Add", "✏️ Update Status", "🗑️ Delete"])

# ---------------- ADD ----------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Incident Date", datetime.now())
        incident_type = st.selectbox(
            "Incident Type",
            ["Malware", "Phishing", "DDoS", "Data Breach", "Ransomware", "Unauthorized Access", "Other"]
        )
        severity = st.select_slider("Severity", ["Low", "Medium", "High", "Critical"], "Medium")

    with col2:
        status = st.selectbox("Status", ["Open", "Investigating", "Resolved"])
        reported_by = st.text_input("Reported By", st.session_state.username)
        description = st.text_area("Description")

    if st.button("Submit Incident", use_container_width=True):
        if description:
            insert_incident(
                str(date),
                incident_type,
                severity,
                status,
                description,
                reported_by
            )
            st.success("Incident added successfully")
            st.rerun()
        else:
            st.error("Description required")

# ---------------- UPDATE ----------------
with tab2:
    if incidents:
        incident_id = st.selectbox("Select Incident", [inc.get_id() for inc in incidents])

        # Find the selected incident
        selected = next((inc for inc in incidents if inc.get_id() == incident_id), None)

        if selected:
            st.info(f"**Current Status:** {selected.get_status()}")
            st.info(f"**Description:** {selected.get_description()[:100]}...")

        new_status = st.selectbox("New Status", ["Open", "Investigating", "Resolved"])

        if st.button("Update Status", use_container_width=True):
            update_incident_status(incident_id, new_status)
            st.success("Status updated")
            st.rerun()
    else:
        st.info("No incidents available")

# ---------------- DELETE ----------------
with tab3:
    if incidents:
        incident_id = st.selectbox("Select Incident to Delete", [inc.get_id() for inc in incidents])

        # Find and display the incident to be deleted
        selected = next((inc for inc in incidents if inc.get_id() == incident_id), None)
        if selected:
            st.warning(f"**You are about to delete:** {selected}")

        confirm = st.checkbox("I confirm deletion")

        if st.button("Delete Incident", disabled=not confirm, use_container_width=True):
            delete_incident(incident_id)
            st.success("Incident deleted")
            st.rerun()
    else:
        st.info("No incidents available")

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption("🔒 Cybersecurity Management System | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
