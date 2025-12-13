import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
from db.db import connect_database
from db.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident
)

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
# Header
# ============================================================
st.markdown("""
<h1 style='text-align:center;color:#FF4B4B;'>🛡️ Cybersecurity Command Center</h1>
<p style='text-align:center;color:#666;'>Incident monitoring and response management</p>
<hr>
""", unsafe_allow_html=True)

# ============================================================
# DB connection
# ============================================================
conn = connect_database()
df = get_all_incidents(conn)

# ============================================================
# Overview Metrics
# ============================================================
st.subheader("📊 Security Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents", len(df))

with col2:
    critical = len(df[df["severity"] == "Critical"]) if not df.empty else 0
    st.metric("Critical Incidents", critical)

with col3:
    open_cases = len(df[df["status"] == "Open"]) if not df.empty else 0
    st.metric("Open Cases", open_cases)

with col4:
    investigating = len(df[df["status"] == "Investigating"]) if not df.empty else 0
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
# Incident Table
# ============================================================
st.subheader("🔍 Incident Records")

if not df.empty:
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search = st.text_input("🔎 Search incidents")

    with col2:
        severity_filter = st.selectbox("Severity", ["All"] + df["severity"].unique().tolist())

    with col3:
        status_filter = st.selectbox("Status", ["All"] + df["status"].unique().tolist())

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["incident_type"].str.contains(search, case=False, na=False) |
            filtered["description"].str.contains(search, case=False, na=False)
        ]

    if severity_filter != "All":
        filtered = filtered[filtered["severity"] == severity_filter]

    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]

    st.dataframe(
        filtered,
        use_container_width=True,
        height=300
    )

    st.caption(f"Showing {len(filtered)} of {len(df)} incidents")
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
                conn,
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
    if not df.empty:
        incident_id = st.selectbox("Select Incident", df["id"].tolist())
        new_status = st.selectbox("New Status", ["Open", "Investigating", "Resolved"])

        if st.button("Update Status", use_container_width=True):
            update_incident_status(conn, incident_id, new_status)
            st.success("Status updated")
            st.rerun()
    else:
        st.info("No incidents available")

# ---------------- DELETE ----------------
with tab3:
    if not df.empty:
        incident_id = st.selectbox("Select Incident to Delete", df["id"].tolist())
        confirm = st.checkbox("I confirm deletion")

        if st.button("Delete Incident", disabled=not confirm, use_container_width=True):
            delete_incident(conn, incident_id)
            st.success("Incident deleted")
            st.rerun()
    else:
        st.info("No incidents available")

# ============================================================
# Cleanup
# ============================================================
conn.close()

st.markdown("---")
st.caption("🔒 Cybersecurity Management System | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
