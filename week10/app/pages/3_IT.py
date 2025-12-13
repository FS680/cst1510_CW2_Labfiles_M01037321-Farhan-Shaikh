import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Path setup
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP_ROOT = ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from db.db import connect_database
from db.tickets import (
    get_all_tickets,
    insert_ticket
)

# Page config
st.set_page_config(page_title="IT Operations", page_icon="💻", layout="wide")

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

# Header with styling
st.markdown("""
    <h1 style='text-align: center; color: #7B1FA2;'>
        💻 IT Operations Control Center
    </h1>
    <p style='text-align: center; color: #666;'>
        Streamlined ticket management and system monitoring
    </p>
    <hr style='margin: 20px 0;'>
""", unsafe_allow_html=True)

# Connect to database
conn = connect_database()

# ---------------- Fetch Data ----------------
df = get_all_tickets(conn)

# ---------------- Top Metrics Dashboard ----------------
st.subheader("📊 Support Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tickets = len(df)
    st.metric(
        "Total Tickets",
        total_tickets,
        delta="All Time"
    )

with col2:
    if not df.empty:
        open_tickets = len(df[df['status'] == 'Open'])
        st.metric(
            "Open Tickets",
            open_tickets,
            delta="Pending" if open_tickets > 0 else "Clear",
            delta_color="inverse" if open_tickets > 0 else "normal"
        )
    else:
        st.metric("Open Tickets", 0)

with col3:
    if not df.empty:
        critical_tickets = len(df[df['priority'] == 'Critical'])
        st.metric(
            "Critical Priority",
            critical_tickets,
            delta="Urgent" if critical_tickets > 0 else "None",
            delta_color="inverse" if critical_tickets > 0 else "normal"
        )
    else:
        st.metric("Critical Priority", 0)

with col4:
    if not df.empty:
        resolved = len(df[df['status'] == 'Resolved'])
        resolution_rate = (resolved / total_tickets * 100) if total_tickets > 0 else 0
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            delta=f"{resolved} Resolved"
        )
    else:
        st.metric("Resolution Rate", "0%")

st.divider()

# ---------------- Advanced Visualizations ----------------
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

# ---------------- Tickets Table with Search ----------------
st.subheader("🔍 Ticket Queue")

if not df.empty:
    # Search and filter
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        search = st.text_input("🔎 Search tickets...", placeholder="Search by subject or description...")

    with col2:
        if 'priority' in df.columns:
            filter_priority = st.selectbox("Priority", ["All"] + sorted(df['priority'].unique().tolist()))
        else:
            filter_priority = "All"

    with col3:
        if 'status' in df.columns:
            filter_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
        else:
            filter_status = "All"

    with col4:
        if 'category' in df.columns:
            filter_category = st.selectbox("Category", ["All"] + sorted(df['category'].unique().tolist()))
        else:
            filter_category = "All"

    # Apply filters
    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df['subject'].str.contains(search, case=False, na=False) |
            filtered_df['description'].str.contains(search, case=False, na=False)
        ]

    if filter_priority != "All":
        filtered_df = filtered_df[filtered_df['priority'] == filter_priority]

    if filter_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]

    if filter_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == filter_category]

    st.dataframe(
        filtered_df,
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

    st.caption(f"Showing {len(filtered_df)} of {len(df)} tickets")
else:
    st.info("📝 No tickets found. Create your first support ticket below!")

st.divider()

# ---------------- CRUD Operations in Tabs ----------------
st.subheader("⚙️ Ticket Management")

tab1, tab2, tab3 = st.tabs(["➕ Create Ticket", "✏️ Update Status", "🗑️ Close Ticket"])

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
                conn,
                ticket_id,
                priority,
                status,
                category,
                subject,
                description,
                str(created_date),
                None,
                assigned_to
            )
            st.success("✅ Ticket created successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields!")

with tab2:
    st.markdown("#### Update Ticket Status")

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            update_id = st.selectbox(
                "Select Ticket",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID {x} - {df[df['id']==x]['ticket_id'].values[0]} ({df[df['id']==x]['subject'].values[0][:30]}...)"
            )

            # Show current details
            current = df[df['id'] == update_id].iloc[0]
            st.info(f"""
                **Current Status:** {current['status']}
                **Priority:** {current['priority']}
                **Category:** {current['category']}
                **Assigned:** {current['assigned_to'] if pd.notna(current['assigned_to']) else 'Unassigned'}
            """)

        with col2:
            new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved"])
            resolved_date = None

            if new_status == "Resolved":
                resolved_date = st.date_input("Resolution Date", value=datetime.now())

            st.write("")

            if st.button("💾 Update Status", type="primary", use_container_width=True):
                cursor = conn.cursor()
                if resolved_date:
                    cursor.execute(
                        "UPDATE it_tickets SET status=?, resolved_date=? WHERE id=?",
                        (new_status, str(resolved_date), update_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE it_tickets SET status=? WHERE id=?",
                        (new_status, update_id)
                    )
                conn.commit()
                rows = cursor.rowcount

                if rows:
                    st.success(f"✅ Ticket #{update_id} updated to '{new_status}'")
                    st.rerun()
                else:
                    st.error("❌ Update failed")
    else:
        st.info("No tickets available to update")

with tab3:
    st.markdown("#### Close and Remove Ticket")

    if not df.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            del_id = st.selectbox(
                "Select Ticket to Close",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID {x} - {df[df['id']==x]['ticket_id'].values[0]}",
                key="del_select"
            )

            # Show details of ticket to be deleted
            to_delete = df[df['id'] == del_id].iloc[0]
            st.warning(f"""
                ⚠️ **You are about to close and remove:**
                **Ticket ID:** {to_delete['ticket_id']}
                **Subject:** {to_delete['subject']}
                **Priority:** {to_delete['priority']}
                **Status:** {to_delete['status']}
                **Created:** {to_delete['created_date']}
            """)

        with col2:
            st.write("")
            st.write("")
            confirm = st.checkbox("✅ I confirm deletion", key="confirm_del")

            if st.button("🗑️ Close Ticket", type="secondary", disabled=not confirm, use_container_width=True):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM it_tickets WHERE id=?", (del_id,))
                conn.commit()
                rows = cursor.rowcount

                if rows:
                    st.success(f"✅ Ticket #{del_id} closed and removed")
                    st.rerun()
                else:
                    st.error("❌ Deletion failed")
    else:
        st.info("No tickets available to close")

# Close connection
conn.close()

# Footer
st.markdown("---")
st.caption("💻 IT Operations Management System | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
