"""Data Science Dashboard - Refactored with OOP."""

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
from models.dataset import Dataset

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="Data Science Hub",
    page_icon="📊",
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
def get_all_datasets() -> list[Dataset]:
    """Fetch all datasets and convert to Dataset objects."""
    rows = db_manager.fetch_all(
        """SELECT id, dataset_name, category, source, last_updated,
           record_count, file_size_mb
           FROM datasets_metadata
           ORDER BY id DESC"""
    )

    datasets = []
    for row in rows:
        dataset = Dataset(
            dataset_id=row["id"],
            name=row["dataset_name"],
            category=row["category"],
            source=row["source"],
            last_updated=row["last_updated"],
            record_count=row["record_count"],
            file_size_mb=row["file_size_mb"]
        )
        datasets.append(dataset)

    return datasets

def insert_dataset(name: str, category: str, source: str, last_updated: str,
                   record_count: int, file_size_mb: float) -> None:
    """Insert a new dataset into the database."""
    db_manager.execute_query(
        """INSERT INTO datasets_metadata
           (dataset_name, category, source, last_updated, record_count, file_size_mb)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, category, source, last_updated, record_count, file_size_mb)
    )

def update_dataset(dataset_id: int, category: str, source: str, last_updated: str,
                   record_count: int, file_size_mb: float) -> None:
    """Update an existing dataset."""
    db_manager.execute_query(
        """UPDATE datasets_metadata
           SET category = ?, source = ?, last_updated = ?,
               record_count = ?, file_size_mb = ?
           WHERE id = ?""",
        (category, source, last_updated, record_count, file_size_mb, dataset_id)
    )

def delete_dataset(dataset_id: int) -> None:
    """Delete a dataset from the database."""
    db_manager.execute_query(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (dataset_id,)
    )

# ============================================================
# Header
# ============================================================
st.markdown("""
    <h1 style='text-align: center; color: #1E88E5;'>
        📊 Data Science Analytics Hub
    </h1>
    <p style='text-align: center; color: #666;'>
        Centralized dataset management and insights
    </p>
    <hr style='margin: 20px 0;'>
""", unsafe_allow_html=True)

# ============================================================
# Fetch Data using OOP
# ============================================================
datasets = get_all_datasets()

# Convert to DataFrame for visualization (pandas still used for Plotly)
df = pd.DataFrame([
    {
        "id": ds.get_id(),
        "dataset_name": ds.get_name(),
        "category": ds.get_category(),
        "source": ds.get_source(),
        "last_updated": ds.get_last_updated(),
        "record_count": ds.get_record_count(),
        "file_size_mb": ds.get_file_size_mb()
    }
    for ds in datasets
])

# ============================================================
# Overview Metrics (Using Object Methods)
# ============================================================
st.subheader("📈 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_datasets = len(datasets)
    st.metric(
        "Total Datasets",
        total_datasets,
        delta=f"{total_datasets} Active"
    )

with col2:
    total_records = sum(ds.get_record_count() for ds in datasets)
    st.metric(
        "Total Records",
        f"{total_records:,}",
        delta="All Sources"
    )

with col3:
    total_size = sum(ds.get_file_size_mb() for ds in datasets)
    st.metric(
        "Total Storage",
        f"{total_size:.2f} MB",
        delta=f"{total_size/1024:.2f} GB" if total_size > 1024 else "Size"
    )

with col4:
    categories = len(set(ds.get_category() for ds in datasets)) if datasets else 0
    st.metric(
        "Categories",
        categories,
        delta="Unique"
    )

st.divider()

# ============================================================
# Advanced Visualizations
# ============================================================
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

# ============================================================
# Dataset Table with Search (Using Object Methods)
# ============================================================
st.subheader("🔍 Dataset Repository")

if datasets:
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search = st.text_input("🔎 Search datasets...", placeholder="Search by name or source...")

    with col2:
        all_categories = sorted(set(ds.get_category() for ds in datasets))
        filter_category = st.selectbox("Filter by Category", ["All"] + all_categories)

    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Name", "Records (High-Low)", "Records (Low-High)", "Size (High-Low)", "Size (Low-High)"]
        )

    # Filter datasets using object methods
    filtered_datasets = datasets.copy()

    if search:
        filtered_datasets = [
            ds for ds in filtered_datasets
            if search.lower() in ds.get_name().lower() or
               search.lower() in ds.get_source().lower()
        ]

    if filter_category != "All":
        filtered_datasets = [ds for ds in filtered_datasets if ds.get_category() == filter_category]

    # Sort datasets using object methods
    if sort_by == "Records (High-Low)":
        filtered_datasets.sort(key=lambda x: x.get_record_count(), reverse=True)
    elif sort_by == "Records (Low-High)":
        filtered_datasets.sort(key=lambda x: x.get_record_count())
    elif sort_by == "Size (High-Low)":
        filtered_datasets.sort(key=lambda x: x.get_file_size_mb(), reverse=True)
    elif sort_by == "Size (Low-High)":
        filtered_datasets.sort(key=lambda x: x.get_file_size_mb())
    else:
        filtered_datasets.sort(key=lambda x: x.get_name())

    # Convert to DataFrame for display
    display_df = pd.DataFrame([
        {
            "id": ds.get_id(),
            "dataset_name": ds.get_name(),
            "category": ds.get_category(),
            "source": ds.get_source(),
            "record_count": ds.get_record_count(),
            "file_size_mb": ds.get_file_size_mb()
        }
        for ds in filtered_datasets
    ])

    st.dataframe(
        display_df,
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

    st.caption(f"Showing {len(filtered_datasets)} of {len(datasets)} datasets")

    # Show statistics about large datasets
    large_datasets = [ds for ds in filtered_datasets if ds.is_large_dataset(100)]
    if large_datasets:
        st.info(f"📦 {len(large_datasets)} large datasets (>100 MB) in current view")

else:
    st.info("📝 No datasets found. Start by adding your first dataset below!")

st.divider()

# ============================================================
# CRUD Operations in Tabs
# ============================================================
st.subheader("⚙️ Dataset Management")

tab1, tab2, tab3 = st.tabs(["➕ Add Dataset", "✏️ Update Metadata", "🗑️ Remove Dataset"])

# ---------------- ADD ----------------
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

        # Show calculated size in GB if large
        if file_size > 1024:
            st.info(f"📦 Size in GB: {file_size/1024:.2f} GB")

    if st.button("🚀 Register Dataset", type="primary", use_container_width=True):
        if name and category and source:
            insert_dataset(name, category, source, str(last_updated), record_count, file_size)
            st.success("✅ Dataset registered successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields!")

# ---------------- UPDATE ----------------
with tab2:
    st.markdown("#### Update Dataset Information")

    if datasets:
        col1, col2 = st.columns(2)

        with col1:
            # Create selection with dataset names
            update_id = st.selectbox(
                "Select Dataset",
                options=[ds.get_id() for ds in datasets],
                format_func=lambda x: f"ID {x} - {next(ds.get_name() for ds in datasets if ds.get_id() == x)}"
            )

            # Find current dataset
            current_dataset = next((ds for ds in datasets if ds.get_id() == update_id), None)

            if current_dataset:
                # Show current details using object methods
                st.info(f"""
                    **Current Info:**
                    📁 Name: {current_dataset.get_name()}
                    🏷️ Category: {current_dataset.get_category()}
                    🔢 Records: {current_dataset.get_record_count():,}
                    💾 Size: {current_dataset.get_file_size_mb():.2f} MB
                    📊 Density: {current_dataset.get_record_density():.2f} records/MB
                    📦 Large Dataset: {'Yes' if current_dataset.is_large_dataset() else 'No'}
                """)

        with col2:
            if current_dataset:
                new_cat = st.text_input("New Category", value=current_dataset.get_category())
                new_src = st.text_input("New Source", value=current_dataset.get_source())
                new_date = st.date_input("New Last Updated", value=datetime.now())
                new_count = st.number_input(
                    "New Record Count",
                    value=current_dataset.get_record_count(),
                    step=1
                )
                new_size = st.number_input(
                    "New Size (MB)",
                    value=float(current_dataset.get_file_size_mb()),
                    step=0.1,
                    format="%.2f"
                )

                if st.button("💾 Update Dataset", type="primary", use_container_width=True):
                    update_dataset(update_id, new_cat, new_src, str(new_date), new_count, new_size)
                    st.success(f"✅ Dataset #{update_id} updated successfully!")
                    st.rerun()
    else:
        st.info("No datasets available to update")

# ---------------- DELETE ----------------
with tab3:
    st.markdown("#### Remove Dataset from Repository")

    if datasets:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Create selection with dataset names
            del_id = st.selectbox(
                "Select Dataset to Remove",
                options=[ds.get_id() for ds in datasets],
                format_func=lambda x: f"ID {x} - {next(ds.get_name() for ds in datasets if ds.get_id() == x)}",
                key="del_select"
            )

            # Find dataset to delete
            to_delete = next((ds for ds in datasets if ds.get_id() == del_id), None)

            if to_delete:
                # Show details using __str__ method and object methods
                st.warning(f"""
                    ⚠️ **You are about to delete:**
                    **ID:** {to_delete.get_id()}
                    **Name:** {to_delete.get_name()}
                    **Category:** {to_delete.get_category()}
                    **Records:** {to_delete.get_record_count():,}
                    **Size:** {to_delete.get_file_size_mb():.2f} MB

                    **Additional Info:**
                    - Source: {to_delete.get_source()}
                    - Last Updated: {to_delete.get_last_updated()}
                    - Record Density: {to_delete.get_record_density():.2f} records/MB
                """)

        with col2:
            st.write("")
            st.write("")
            confirm = st.checkbox("✅ I confirm deletion", key="confirm_del")

            if st.button("🗑️ Delete Dataset", type="secondary", disabled=not confirm, use_container_width=True):
                delete_dataset(del_id)
                st.success(f"✅ Dataset #{del_id} removed from repository")
                st.rerun()
    else:
        st.info("No datasets available to delete")

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption("📊 Data Science Analytics Platform | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
