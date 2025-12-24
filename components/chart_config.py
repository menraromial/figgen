"""Chart configuration panel component."""

import streamlit as st
import pandas as pd
from typing import Optional

from core.models import ChartConfig, ChartType, AxisConfig, LegendConfig, DataProfile, RegressionConfig, RegressionType
from viz.themes import get_theme_names, THEMES


def render_chart_config(df: pd.DataFrame, profile: DataProfile) -> ChartConfig:
    """
    Render the chart configuration panel.
    
    Args:
        df: DataFrame with the data
        profile: DataProfile with column analysis
        
    Returns:
        ChartConfig with user selections
    """
    st.markdown('<div class="section-header"><span class="material-icons-outlined">settings</span><h3>Configuration du graphique</h3></div>', unsafe_allow_html=True)
    
    # Get column lists by type
    all_columns = df.columns.tolist()
    numeric_columns = profile.get_numeric_columns()
    categorical_columns = profile.get_categorical_columns()
    temporal_columns = profile.get_temporal_columns()
    
    # Chart type selection
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox(
            "Type de graphique",
            options=[ct.value for ct in ChartType],
            format_func=lambda x: _get_chart_label(x),
            key="chart_type",
        )
    
    with col2:
        theme = st.selectbox(
            "Thème",
            options=get_theme_names(),
            format_func=lambda x: THEMES[x]["name"],
            key="theme",
        )
    
    st.markdown("---")
    
    # Data mapping
    st.markdown('<div class="section-header"><span class="material-icons-outlined">data_object</span><span>Mapping des données</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # X axis selection
        x_options = ["(index)"] + all_columns
        x_column = st.selectbox(
            "Axe X",
            options=x_options,
            index=_get_default_x_index(chart_type, temporal_columns, categorical_columns, x_options),
            key="x_column",
        )
        if x_column == "(index)":
            x_column = None
    
    with col2:
        # Y axis selection (can be multiple for some chart types)
        if chart_type in ["line", "area"]:
            y_columns = st.multiselect(
                "Axe Y principal",
                options=numeric_columns,
                default=numeric_columns[:1] if numeric_columns else [],
                key="y_columns",
            )
        elif chart_type == "heatmap":
            y_columns = st.multiselect(
                "Variables (corrélation)",
                options=numeric_columns,
                default=numeric_columns[:5] if len(numeric_columns) >= 3 else numeric_columns,
                key="y_columns_heatmap",
            )
            if y_columns:
                x_column = "__correlation__"
        else:
            y_col = st.selectbox(
                "Axe Y",
                options=numeric_columns if numeric_columns else all_columns,
                index=0 if numeric_columns else 0,
                key="y_column_single",
            )
            y_columns = [y_col] if y_col else []
    
    # Secondary Y axis (dual axis) - only for line and scatter charts
    y2_columns = []
    if chart_type in ["line", "scatter", "area"]:
        with st.expander("Axe Y secondaire (double axe)"):
            st.caption("Ajoutez des séries sur un second axe Y pour comparer des échelles différentes")
            remaining_numeric = [c for c in numeric_columns if c not in y_columns]
            if remaining_numeric:
                y2_columns = st.multiselect(
                    "Colonnes sur axe Y secondaire",
                    options=remaining_numeric,
                    default=[],
                    key="y2_columns",
                )
                if y2_columns:
                    y2_label = st.text_input(
                        "Label axe Y secondaire",
                        value=y2_columns[0] if y2_columns else "",
                        key="y2_label",
                    )
            else:
                st.info("Toutes les colonnes numériques sont déjà sur l'axe Y principal")
                y2_label = ""
    else:
        y2_label = ""
    
    # Color and size columns
    col1, col2 = st.columns(2)
    
    with col1:
        color_options = ["(aucun)"] + categorical_columns + numeric_columns
        color_column = st.selectbox(
            "Couleur par",
            options=color_options,
            index=0,
            key="color_column",
        )
        if color_column == "(aucun)":
            color_column = None
    
    with col2:
        if chart_type in ["scatter", "bubble"]:
            size_options = ["(aucun)"] + numeric_columns
            size_column = st.selectbox(
                "Taille par",
                options=size_options,
                index=0,
                key="size_column",
            )
            if size_column == "(aucun)":
                size_column = None
        else:
            size_column = None
    
    st.markdown("---")
    
    # Title and labels
    st.markdown('<div class="section-header"><span class="material-icons-outlined">edit</span><span>Titre et labels</span></div>', unsafe_allow_html=True)
    
    title = st.text_input(
        "Titre du graphique",
        value="Figure",
        key="chart_title",
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_label = st.text_input(
            "Label axe X",
            value=x_column if x_column and x_column != "__correlation__" else "",
            key="x_label",
        )
    
    with col2:
        # Default Y label: combine all Y columns if multiple
        default_y_label = ""
        if y_columns:
            if len(y_columns) == 1:
                default_y_label = y_columns[0]
            else:
                default_y_label = " / ".join(y_columns)
        
        y_label = st.text_input(
            "Label axe Y principal",
            value=default_y_label,
            key="y_label",
        )
    
    # Advanced options in expander
    with st.expander("Options avancées"):
        _render_advanced_options()
    
    # Build config
    from core.models import GridConfig
    
    config = ChartConfig(
        chart_type=ChartType(chart_type),
        x_column=x_column,
        y_columns=y_columns,
        y2_columns=y2_columns,
        color_column=color_column,
        size_column=size_column,
        title=title,
        theme=theme,
        x_axis=AxisConfig(label=x_label, show_grid=st.session_state.get("show_grid_x", True)),
        y_axis=AxisConfig(
            label=y_label, 
            show_grid=st.session_state.get("show_grid_y", True),
            start_zero=st.session_state.get("y_start_zero", False),
        ),
        y2_axis=AxisConfig(
            label=st.session_state.get("y2_label", ""),
            start_zero=st.session_state.get("y2_start_zero", False),
        ),
        legend=LegendConfig(
            show=st.session_state.get("show_legend", True),
            position=st.session_state.get("legend_position", "right"),
            orientation=st.session_state.get("legend_orientation", "vertical"),
            font_size=st.session_state.get("legend_font_size", 10),
            background_alpha=st.session_state.get("legend_bg_alpha", 0.8),
        ),
        grid=GridConfig(
            show=st.session_state.get("show_grid_x", True) or st.session_state.get("show_grid_y", True),
            color=st.session_state.get("grid_color", "#CCCCCC"),
            width=st.session_state.get("grid_width", 1.0),
            style=st.session_state.get("grid_style", "solid"),
            opacity=st.session_state.get("grid_opacity", 0.5),
        ),
        marker_size=st.session_state.get("marker_size", 8.0),
        line_width=st.session_state.get("line_width", 2.0),
        opacity=st.session_state.get("opacity", 0.8),
        marker_style=st.session_state.get("marker_style", "circle"),
        line_style=st.session_state.get("line_style", "solid"),
        regression=RegressionConfig(
            enabled=st.session_state.get("regression_enabled", False),
            type=RegressionType(st.session_state.get("regression_type", "linear")),
            degree=st.session_state.get("regression_degree", 2),
            show_equation=st.session_state.get("regression_show_eq", True),
            show_r2=st.session_state.get("regression_show_r2", True),
        ),
    )
    
    return config


def _render_advanced_options():
    """Render advanced configuration options."""
    
    # Style options
    st.markdown("**Style des éléments**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Taille des marqueurs", 
            min_value=0.1, max_value=50.0, value=8.0, step=0.5, 
            format="%.1f",
            key="marker_size",
            help="Valeurs < 1 possibles pour traits fins"
        )
        st.selectbox(
            "Style marqueur",
            options=["circle", "square", "diamond", "cross", "x", "triangle-up", "triangle-down", "star"],
            format_func=lambda x: {
                "circle": "● Cercle",
                "square": "■ Carré", 
                "diamond": "◆ Losange",
                "cross": "+ Croix",
                "x": "× X",
                "triangle-up": "▲ Triangle haut",
                "triangle-down": "▼ Triangle bas",
                "star": "★ Étoile",
            }.get(x, x),
            key="marker_style",
        )
    
    with col2:
        st.number_input(
            "Épaisseur des lignes", 
            min_value=0.1, max_value=20.0, value=2.0, step=0.5,
            format="%.1f",
            key="line_width",
            help="Valeurs < 1 possibles pour traits fins"
        )
        st.selectbox(
            "Style ligne",
            options=["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"],
            format_func=lambda x: {
                "solid": "━━━ Continu",
                "dash": "┅┅┅ Tirets",
                "dot": "···· Pointillé",
                "dashdot": "─·─· Tiret-point",
                "longdash": "── ── Tirets longs",
                "longdashdot": "──·── Long tiret-point",
            }.get(x, x),
            key="line_style",
        )
    
    st.slider("Opacité générale", 0.1, 1.0, 0.8, key="opacity")
    
    st.markdown("---")
    
    # Grid configuration
    st.markdown("**Grille**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Grille X", value=True, key="show_grid_x")
        st.checkbox("Grille Y", value=True, key="show_grid_y")
        st.color_picker("Couleur grille", value="#CCCCCC", key="grid_color")
    
    with col2:
        st.number_input("Épaisseur grille", min_value=0.1, max_value=5.0, value=1.0, step=0.1, format="%.1f", key="grid_width")
        st.slider("Opacité grille", 0.0, 1.0, 0.5, key="grid_opacity")
        st.selectbox(
            "Style grille",
            options=["solid", "dashed", "dotted", "dashdot"],
            format_func=lambda x: {
                "solid": "━━━ Continu",
                "dashed": "┅┅┅ Tirets",
                "dotted": "···· Pointillé",
                "dashdot": "─·─· Tiret-point",
            }.get(x, x),
            key="grid_style",
        )
    
    st.markdown("---")
    
    # Axis options
    st.markdown("**Axes**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Axe Y commence à 0", value=False, key="y_start_zero")
    
    with col2:
        st.checkbox("Axe Y secondaire commence à 0", value=False, key="y2_start_zero")
    
    st.markdown("---")
    
    # Legend options
    st.markdown("**Légende**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Afficher la légende", value=True, key="show_legend")
        st.selectbox(
            "Position",
            options=[
                "right", "left", "top", "bottom", "top_center", "bottom_center",
                "inside_top_right", "inside_top_left", "inside_top_center",
                "inside_bottom_right", "inside_bottom_left", "inside_bottom_center"
            ],
            format_func=lambda x: {
                "right": "Droite (extérieur)",
                "left": "Gauche (extérieur)",
                "top": "Haut (extérieur)",
                "bottom": "Bas (extérieur)",
                "top_center": "Haut-centre (extérieur)",
                "bottom_center": "Bas-centre (extérieur)",
                "inside_top_right": "Haut-droite (intérieur)",
                "inside_top_left": "Haut-gauche (intérieur)",
                "inside_top_center": "Haut-centre (intérieur)",
                "inside_bottom_right": "Bas-droite (intérieur)",
                "inside_bottom_left": "Bas-gauche (intérieur)",
                "inside_bottom_center": "Bas-centre (intérieur)",
            }.get(x, x),
            key="legend_position",
        )
    
    with col2:
        st.selectbox(
            "Orientation",
            options=["vertical", "horizontal"],
            format_func=lambda x: "Verticale" if x == "vertical" else "Horizontale",
            key="legend_orientation",
        )
        st.number_input("Taille police légende", min_value=4, max_value=24, value=10, step=1, key="legend_font_size")
        st.slider("Opacité fond légende", 0.0, 1.0, 0.8, key="legend_bg_alpha")
    
    st.markdown("---")
    
    # Regression options
    st.markdown("**Régression / Tendance**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Afficher ligne de tendance", value=False, key="regression_enabled")
        st.selectbox(
            "Type",
            options=["linear", "polynomial"],
            format_func=lambda x: {"linear": "Linéaire", "polynomial": "Polynomiale"}.get(x, x),
            key="regression_type",
        )
    
    with col2:
        st.number_input("Degré (polynomial)", min_value=2, max_value=6, value=2, key="regression_degree")
        st.checkbox("Afficher équation", value=True, key="regression_show_eq")
        st.checkbox("Afficher R²", value=True, key="regression_show_r2")


def _get_chart_label(chart_type: str) -> str:
    """Get display label for chart type."""
    labels = {
        "line": "Courbes",
        "scatter": "Nuage de points",
        "bar": "Barres",
        "histogram": "Histogramme",
        "box": "Box plot",
        "violin": "Violin plot",
        "heatmap": "Heatmap",
        "area": "Aires",
        "pie": "Camembert",
        "bubble": "Bulles",
        "funnel": "Entonnoir",
        "treemap": "Treemap",
        "sunburst": "Sunburst",
        "radar": "Radar",
        "parallel_coords": "Coordonnées parallèles",
        "candlestick": "Chandelier (OHLC)",
        "waterfall": "Cascade",
        "polar": "Polaire",
        "contour": "Contour 2D",
        "density": "Densité 2D",
    }
    return labels.get(chart_type, chart_type)


def _get_default_x_index(
    chart_type: str,
    temporal_columns: list,
    categorical_columns: list,
    x_options: list,
) -> int:
    """Get default X column index based on chart type."""
    if chart_type in ["line", "area"] and temporal_columns:
        # Prefer temporal for line charts
        for i, opt in enumerate(x_options):
            if opt in temporal_columns:
                return i
    
    if chart_type in ["bar", "box", "violin"] and categorical_columns:
        # Prefer categorical for bar/box charts
        for i, opt in enumerate(x_options):
            if opt in categorical_columns:
                return i
    
    # Default to first column (after index)
    return 1 if len(x_options) > 1 else 0
