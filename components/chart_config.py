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
    # Check for pending config to load BEFORE widgets are created
    if st.session_state.get("pending_config_load"):
        _apply_pending_config(st.session_state["pending_config_load"], df)
        del st.session_state["pending_config_load"]
    
    st.markdown("### Configuration du graphique")
    
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
    st.markdown("**Mapping des donnees**")
    
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
    st.markdown("**Titre et labels**")
    
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
    
    # Axis label styling
    with st.expander("Style des labels d'axes", expanded=False):
        st.markdown("**Axe X**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("Taille police", min_value=2, max_value=24, value=12, step=1, key="x_label_font_size")
        with col2:
            st.color_picker("Couleur", value="#000000", key="x_label_color")
        with col3:
            st.number_input("Rotation", min_value=-90.0, max_value=90.0, value=0.0, step=5.0, key="x_label_rotation")
        
        st.markdown("**Axe Y**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("Taille police", min_value=2, max_value=24, value=12, step=1, key="y_label_font_size")
        with col2:
            st.color_picker("Couleur", value="#000000", key="y_label_color")
        with col3:
            st.number_input("Rotation", min_value=-90.0, max_value=90.0, value=90.0, step=5.0, key="y_label_rotation")
        
        st.markdown("**Ticks (graduations)**")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Taille X", min_value=2, max_value=18, value=10, step=1, key="x_tick_font_size")
            st.number_input("Rotation X", min_value=-90.0, max_value=90.0, value=0.0, step=5.0, key="x_tick_rotation")
        with col2:
            st.number_input("Taille Y", min_value=2, max_value=18, value=10, step=1, key="y_tick_font_size")
            st.number_input("Rotation Y", min_value=-90.0, max_value=90.0, value=0.0, step=5.0, key="y_tick_rotation")
    
    # Advanced options in expander
    with st.expander("Options avancees"):
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
        x_axis=AxisConfig(
            label=x_label, 
            show_grid=st.session_state.get("show_grid_x", True),
            label_font_size=st.session_state.get("x_label_font_size", 12),
            label_color=st.session_state.get("x_label_color", "#000000"),
            label_rotation=st.session_state.get("x_label_rotation", 0.0),
            tick_font_size=st.session_state.get("x_tick_font_size", 10),
            tick_rotation=st.session_state.get("x_tick_rotation", 0.0),
        ),
        y_axis=AxisConfig(
            label=y_label, 
            show_grid=st.session_state.get("show_grid_y", True),
            start_zero=st.session_state.get("y_start_zero", False),
            label_font_size=st.session_state.get("y_label_font_size", 12),
            label_color=st.session_state.get("y_label_color", "#000000"),
            label_rotation=st.session_state.get("y_label_rotation", 90.0),
            tick_font_size=st.session_state.get("y_tick_font_size", 10),
            tick_rotation=st.session_state.get("y_tick_rotation", 0.0),
        ),
        y2_axis=AxisConfig(
            label=st.session_state.get("y2_label", ""),
            start_zero=st.session_state.get("y2_start_zero", False),
            label_font_size=st.session_state.get("y_label_font_size", 12),
            label_color=st.session_state.get("y_label_color", "#000000"),
        ),
        legend=LegendConfig(
            show=st.session_state.get("show_legend", True),
            position=st.session_state.get("legend_position", "right"),
            orientation=st.session_state.get("legend_orientation", "vertical"),
            font_size=st.session_state.get("legend_font_size", 10),
            font_color=st.session_state.get("legend_font_color", "#000000"),
            font_family=st.session_state.get("legend_font_family", "sans-serif"),
            font_bold=st.session_state.get("legend_font_bold", False),
            background_color=st.session_state.get("legend_bg_color", "#FFFFFF"),
            background_alpha=st.session_state.get("legend_bg_alpha", 0.8),
            border_show=st.session_state.get("legend_border_show", True),
            border_color=st.session_state.get("legend_border_color", "#CCCCCC"),
            border_width=st.session_state.get("legend_border_width", 1.0),
            border_style=st.session_state.get("legend_border_style", "solid"),
            shadow_show=st.session_state.get("legend_shadow_show", False),
            shadow_color=st.session_state.get("legend_shadow_color", "#00000033"),
            shadow_offset_x=st.session_state.get("legend_shadow_x", 2.0),
            shadow_offset_y=st.session_state.get("legend_shadow_y", 2.0),
            padding=st.session_state.get("legend_padding", 5.0),
            column_spacing=st.session_state.get("legend_column_spacing", 1.0),
            marker_scale=st.session_state.get("legend_marker_scale", 1.0),
            num_columns=st.session_state.get("legend_columns", 1),
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
        y2_marker_style=st.session_state.get("y2_marker_style", "auto"),
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
    
    # Secondary axis marker style
    st.selectbox(
        "Marqueur axe Y secondaire",
        options=["auto", "circle", "square", "diamond", "cross", "x", "triangle-up", "triangle-down", "star"],
        format_func=lambda x: {
            "auto": "Automatique (différent de Y)",
            "circle": "● Cercle",
            "square": "■ Carré", 
            "diamond": "◆ Losange",
            "cross": "+ Croix",
            "x": "× X",
            "triangle-up": "▲ Triangle haut",
            "triangle-down": "▼ Triangle bas",
            "star": "★ Étoile",
        }.get(x, x),
        key="y2_marker_style",
        help="Style de marqueur pour les courbes de l'axe Y secondaire"
    )
    
    st.markdown("---")
    
    # Legend options
    st.markdown("**Legende**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Afficher la legende", value=True, key="show_legend")
        st.selectbox(
            "Position",
            options=[
                "right", "left", "top", "bottom", "top_center", "bottom_center",
                "inside_top_right", "inside_top_left", "inside_top_center",
                "inside_bottom_right", "inside_bottom_left", "inside_bottom_center"
            ],
            format_func=lambda x: {
                "right": "Droite (exterieur)",
                "left": "Gauche (exterieur)",
                "top": "Haut (exterieur)",
                "bottom": "Bas (exterieur)",
                "top_center": "Haut-centre (exterieur)",
                "bottom_center": "Bas-centre (exterieur)",
                "inside_top_right": "Haut-droite (interieur)",
                "inside_top_left": "Haut-gauche (interieur)",
                "inside_top_center": "Haut-centre (interieur)",
                "inside_bottom_right": "Bas-droite (interieur)",
                "inside_bottom_left": "Bas-gauche (interieur)",
                "inside_bottom_center": "Bas-centre (interieur)",
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
        st.number_input("Colonnes", min_value=1, max_value=5, value=1, step=1, key="legend_columns")
    
    # Legend font options
    with st.expander("Police de la legende", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input("Taille police", min_value=2, max_value=24, value=10, step=1, key="legend_font_size")
            st.color_picker("Couleur police", value="#000000", key="legend_font_color")
        
        with col2:
            st.selectbox(
                "Famille de police",
                options=["sans-serif", "serif", "monospace", "Arial", "Times New Roman", "Courier New"],
                key="legend_font_family",
            )
        
        with col3:
            st.checkbox("Gras", value=False, key="legend_font_bold")
    
    # Legend background options
    with st.expander("Fond de la legende", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.color_picker("Couleur de fond", value="#FFFFFF", key="legend_bg_color")
        
        with col2:
            st.slider("Opacite fond", 0.0, 1.0, 0.8, key="legend_bg_alpha")
    
    # Legend border options
    with st.expander("Bordure de la legende", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Afficher bordure", value=True, key="legend_border_show")
            st.color_picker("Couleur bordure", value="#CCCCCC", key="legend_border_color")
        
        with col2:
            st.number_input("Epaisseur bordure", min_value=0.1, max_value=5.0, value=1.0, step=0.1, format="%.1f", key="legend_border_width")
            st.selectbox(
                "Style bordure",
                options=["solid", "dashed", "dotted", "dashdot"],
                format_func=lambda x: {
                    "solid": "━━━ Continu",
                    "dashed": "┅┅┅ Tirets",
                    "dotted": "···· Pointille",
                    "dashdot": "─·─· Tiret-point",
                }.get(x, x),
                key="legend_border_style",
            )
    
    # Legend shadow options
    with st.expander("Ombre de la legende", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Afficher ombre", value=False, key="legend_shadow_show")
            st.color_picker("Couleur ombre", value="#666666", key="legend_shadow_color")
        
        with col2:
            st.number_input("Decalage X", min_value=0.0, max_value=20.0, value=2.0, step=0.5, format="%.1f", key="legend_shadow_x")
            st.number_input("Decalage Y", min_value=0.0, max_value=20.0, value=2.0, step=0.5, format="%.1f", key="legend_shadow_y")
    
    # Legend layout options
    with st.expander("Mise en page de la legende", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Padding", min_value=0.0, max_value=20.0, value=5.0, step=1.0, format="%.1f", key="legend_padding")
            st.number_input("Espacement colonnes", min_value=0.0, max_value=5.0, value=1.0, step=0.1, format="%.1f", key="legend_column_spacing")
        
        with col2:
            st.number_input("Echelle marqueurs", min_value=0.5, max_value=3.0, value=1.0, step=0.1, format="%.1f", key="legend_marker_scale")
    
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


def _apply_pending_config(config: ChartConfig, df: pd.DataFrame):
    """Apply pending config to session state BEFORE widgets are created."""
    all_columns = df.columns.tolist()
    
    # Basic chart settings - only set if column exists in current data
    st.session_state["chart_type"] = config.chart_type.value if hasattr(config.chart_type, 'value') else config.chart_type
    
    if config.x_column and config.x_column in all_columns:
        st.session_state["x_column"] = config.x_column
    
    if config.y_columns:
        valid_y_cols = [c for c in config.y_columns if c in all_columns]
        if valid_y_cols:
            st.session_state["y_columns"] = valid_y_cols
    
    if config.y2_columns:
        valid_y2_cols = [c for c in config.y2_columns if c in all_columns]
        if valid_y2_cols:
            st.session_state["y2_columns"] = valid_y2_cols
    
    if config.color_column and config.color_column in all_columns:
        st.session_state["color_column"] = config.color_column
    
    # Title and labels
    st.session_state["chart_title"] = config.title or ""
    if config.x_axis:
        st.session_state["x_label"] = config.x_axis.label or ""
    if config.y_axis:
        st.session_state["y_label"] = config.y_axis.label or ""
    if config.y2_axis:
        st.session_state["y2_label"] = config.y2_axis.label if config.y2_axis.label else ""
    
    # Style elements
    st.session_state["marker_size"] = config.marker_size
    st.session_state["line_width"] = config.line_width
    st.session_state["opacity"] = config.opacity
    st.session_state["marker_style"] = config.marker_style
    st.session_state["line_style"] = config.line_style
    st.session_state["y2_marker_style"] = config.y2_marker_style or "auto"
    
    # Grid settings
    if config.grid:
        st.session_state["show_grid_x"] = config.grid.show
        st.session_state["show_grid_y"] = config.grid.show
        st.session_state["grid_color"] = config.grid.color
        st.session_state["grid_width"] = config.grid.width
        st.session_state["grid_opacity"] = config.grid.opacity
        st.session_state["grid_style"] = config.grid.style
    
    # Axis settings
    if config.y_axis:
        st.session_state["y_start_zero"] = config.y_axis.start_zero
    if config.y2_axis:
        st.session_state["y2_start_zero"] = config.y2_axis.start_zero
    
    # Legend settings
    if config.legend:
        st.session_state["show_legend"] = config.legend.show
        st.session_state["legend_position"] = config.legend.position
        st.session_state["legend_orientation"] = config.legend.orientation
        st.session_state["legend_font_size"] = config.legend.font_size
        st.session_state["legend_font_color"] = config.legend.font_color
        st.session_state["legend_font_family"] = config.legend.font_family
        st.session_state["legend_font_bold"] = config.legend.font_bold
        st.session_state["legend_bg_color"] = config.legend.background_color
        st.session_state["legend_bg_alpha"] = config.legend.background_alpha
        st.session_state["legend_border_show"] = config.legend.border_show
        st.session_state["legend_border_color"] = config.legend.border_color
        st.session_state["legend_border_width"] = config.legend.border_width
        st.session_state["legend_border_style"] = config.legend.border_style
        st.session_state["legend_shadow_show"] = config.legend.shadow_show
        st.session_state["legend_shadow_color"] = config.legend.shadow_color
        st.session_state["legend_shadow_x"] = config.legend.shadow_offset_x
        st.session_state["legend_shadow_y"] = config.legend.shadow_offset_y
        st.session_state["legend_padding"] = config.legend.padding
        st.session_state["legend_column_spacing"] = config.legend.column_spacing
        st.session_state["legend_marker_scale"] = config.legend.marker_scale
        st.session_state["legend_columns"] = config.legend.num_columns
    
    # Regression settings
    if config.regression:
        st.session_state["regression_enabled"] = config.regression.enabled
        rtype = config.regression.type
        st.session_state["regression_type"] = rtype.value if hasattr(rtype, 'value') else rtype
        st.session_state["regression_degree"] = config.regression.degree
        st.session_state["regression_show_eq"] = config.regression.show_equation
        st.session_state["regression_show_r2"] = config.regression.show_r2
    
    # Theme
    if config.theme:
        st.session_state["theme"] = config.theme
    
    # Annotations - important: store directly in the loaded config  
    if config.annotations:
        st.session_state["annotations"] = config.annotations
        st.session_state["num_annotations"] = len(config.annotations)
