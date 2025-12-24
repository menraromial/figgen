"""Dashboard component for multi-chart layouts."""

import streamlit as st
import pandas as pd
from typing import Optional


def render_dashboard_mode(df: pd.DataFrame, render_single_chart_fn) -> None:
    """
    Render dashboard mode with multiple charts.
    
    Args:
        df: DataFrame with the data
        render_single_chart_fn: Function to render a single chart
    """
    # Dashboard controls
    st.markdown("**Dashboard**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        layout = st.selectbox(
            "Disposition",
            options=["1x2", "2x1", "2x2", "1x3", "3x1"],
            key="dashboard_layout",
        )
    
    with col2:
        if st.button("Réinitialiser", key="reset_dashboard"):
            if "dashboard_charts" in st.session_state:
                st.session_state.dashboard_charts = []
            st.rerun()
    
    # Parse layout
    rows, cols = map(int, layout.split("x"))
    num_charts = rows * cols
    
    # Initialize dashboard charts
    if "dashboard_charts" not in st.session_state:
        st.session_state.dashboard_charts = [None] * num_charts
    
    # Ensure we have enough slots
    while len(st.session_state.dashboard_charts) < num_charts:
        st.session_state.dashboard_charts.append(None)
    
    # Render grid
    for row in range(rows):
        columns = st.columns(cols)
        
        for col_idx, column in enumerate(columns):
            chart_idx = row * cols + col_idx
            
            with column:
                with st.container():
                    st.markdown(f"**Graphique {chart_idx + 1}**")
                    
                    # Each chart has its own mini-config
                    chart_type = st.selectbox(
                        "Type",
                        options=["Courbes", "Nuage", "Barres", "Histogramme"],
                        key=f"dash_type_{chart_idx}",
                        label_visibility="collapsed",
                    )
                    
                    type_map = {
                        "Courbes": "line",
                        "Nuage": "scatter", 
                        "Barres": "bar",
                        "Histogramme": "histogram",
                    }
                    
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    all_cols = df.columns.tolist()
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        x_col = st.selectbox(
                            "X",
                            options=all_cols,
                            key=f"dash_x_{chart_idx}",
                            label_visibility="collapsed",
                        )
                    
                    with col_b:
                        y_col = st.selectbox(
                            "Y",
                            options=numeric_cols if numeric_cols else all_cols,
                            key=f"dash_y_{chart_idx}",
                            label_visibility="collapsed",
                        )
                    
                    # Store chart config
                    st.session_state.dashboard_charts[chart_idx] = {
                        "type": type_map.get(chart_type, "scatter"),
                        "x": x_col,
                        "y": y_col,
                    }


def get_dashboard_layout(layout: str) -> tuple[int, int]:
    """Parse layout string to rows and columns."""
    rows, cols = map(int, layout.split("x"))
    return rows, cols
