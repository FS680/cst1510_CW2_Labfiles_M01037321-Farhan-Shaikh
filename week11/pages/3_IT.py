"""IT Operations Dashboard - Refactored with OOP."""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
# OOP Imports
# ============================================================
from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="IT Operations",
    page_icon="💻",
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
def get_all_tickets() -> list[ITTicket]:
    """Fetch all tickets and convert to ITTicket objects."""
    rows = db_manager.fetch_all(
        """SELECT id, ticket_id, priority, status, category,
           subject, description, created_date, resolved_date, assigned_to
           FROM it_tickets
           ORDER BY id DESC"""
    )

    tickets = []
    for row in rows:
        ticket = ITTicket(
            ticket_db_id=row["id"],
            ticket_id=row["ticket_id"],
            priority=row["priority"],
            status=row["status"],
            category=row["category"],
            subject=row["subject"],
            description=row["description"],
            created_date=row["created_date"],
            resolved_date=row["resolved_date"] if row["resolved_date"] else None,
            assigned_to=row["assigned_to"] if row["assigned_to"] else None
        )
        tickets.append(ticket)

    return tickets

def insert_ticket(ticket_id: str, priority: str, status: str, category: str,
                 subject: str, description: str, created_date: str,
                 resolved_date: str = None, assigned_to: str = None) -> None:
    """Insert a new ticket into the database."""
    db_manager.execute_query(
        """INSERT INTO it_tickets
           (ticket_id, priority, status, category, subject, description,
            created_date, resolved_date, assigned_to)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (ticket_id, priority, status, category, subject, description,
         created_date, resolved_date, assigned_to)
    )

def update_ticket_status(ticket_db_id: int, new_status: str, resolved_date: str = None) -> int:
    """Update the status of a ticket. Returns number of rows affected."""
    if resolved_date:
        cursor = db_manager.execute_query(
            "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE id = ?",
            (new_status, resolved_date, ticket_db_id)
        )
    else:
        cursor = db_manager.execute_query(
            "UPDATE it_tickets SET status = ? WHERE id = ?",
            (new_status, ticket_db_id)
        )
    return cursor.rowcount

def delete_ticket(ticket_db_id: int) -> int:
    """Delete a ticket from the database. Returns number of rows affected."""
    cursor = db_manager.execute_query(
        "DELETE FROM it_tickets WHERE id = ?",
        (ticket_db_id,)
    )
    return cursor.rowcount

# ============================================================
# Header
# ============================================================
st.markdown("""
    <h1 style='text-align: center; color: #7B1FA2;'>
        💻 IT Operations Control Center
    </h1>
    <p style='text-align: center; color: #666;'>
        Streamlined ticket management and system monitoring
    </p>
    <hr style='margin: 20px 0;'>
""", unsafe_allow_html=True)

# ============================================================
# Fetch Data using OOP
# ============================================================
tickets = get_all_tickets()

# Convert to DataFrame for visualization (pandas still used for Plotly)
df = pd.DataFrame([
    {
        "id": tk.get_db_id(),
        "ticket_id": tk.get_ticket_id(),
        "priority": tk.get_priority(),
        "status": tk.get_status(),
        "category": tk.get_category(),
        "subject": tk.get_subject(),
        "description": tk.get_description(),
        "created_date": tk.get_created_date(),
        "resolved_date": tk.get_resolved_date(),
        "assigned_to": tk.get_assigned_to(),
        "priority_level": tk.get_priority_level()
    }
    for tk in tickets
])

# ============================================================
# Overview Metrics (Using Object Methods)
# ============================================================
st.subheader("📊 Support Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tickets = len(tickets)
    st.metric(
        "Total Tickets",
        total_tickets,
        delta="All Time"
    )

with col2:
    open_tickets = sum(1 for tk in tickets if not tk.is_resolved() and tk.get_status() == "Open")
    st.metric(
        "Open Tickets",
        open_tickets,
        delta="Pending" if open_tickets > 0 else "Clear",
        delta_color="inverse" if open_tickets > 0 else "normal"
    )

with col3:
    critical_tickets = sum(1 for tk in tickets if tk.is_critical())
    st.metric(
        "Critical Priority",
        critical_tickets,
        delta="Urgent" if critical_tickets > 0 else "None",
        delta_color="inverse" if critical_tickets > 0 else "normal"
    )

with col4:
    resolved = sum(1 for tk in tickets if tk.is_resolved())
    resolution_rate = (resolved / total_tickets * 100) if total_tickets > 0 else 0
    st.metric(
        "Resolution Rate",
        f"{resolution_rate:.1f}%",
        delta=f"{resolved} Resolved"
    )

st.divider()

# ============================================================
# Advanced Visualizations
# ============================================================
if not df.empty:
    # Row 1: Priority and Status Analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Priority Distribution")

        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['priority', 'count']

        # Custom colors for priority
        color_map = {
            'Critical': '#D32F2F',
            'High': '#F57C00',
            'Medium': '#FBC02D',
            'Low': '#388E3C'
        }

        fig1 = go.Figure(data=[go.Pie(
            labels=priority_counts['priority'],
            values=priority_counts['count'],
            hole=0.6,
            marker=dict(colors=[color_map.get(p, '#888888') for p in priority_counts['priority']]),
            textinfo='label+percent+value',
            textfont_size=13
        )])
        fig1.update_layout(
            height=350,
            showlegend=True,
            annotations=[dict(text='Tickets', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("### 📊 Status Breakdown")

        status_priority = df.groupby(['status', 'priority']).size().reset_index(name='count')

        fig2 = px.bar(
            status_priority,
            x='status',
            y='count',
            color='priority',
            title="",
            barmode='stack',
            color_discrete_map=color_map,
            height=350
        )
        fig2.update_layout(showlegend=True, legend_title="Priority")
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2: Category and Timeline
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏷️ Tickets by Category")

        if 'category' in df.columns:
            category_counts = df['category'].value_counts().head(10).reset_index()
            category_counts.columns = ['category', 'count']

            fig3 = go.Figure(go.Bar(
                y=category_counts['category'],
                x=category_counts['count'],
                orientation='h',
                marker=dict(
                    color=category_counts['count'],
                    colorscale='Purples',
                    showscale=True
                ),
                text=category_counts['count'],
                textposition='auto'
            ))
            fig3.update_layout(
                height=350,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("### ⏱️ Resolution Progress")

        status_order = ['Open', 'In Progress', 'Resolved']
        status_counts = df['status'].value_counts().reindex(status_order, fill_value=0).reset_index()
        status_counts.columns = ['status', 'count']

        fig4 = go.Figure(go.Waterfall(
            name="Tickets",
            orientation="v",
            x=status_counts['status'],
            y=status_counts['count'],
            text=status_counts['count'],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#FF6B6B"}},
            increasing={"marker": {"color": "#4ECDC4"}},
            totals={"marker": {"color": "#95E1D3"}}
        ))
        fig4.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

# ============================================================
# Ticket Table with Search (Using Object Methods)
# ============================================================
st.subheader("🔍 Ticket Queue")

if tickets:
    # Search and filter
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        search = st.text_input("🔎 Search tickets...", placeholder="Search by subject or description...")

    with col2:
        all_priorities = sorted(set(tk.get_priority() for tk in tickets))
        filter_priority = st.selectbox("Priority", ["All"] + all_priorities)

    with col3:
        all_statuses = sorted(set(tk.get_status() for tk in tickets))
        filter_status = st.selectbox("Status", ["All"] + all_statuses)

    with col4:
        all_categories = sorted(set(tk.get_category() for tk in tickets))
        filter_category = st.selectbox("Category", ["All"] + all_categories)

    # Filter tickets using object methods
    filtered_tickets = tickets.copy()

    if search:
        filtered_tickets = [
            tk for tk in filtered_tickets
            if search.lower() in tk.get_subject().lower() or
               search.lower() in tk.get_description().lower()
        ]

    if filter_priority != "All":
        filtered_tickets = [tk for tk in filtered_tickets if tk.get_priority() == filter_priority]

    if filter_status != "All":
        filtered_tickets = [tk for tk in filtered_tickets if tk.get_status() == filter_status]

    if filter_category != "All":
        filtered_tickets = [tk for tk in filtered_tickets if tk.get_category() == filter_category]

    # Convert to DataFrame for display
    display_df = pd.DataFrame([
        {
            "id": tk.get_db_id(),
            "ticket_id": tk.get_ticket_id(),
            "priority": tk.get_priority(),
            "status": tk.get_status(),
            "category": tk.get_category(),
            "subject": tk.get_subject(),
            "assigned_to": tk.get_assigned_to() if tk.get_assigned_to() else "Unassigned"
        }
        for tk in filtered_tickets
    ])

    st.dataframe(
        display_df,
        use_container_width=True,
        height=350,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "ticket_id": st.column_config.TextColumn("Ticket #", width="small"),
            "priority": st.column_config.TextColumn("Priority", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "category": st.column_config.TextColumn("Category", width="medium"),
            "subject": st.column_config.TextColumn("Subject", width="large"),
            "assigned_to": st.column_config.TextColumn("Assigned", width="small"),
        }
    )

    st.caption(f"Showing {len(filtered_tickets)} of {len(tickets)} tickets")
else:
    st.info("📝 No tickets found. Create your first support ticket below!")

st.divider()

# ============================================================
# CRUD Operations in Tabs
# ============================================================
st.subheader("⚙️ Ticket Management")

tab1, tab2, tab3 = st.tabs(["➕ Create Ticket", "✏️ Update Status", "🗑️ Close Ticket"])

# ---------------- CREATE ----------------
with tab1:
    st.markdown("#### Submit New Support Ticket")

    col1, col2 = st.columns(2)

    with col1:
        ticket_id = st.text_input("🎫 Ticket ID", placeholder="e.g., TKT-2024-001")
        priority = st.select_slider(
            "⚠️ Priority Level",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
        status = st.selectbox("📊 Initial Status", ["Open", "In Progress", "Resolved"])
        category = st.selectbox(
            "🏷️ Category",
            ["Hardware", "Software", "Network", "Access", "Security", "Other"]
        )

    with col2:
        subject = st.text_input("📝 Subject", placeholder="Brief description of the issue")
        description = st.text_area("📄 Detailed Description", placeholder="Provide detailed information about the ticket...")
        assigned_to = st.text_input("👤 Assign To", placeholder="Enter technician name")
        created_date = st.date_input("📅 Created Date", value=datetime.now())

    if st.button("🚀 Create Ticket", type="primary", use_container_width=True):
        if ticket_id and subject and description:
            insert_ticket(
                ticket_id,
                priority,
                status,
                category,
                subject,
                description,
                str(created_date),
                None,
                assigned_to if assigned_to else None
            )
            st.success("✅ Ticket created successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields!")

# ---------------- UPDATE STATUS ----------------
with tab2:
    st.markdown("#### Update Ticket Status")

    if tickets:
        col1, col2 = st.columns(2)

        with col1:
            # Create selection with ticket details
            update_id = st.selectbox(
                "Select Ticket",
                options=[tk.get_db_id() for tk in tickets],
                format_func=lambda x: f"ID {x} - {next(tk.get_ticket_id() for tk in tickets if tk.get_db_id() == x)} ({next(tk.get_subject() for tk in tickets if tk.get_db_id() == x)[:30]}...)"
            )

            # Find current ticket
            current_ticket = next((tk for tk in tickets if tk.get_db_id() == update_id), None)

            if current_ticket:
                # Show current details using object methods
                st.info(f"""
                    **Current Status:** {current_ticket.get_status()}
                    **Priority:** {current_ticket.get_priority()}
                    **Category:** {current_ticket.get_category()}
                    **Assigned:** {current_ticket.get_assigned_to() if current_ticket.get_assigned_to() else 'Unassigned'}
                """)

        with col2:
            new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved"])
            resolved_date = None

            if new_status == "Resolved":
                resolved_date = st.date_input("Resolution Date", value=datetime.now())

            st.write("")

            if st.button("💾 Update Status", type="primary", use_container_width=True):
                rows = update_ticket_status(
                    update_id,
                    new_status,
                    str(resolved_date) if resolved_date else None
                )

                if rows:
                    st.success(f"✅ Ticket #{update_id} updated to '{new_status}'")
                    st.rerun()
                else:
                    st.error("❌ Update failed")
    else:
        st.info("No tickets available to update")

# ---------------- DELETE ----------------
with tab3:
    st.markdown("#### Close and Remove Ticket")

    if tickets:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Create selection with ticket details
            del_id = st.selectbox(
                "Select Ticket to Close",
                options=[tk.get_db_id() for tk in tickets],
                format_func=lambda x: f"ID {x} - {next(tk.get_ticket_id() for tk in tickets if tk.get_db_id() == x)}",
                key="del_select"
            )

            # Find ticket to delete
            to_delete = next((tk for tk in tickets if tk.get_db_id() == del_id), None)

            if to_delete:
                # Show details using object methods
                st.warning(f"""
                    ⚠️ **You are about to close and remove:**
                    **Ticket ID:** {to_delete.get_ticket_id()}
                    **Subject:** {to_delete.get_subject()}
                    **Priority:** {to_delete.get_priority()}
                    **Status:** {to_delete.get_status()}
                    **Created:** {to_delete.get_created_date()}
                """)

        with col2:
            st.write("")
            st.write("")
            confirm = st.checkbox("✅ I confirm deletion", key="confirm_del")

            if st.button("🗑️ Close Ticket", type="secondary", disabled=not confirm, use_container_width=True):
                rows = delete_ticket(del_id)

                if rows:
                    st.success(f"✅ Ticket #{del_id} closed and removed")
                    st.rerun()
                else:
                    st.error("❌ Deletion failed")
    else:
        st.info("No tickets available to close")

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption("💻 IT Operations Management System | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
