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
from db.datasets import (
    get_all_datasets,
    insert_dataset
)

# Page config
st.set_page_config(page_title="Data Science Hub", page_icon="📊", layout="wide")

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

# Header with styling
st.markdown("""
    <h1 style='text-align: center; color: #1E88E5;'>
        📊 Data Science Analytics Hub
    </h1>
    <p style='text-align: center; color: #666;'>
        Centralized dataset management and insights
    </p>
    <hr style='margin: 20px 0;'>
""", unsafe_allow_html=True)

# Connect to database
conn = connect_database()

# ---------------- Fetch Data ----------------
df = get_all_datasets(conn)

# ---------------- Top Metrics Dashboard ----------------
st.subheader("📈 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_datasets = len(df)
    st.metric(
        "Total Datasets",
        total_datasets,
        delta=f"{total_datasets} Active"
    )

with col2:
    if not df.empty:
        total_records = df['record_count'].sum()
        st.metric(
            "Total Records",
            f"{total_records:,}",
            delta="All Sources"
        )
    else:
        st.metric("Total Records", 0)

with col3:
    if not df.empty:
        total_size = df['file_size_mb'].sum()
        st.metric(
            "Total Storage",
            f"{total_size:.2f} MB",
            delta=f"{total_size/1024:.2f} GB" if total_size > 1024 else "Size"
        )
    else:
        st.metric("Total Storage", "0 MB")

with col4:
    if not df.empty:
        categories = df['category'].nunique()
        st.metric(
            "Categories",
            categories,
            delta="Unique"
        )
    else:
        st.metric("Categories", 0)

st.divider()

# ---------------- Advanced Visualizations ----------------
if not df.empty:

    # Row 1: Category Analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Records by Category")
        category_records = df.groupby('category')['record_count'].sum().reset_index()

        fig1 = px.sunburst(
            df,
            path=['category', 'dataset_name'],
            values='record_count',
            title="",
            color='record_count',
            color_continuous_scale='Blues',
            height=400
        )
        fig1.update_traces(textinfo="label+percent parent")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("### 💾 Storage Distribution")

        fig2 = px.bar(
            df.sort_values('file_size_mb', ascending=False).head(10),
            x='dataset_name',
            y='file_size_mb',
            title="",
            color='file_size_mb',
            color_continuous_scale='Teal',
            text='file_size_mb',
            height=400
        )
        fig2.update_traces(texttemplate='%{text:.2f} MB', textposition='outside')
        fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2: Detailed Analytics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Dataset Size vs Records")

        fig3 = px.scatter(
            df,
            x='record_count',
            y='file_size_mb',
            size='record_count',
            color='category',
            hover_name='dataset_name',
            title="",
            height=350,
            size_max=50
        )
        fig3.update_layout(showlegend=True)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("### 🔢 Top Datasets by Records")

        top_datasets = df.nlargest(8, 'record_count')[['dataset_name', 'record_count']]

        fig4 = go.Figure(go.Bar(
            x=top_datasets['record_count'],
            y=top_datasets['dataset_name'],
            orientation='h',
            marker=dict(
                color=top_datasets['record_count'],
                colorscale='Viridis',
                showscale=True
            ),
            text=top_datasets['record_count'],
            textposition='auto'
        ))
        fig4.update_layout(
            height=350,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

# ---------------- Datasets Table with Search ----------------
st.subheader("🔍 Dataset Repository")

if not df.empty:
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search = st.text_input("🔎 Search datasets...", placeholder="Search by name or source...")

    with col2:
        if 'category' in df.columns:
            filter_category = st.selectbox("Filter by Category", ["All"] + sorted(df['category'].unique().tolist()))
        else:
            filter_category = "All"

    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Records (High-Low)", "Records (Low-High)", "Size (High-Low)", "Size (Low-High)"])

    # Apply filters
    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df['dataset_name'].str.contains(search, case=False, na=False) |
            filtered_df['source'].str.contains(search, case=False, na=False)
        ]

    if filter_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == filter_category]

    # Apply sorting
    if sort_by == "Records (High-Low)":
        filtered_df = filtered_df.sort_values('record_count', ascending=False)
    elif sort_by == "Records (Low-High)":
        filtered_df = filtered_df.sort_values('record_count', ascending=True)
    elif sort_by == "Size (High-Low)":
        filtered_df = filtered_df.sort_values('file_size_mb', ascending=False)
    elif sort_by == "Size (Low-High)":
        filtered_df = filtered_df.sort_values('file_size_mb', ascending=True)
    else:
        filtered_df = filtered_df.sort_values('dataset_name')

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=350,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "dataset_name": st.column_config.TextColumn("Dataset Name", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "source": st.column_config.TextColumn("Source", width="medium"),
            "record_count": st.column_config.NumberColumn("Records", format="%d"),
            "file_size_mb": st.column_config.NumberColumn("Size (MB)", format="%.2f"),
        }
    )

    st.caption(f"Showing {len(filtered_df)} of {len(df)} datasets")
else:
    st.info("📝 No datasets found. Start by adding your first dataset below!")

st.divider()

# ---------------- CRUD Operations in Tabs ----------------
st.subheader("⚙️ Dataset Management")

tab1, tab2, tab3 = st.tabs(["➕ Add Dataset", "✏️ Update Metadata", "🗑️ Remove Dataset"])

with tab1:
    st.markdown("#### Register New Dataset")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("📁 Dataset Name", placeholder="e.g., Customer Database 2024")
        category = st.selectbox(
            "🏷️ Category",
            ["Sales", "Marketing", "Finance", "Operations", "Research", "Analytics", "Other"]
        )
        source = st.text_input("🔗 Data Source", placeholder="e.g., Internal DB, API, CSV Import")

    with col2:
        record_count = st.number_input("🔢 Number of Records", min_value=0, step=1, value=0)
        file_size = st.number_input("💾 File Size (MB)", min_value=0.0, step=0.1, value=0.0, format="%.2f")
        last_updated = st.date_input("📅 Last Updated", value=datetime.now())

    if st.button("🚀 Register Dataset", type="primary", use_container_width=True):
        if name and category and source:
            insert_dataset(
                conn,
                name,
                category,
                source,
                str(last_updated),
                record_count,
                file_size
            )
            st.success("✅ Dataset registered successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields!")

with tab2:
    st.markdown("#### Update Dataset Information")

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            update_id = st.selectbox(
                "Select Dataset",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID {x} - {df[df['id']==x]['dataset_name'].values[0]}"
            )

            # Show current details
            current = df[df['id'] == update_id].iloc[0]
            st.info(f"""
                **Current Info:**
                📁 Name: {current['dataset_name']}
                🏷️ Category: {current['category']}
                🔢 Records: {current['record_count']:,}
                💾 Size: {current['file_size_mb']:.2f} MB
            """)

        with col2:
            new_cat = st.text_input("New Category", value=current['category'])
            new_src = st.text_input("New Source", value=current['source'])
            new_date = st.date_input("New Last Updated", value=datetime.now())
            new_count = st.number_input("New Record Count", value=int(current['record_count']), step=1)
            new_size = st.number_input("New Size (MB)", value=float(current['file_size_mb']), step=0.1, format="%.2f")

        if st.button("💾 Update Dataset", type="primary", use_container_width=True):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE datasets_metadata
                SET category=?, source=?, last_updated=?, record_count=?, file_size_mb=?
                WHERE id=?
            """, (new_cat, new_src, str(new_date), new_count, new_size, update_id))
            conn.commit()
            rows = cursor.rowcount

            if rows:
                st.success(f"✅ Dataset #{update_id} updated successfully!")
                st.rerun()
            else:
                st.error("❌ Update failed")
    else:
        st.info("No datasets available to update")

with tab3:
    st.markdown("#### Remove Dataset from Repository")

    if not df.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            del_id = st.selectbox(
                "Select Dataset to Remove",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID {x} - {df[df['id']==x]['dataset_name'].values[0]}",
                key="del_select"
            )

            # Show details of dataset to be deleted
            to_delete = df[df['id'] == del_id].iloc[0]
            st.warning(f"""
                ⚠️ **You are about to delete:**
                **ID:** {to_delete['id']}
                **Name:** {to_delete['dataset_name']}
                **Category:** {to_delete['category']}
                **Records:** {to_delete['record_count']:,}
                **Size:** {to_delete['file_size_mb']:.2f} MB
            """)

        with col2:
            st.write("")
            st.write("")
            confirm = st.checkbox("✅ I confirm deletion", key="confirm_del")

            if st.button("🗑️ Delete Dataset", type="secondary", disabled=not confirm, use_container_width=True):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM datasets_metadata WHERE id=?", (del_id,))
                conn.commit()
                rows = cursor.rowcount

                if rows:
                    st.success(f"✅ Dataset #{del_id} removed from repository")
                    st.rerun()
                else:
                    st.error("❌ Deletion failed")
    else:
        st.info("No datasets available to delete")

# Close connection
conn.close()

# Footer
st.markdown("---")
st.caption("📊 Data Science Analytics Platform | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
