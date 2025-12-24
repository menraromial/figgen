"""Data explorer component for viewing and analyzing data."""

import streamlit as st
import pandas as pd
from typing import Optional

from core import DataAnalyzer, DataProfile


def render_data_explorer(df: pd.DataFrame) -> Optional[DataProfile]:
    """
    Render the data explorer component.
    
    Args:
        df: DataFrame to explore
        
    Returns:
        DataProfile with analysis results
    """
    st.markdown('<div class="section-header"><span class="material-icons-outlined">search</span><span>Exploration des données</span></div>', unsafe_allow_html=True)
    
    # Analyze data
    analyzer = DataAnalyzer()
    profile = analyzer.analyze(df)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Aperçu", "Statistiques", "Suggestions"])
    
    with tab1:
        _render_preview(df)
    
    with tab2:
        _render_statistics(df, profile)
    
    with tab3:
        _render_suggestions(profile)
    
    return profile


def _render_preview(df: pd.DataFrame):
    """Render data preview."""
    # Show sample of data
    st.markdown("##### Échantillon des données")
    st.dataframe(
        df.head(10),
        use_container_width=True,
        height=300,
    )
    
    # Quick info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes", f"{len(df):,}")
    with col2:
        st.metric("Colonnes", len(df.columns))
    with col3:
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        st.metric("Données manquantes", f"{missing_pct:.1f}%")


def _render_statistics(df: pd.DataFrame, profile: DataProfile):
    """Render column statistics."""
    st.markdown("##### Détail des colonnes")
    
    # Create stats table
    stats_data = []
    for col in profile.columns:
        stats_data.append({
            "Colonne": col.name,
            "Type": col.column_type.value,
            "Non-nuls": f"{100 - col.null_percentage:.1f}%",
            "Uniques": col.unique_count,
            "Aperçu": str(col.sample_values[:2]) if col.sample_values else "-",
        })
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Detailed stats for selected column
    st.markdown("##### Statistiques détaillées")
    selected_col = st.selectbox(
        "Sélectionnez une colonne",
        options=df.columns.tolist(),
        key="stats_column_select",
    )
    
    if selected_col:
        col_profile = next((c for c in profile.columns if c.name == selected_col), None)
        if col_profile:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Type détecté:** {col_profile.column_type.value}")
                st.markdown(f"**Type pandas:** `{col_profile.dtype}`")
                st.markdown(f"**Valeurs nulles:** {col_profile.null_count} ({col_profile.null_percentage:.1f}%)")
                st.markdown(f"**Valeurs uniques:** {col_profile.unique_count}")
            
            with col2:
                if col_profile.min_value is not None:
                    st.markdown(f"**Min:** {col_profile.min_value:.4g}")
                    st.markdown(f"**Max:** {col_profile.max_value:.4g}")
                    st.markdown(f"**Moyenne:** {col_profile.mean_value:.4g}")
                    st.markdown(f"**Écart-type:** {col_profile.std_value:.4g}")
                
                if col_profile.top_categories:
                    st.markdown("**Top catégories:**")
                    for cat, count in list(col_profile.top_categories.items())[:5]:
                        st.markdown(f"- {cat}: {count}")


def _render_suggestions(profile: DataProfile):
    """Render chart suggestions."""
    st.markdown("##### Graphiques suggérés")
    
    if profile.suggested_charts:
        for i, chart_type in enumerate(profile.suggested_charts[:5]):
            icon = _get_chart_icon(chart_type)
            st.markdown(f'{i+1}. <span class="material-icons-outlined" style="font-size:1rem;vertical-align:middle;">{icon}</span> **{chart_type.title()}**', unsafe_allow_html=True)
    else:
        st.info("Aucune suggestion disponible pour ce jeu de données")
    
    # Column type summary
    st.markdown("---")
    st.markdown("##### Résumé des types de colonnes")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_cols = len(profile.get_numeric_columns())
        st.metric("Numériques", num_cols)
    with col2:
        cat_cols = len(profile.get_categorical_columns())
        st.metric("Catégorielles", cat_cols)
    with col3:
        temp_cols = len(profile.get_temporal_columns())
        st.metric("Temporelles", temp_cols)


def _get_chart_icon(chart_type: str) -> str:
    """Get Material icon name for chart type."""
    icons = {
        "line": "show_chart",
        "scatter": "scatter_plot",
        "bar": "bar_chart",
        "histogram": "equalizer",
        "box": "candlestick_chart",
        "heatmap": "grid_on",
        "area": "area_chart",
        "pie": "pie_chart",
        "violin": "graphic_eq",
    }
    return icons.get(chart_type, "insert_chart")
