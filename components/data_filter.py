"""Data filtering component for interactive data filtering."""

import streamlit as st
import pandas as pd
from typing import Optional


def render_data_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render the data filtering panel.
    
    Args:
        df: Original DataFrame
        
    Returns:
        Filtered DataFrame
    """
    with st.expander("Filtres de données", expanded=False):
        filtered_df = df.copy()
        
        # Initialize filters in session state
        if "data_filters" not in st.session_state:
            st.session_state.data_filters = []
        
        # Add filter button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("+ Filtre", use_container_width=True):
                st.session_state.data_filters.append({
                    "column": df.columns[0],
                    "operator": "equals",
                    "value": ""
                })
                st.rerun()
        
        # Render existing filters
        filters_to_remove = []
        
        for i, filter_config in enumerate(st.session_state.data_filters):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                column = st.selectbox(
                    "Colonne",
                    options=df.columns.tolist(),
                    index=df.columns.tolist().index(filter_config["column"]) if filter_config["column"] in df.columns else 0,
                    key=f"filter_col_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.data_filters[i]["column"] = column
            
            with col2:
                # Determine operators based on column type
                col_dtype = df[column].dtype
                if pd.api.types.is_numeric_dtype(col_dtype):
                    operators = ["=", "≠", ">", "<", "≥", "≤"]
                    op_map = {"=": "equals", "≠": "not_equals", ">": "greater", "<": "less", "≥": "gte", "≤": "lte"}
                else:
                    operators = ["=", "≠", "contient", "commence par", "finit par"]
                    op_map = {"=": "equals", "≠": "not_equals", "contient": "contains", "commence par": "startswith", "finit par": "endswith"}
                
                reverse_map = {v: k for k, v in op_map.items()}
                current_op = reverse_map.get(filter_config["operator"], operators[0])
                
                operator = st.selectbox(
                    "Opérateur",
                    options=operators,
                    index=operators.index(current_op) if current_op in operators else 0,
                    key=f"filter_op_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.data_filters[i]["operator"] = op_map.get(operator, "equals")
            
            with col3:
                # Value input
                if pd.api.types.is_numeric_dtype(df[column].dtype):
                    value = st.number_input(
                        "Valeur",
                        value=float(filter_config["value"]) if filter_config["value"] else 0.0,
                        key=f"filter_val_{i}",
                        label_visibility="collapsed",
                    )
                else:
                    unique_values = df[column].dropna().unique().tolist()[:100]
                    value = st.text_input(
                        "Valeur",
                        value=str(filter_config["value"]),
                        key=f"filter_val_{i}",
                        label_visibility="collapsed",
                        placeholder="Valeur...",
                    )
                st.session_state.data_filters[i]["value"] = value
            
            with col4:
                if st.button("×", key=f"del_filter_{i}"):
                    filters_to_remove.append(i)
        
        # Remove filters marked for deletion
        for idx in reversed(filters_to_remove):
            st.session_state.data_filters.pop(idx)
            st.rerun()
        
        # Apply filters
        for filter_config in st.session_state.data_filters:
            col = filter_config["column"]
            op = filter_config["operator"]
            val = filter_config["value"]
            
            if val == "" or val is None:
                continue
            
            try:
                if op == "equals":
                    if pd.api.types.is_numeric_dtype(filtered_df[col].dtype):
                        filtered_df = filtered_df[filtered_df[col] == float(val)]
                    else:
                        filtered_df = filtered_df[filtered_df[col].astype(str) == str(val)]
                elif op == "not_equals":
                    if pd.api.types.is_numeric_dtype(filtered_df[col].dtype):
                        filtered_df = filtered_df[filtered_df[col] != float(val)]
                    else:
                        filtered_df = filtered_df[filtered_df[col].astype(str) != str(val)]
                elif op == "greater":
                    filtered_df = filtered_df[filtered_df[col] > float(val)]
                elif op == "less":
                    filtered_df = filtered_df[filtered_df[col] < float(val)]
                elif op == "gte":
                    filtered_df = filtered_df[filtered_df[col] >= float(val)]
                elif op == "lte":
                    filtered_df = filtered_df[filtered_df[col] <= float(val)]
                elif op == "contains":
                    filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(val), case=False, na=False)]
                elif op == "startswith":
                    filtered_df = filtered_df[filtered_df[col].astype(str).str.startswith(str(val), na=False)]
                elif op == "endswith":
                    filtered_df = filtered_df[filtered_df[col].astype(str).str.endswith(str(val), na=False)]
            except Exception:
                pass  # Skip invalid filters
        
        # Show filter results
        if st.session_state.data_filters:
            st.caption(f"{len(filtered_df):,} / {len(df):,} lignes")
    
    return filtered_df


def clear_filters():
    """Clear all data filters."""
    if "data_filters" in st.session_state:
        st.session_state.data_filters = []
