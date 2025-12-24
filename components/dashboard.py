"""Enhanced Dashboard component for multi-chart layouts with full configuration."""

import streamlit as st
import pandas as pd
from typing import Optional, List
from io import BytesIO
from core.models import ChartConfig, ChartType, AxisConfig, LegendConfig, GridConfig, DataProfile, AnnotationConfig, AnnotationType
import matplotlib.pyplot as plt


def _convert_annotations(ann_list: List[dict]) -> List[AnnotationConfig]:
    """Convert annotation dictionaries to AnnotationConfig objects."""
    result = []
    for ann in ann_list:
        if ann.get("text") or ann.get("type") in ["line", "rect"]:
            try:
                ann_type_map = {
                    "text": AnnotationType.TEXT,
                    "arrow": AnnotationType.ARROW,
                    "line": AnnotationType.LINE,
                    "rect": AnnotationType.RECT,
                }
                result.append(AnnotationConfig(
                    type=ann_type_map.get(ann.get("type", "text"), AnnotationType.TEXT),
                    text=ann.get("text", ""),
                    x=ann.get("x", 0),
                    y=ann.get("y", 0),
                ))
            except Exception:
                pass
    return result


def render_dashboard_mode(df: pd.DataFrame, profile: DataProfile, viz_engine) -> None:
    """
    Render enhanced dashboard mode with multiple configurable charts.
    
    Args:
        df: DataFrame with the data
        profile: Data profile for column information
        viz_engine: VizEngine instance for rendering
    """
    st.markdown("### Configuration du Dashboard")
    
    # Grid size controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        num_rows = st.number_input(
            "Lignes",
            min_value=1, max_value=4, value=1, step=1,
            key="dashboard_rows",
            help="Nombre de lignes dans la grille"
        )
    
    with col2:
        num_cols = st.number_input(
            "Colonnes", 
            min_value=1, max_value=4, value=2, step=1,
            key="dashboard_cols",
            help="Nombre de colonnes dans la grille"
        )
    
    with col3:
        if st.button("Reinitialiser", key="reset_dashboard"):
            if "dashboard_configs" in st.session_state:
                del st.session_state.dashboard_configs
            st.rerun()
    
    num_charts = int(num_rows) * int(num_cols)
    
    # Initialize dashboard configs
    if "dashboard_configs" not in st.session_state:
        st.session_state.dashboard_configs = {}
    
    st.markdown("---")
    
    # Chart type options
    chart_type_options = {
        "line": "Courbes",
        "scatter": "Nuage de points",
        "bar": "Barres",
        "histogram": "Histogramme",
        "area": "Aires",
        "box": "Boite a moustaches",
        "pie": "Camembert",
        "heatmap": "Carte de chaleur",
        "violin": "Violon",
        "funnel": "Entonnoir",
        "treemap": "Treemap",
        "sunburst": "Sunburst",
    }
    
    # Get columns
    numeric_cols = profile.get_numeric_columns()
    all_cols = [c.name for c in profile.columns]
    categorical_cols = profile.get_categorical_columns()
    
    # Configuration section with tabs for each chart
    st.markdown("### Configuration des graphiques")
    
    chart_tabs = st.tabs([f"Graphique {i+1}" for i in range(num_charts)])
    
    for i, tab in enumerate(chart_tabs):
        with tab:
            _render_chart_config(i, df, profile, chart_type_options, numeric_cols, all_cols, categorical_cols)
    
    st.markdown("---")
    
    # Render the chart grid preview
    st.markdown("### Apercu du Dashboard")
    
    _render_dashboard_grid(df, viz_engine, int(num_rows), int(num_cols))
    
    # Store dashboard state for unified export panel
    st.session_state.dashboard_mode = True
    st.session_state.dashboard_num_rows = int(num_rows)
    st.session_state.dashboard_num_cols = int(num_cols)


def _render_chart_config(
    chart_idx: int, 
    df: pd.DataFrame, 
    profile: DataProfile,
    chart_type_options: dict,
    numeric_cols: list,
    all_cols: list,
    categorical_cols: list
) -> None:
    """Render full configuration UI for a single chart in the dashboard."""
    
    # Basic config
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chart_type = st.selectbox(
            "Type de graphique",
            options=list(chart_type_options.keys()),
            format_func=lambda x: chart_type_options.get(x, x),
            key=f"dash_type_{chart_idx}",
        )
        
        x_col = st.selectbox(
            "Colonne X",
            options=[""] + all_cols,
            key=f"dash_x_{chart_idx}",
        )
        
        x_label = st.text_input(
            "Label axe X",
            value="",
            key=f"dash_xlabel_{chart_idx}",
        )
    
    with col2:
        title = st.text_input(
            "Titre",
            value=f"Graphique {chart_idx + 1}",
            key=f"dash_title_{chart_idx}",
        )
        
        y_cols = st.multiselect(
            "Colonnes Y",
            options=numeric_cols,
            default=[numeric_cols[0]] if numeric_cols else [],
            key=f"dash_y_{chart_idx}",
        )
        
        y_label = st.text_input(
            "Label axe Y",
            value="",
            key=f"dash_ylabel_{chart_idx}",
        )
    
    with col3:
        y2_cols = st.multiselect(
            "Colonnes Y secondaire",
            options=[c for c in numeric_cols if c not in (st.session_state.get(f"dash_y_{chart_idx}") or [])],
            key=f"dash_y2_{chart_idx}",
        )
        
        color_col = st.selectbox(
            "Colonne couleur",
            options=["Aucune"] + categorical_cols + numeric_cols,
            key=f"dash_color_{chart_idx}",
        )
        
        y2_label = st.text_input(
            "Label axe Y2",
            value="",
            key=f"dash_y2label_{chart_idx}",
        )
    
    # Advanced options - Style
    with st.expander("Style des elements", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            marker_size = st.number_input(
                "Taille marqueurs",
                min_value=0.1, max_value=50.0, value=8.0, step=0.5,
                format="%.1f",
                key=f"dash_marker_{chart_idx}",
            )
            marker_style = st.selectbox(
                "Style marqueur",
                options=["circle", "square", "diamond", "cross", "x", "triangle-up", "triangle-down", "star"],
                format_func=lambda x: {"circle": "● Cercle", "square": "■ Carre", "diamond": "◆ Losange",
                    "cross": "+ Croix", "x": "× X", "triangle-up": "▲ Triangle", 
                    "triangle-down": "▼ Triangle bas", "star": "★ Etoile"}.get(x, x),
                key=f"dash_marker_style_{chart_idx}",
            )
        
        with col2:
            line_width = st.number_input(
                "Epaisseur lignes",
                min_value=0.1, max_value=20.0, value=2.0, step=0.5,
                format="%.1f",
                key=f"dash_linewidth_{chart_idx}",
            )
            line_style = st.selectbox(
                "Style ligne",
                options=["solid", "dash", "dot", "dashdot"],
                format_func=lambda x: {"solid": "━━━ Continu", "dash": "┅┅┅ Tirets", 
                    "dot": "···· Pointille", "dashdot": "─·─ Tiret-point"}.get(x, x),
                key=f"dash_line_style_{chart_idx}",
            )
        
        with col3:
            opacity = st.slider(
                "Opacite",
                min_value=0.1, max_value=1.0, value=0.8, step=0.1,
                key=f"dash_opacity_{chart_idx}",
            )
    
    # Advanced options - Grid
    with st.expander("Grille et Axes", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            show_grid = st.checkbox("Afficher grille", value=True, key=f"dash_grid_{chart_idx}")
            grid_color = st.color_picker("Couleur grille", value="#CCCCCC", key=f"dash_grid_color_{chart_idx}")
            grid_opacity = st.slider("Opacite grille", 0.0, 1.0, 0.5, key=f"dash_grid_opacity_{chart_idx}")
        
        with col2:
            y_start_zero = st.checkbox("Axe Y commence a 0", value=False, key=f"dash_y_zero_{chart_idx}")
            y2_start_zero = st.checkbox("Axe Y2 commence a 0", value=False, key=f"dash_y2_zero_{chart_idx}")
            grid_style = st.selectbox(
                "Style grille",
                options=["solid", "dashed", "dotted", "dashdot"],
                format_func=lambda x: {"solid": "━━━ Continu", "dashed": "┅┅┅ Tirets", "dotted": "···· Pointille", "dashdot": "─·─ Tiret-point"}.get(x, x),
                key=f"dash_grid_style_{chart_idx}",
            )
    
    # Advanced options - Legend
    with st.expander("Legende", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            show_legend = st.checkbox("Afficher legende", value=True, key=f"dash_legend_{chart_idx}")
            legend_position = st.selectbox(
                "Position legende",
                options=["right", "left", "top", "bottom", "inside_top_right", "inside_top_left"],
                format_func=lambda x: {"right": "Droite", "left": "Gauche", "top": "Haut", "bottom": "Bas",
                    "inside_top_right": "Interieur haut-droite", "inside_top_left": "Interieur haut-gauche"}.get(x, x),
                key=f"dash_legend_pos_{chart_idx}",
            )
        
        with col2:
            legend_font_size = st.number_input("Taille police", min_value=6, max_value=24, value=10, key=f"dash_legend_size_{chart_idx}")
            legend_bg_alpha = st.slider("Opacite fond", 0.0, 1.0, 0.8, key=f"dash_legend_alpha_{chart_idx}")
    
    # Annotations section
    with st.expander("Annotations", expanded=False):
        from components.annotation_panel import AnnotationType
        
        ann_list = []
        num_annotations = st.number_input(
            "Nombre d'annotations",
            min_value=0, max_value=5, value=0, step=1,
            key=f"dash_num_ann_{chart_idx}",
        )
        
        for ann_idx in range(int(num_annotations)):
            st.markdown(f"**Annotation {ann_idx + 1}**")
            acol1, acol2 = st.columns(2)
            
            with acol1:
                ann_type = st.selectbox(
                    "Type",
                    options=["text", "arrow", "line", "rect"],
                    format_func=lambda x: {"text": "Texte", "arrow": "Fleche", "line": "Ligne", "rect": "Rectangle"}.get(x, x),
                    key=f"dash_ann_type_{chart_idx}_{ann_idx}",
                )
                ann_text = st.text_input("Texte", value="", key=f"dash_ann_text_{chart_idx}_{ann_idx}")
            
            with acol2:
                ann_x = st.number_input("X", value=0.0, key=f"dash_ann_x_{chart_idx}_{ann_idx}")
                ann_y = st.number_input("Y", value=0.0, key=f"dash_ann_y_{chart_idx}_{ann_idx}")
            
            ann_list.append({
                "type": ann_type,
                "text": ann_text,
                "x": ann_x,
                "y": ann_y,
            })
        
        st.session_state[f"dash_annotations_{chart_idx}"] = ann_list
    
    # Store configuration
    config_dict = {
        "chart_type": chart_type,
        "x_column": x_col if x_col else None,
        "y_columns": y_cols,
        "y2_columns": y2_cols,
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "y2_label": y2_label,
        "color_column": color_col if color_col != "Aucune" else None,
        "marker_size": marker_size,
        "marker_style": marker_style,
        "line_width": line_width,
        "line_style": line_style,
        "opacity": opacity,
        "show_grid": show_grid,
        "grid_color": grid_color,
        "grid_opacity": grid_opacity,
        "grid_style": grid_style,
        "y_start_zero": y_start_zero,
        "y2_start_zero": y2_start_zero,
        "show_legend": show_legend,
        "legend_position": legend_position,
        "legend_font_size": legend_font_size,
        "legend_bg_alpha": legend_bg_alpha,
        "annotations": ann_list,
    }
    
    st.session_state.dashboard_configs[chart_idx] = config_dict


def _render_dashboard_grid(df: pd.DataFrame, viz_engine, num_rows: int, num_cols: int) -> None:
    """Render the dashboard grid with charts."""
    
    for row in range(num_rows):
        columns = st.columns(num_cols)
        
        for col_idx, column in enumerate(columns):
            chart_idx = row * num_cols + col_idx
            
            with column:
                config_dict = st.session_state.dashboard_configs.get(chart_idx, {})
                
                if not config_dict or not config_dict.get("y_columns"):
                    st.info(f"Configurez le graphique {chart_idx + 1}")
                    continue
                
                # Build ChartConfig from stored dict
                config = _build_chart_config(config_dict)
                
                if config:
                    try:
                        # Create Matplotlib figure
                        fig = viz_engine.create_matplotlib_figure(df, config)
                        
                        if fig:
                            st.pyplot(fig, use_container_width=True)
                            plt.close(fig)  # Clean up
                        else:
                            st.error(f"Erreur: {viz_engine.get_last_error()}")
                            
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")


def _build_chart_config(config_dict: dict) -> Optional[ChartConfig]:
    """Build a ChartConfig from a config dictionary."""
    try:
        return ChartConfig(
            chart_type=ChartType(config_dict["chart_type"]),
            x_column=config_dict["x_column"],
            y_columns=config_dict["y_columns"],
            y2_columns=config_dict.get("y2_columns", []),
            title=config_dict.get("title", ""),
            color_column=config_dict.get("color_column"),
            marker_size=config_dict.get("marker_size", 8.0),
            marker_style=config_dict.get("marker_style", "circle"),
            line_width=config_dict.get("line_width", 2.0),
            line_style=config_dict.get("line_style", "solid"),
            opacity=config_dict.get("opacity", 0.8),
            x_axis=AxisConfig(
                label=config_dict.get("x_label", ""),
                show_grid=config_dict.get("show_grid", True),
            ),
            y_axis=AxisConfig(
                label=config_dict.get("y_label", ""),
                show_grid=config_dict.get("show_grid", True),
                start_zero=config_dict.get("y_start_zero", False),
            ),
            y2_axis=AxisConfig(
                label=config_dict.get("y2_label", ""),
                start_zero=config_dict.get("y2_start_zero", False),
            ),
            grid=GridConfig(
                show=config_dict.get("show_grid", True),
                color=config_dict.get("grid_color", "#CCCCCC"),
                opacity=config_dict.get("grid_opacity", 0.5),
                style=config_dict.get("grid_style", "solid"),
            ),
            legend=LegendConfig(
                show=config_dict.get("show_legend", True),
                position=config_dict.get("legend_position", "right"),
                font_size=config_dict.get("legend_font_size", 10),
                background_alpha=config_dict.get("legend_bg_alpha", 0.8),
            ),
            annotations=_convert_annotations(config_dict.get("annotations", [])),
        )
    except Exception:
        return None


def _render_dashboard_export(df: pd.DataFrame, viz_engine, num_rows: int, num_cols: int) -> None:
    """Render export options for the dashboard - same style as export_panel."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Format",
            options=["PNG", "PDF", "SVG", "EPS"],
            key="dashboard_export_format",
        )
        
        width = st.number_input("Largeur (px)", 400, 4000, 1200, key="dashboard_export_width")
    
    with col2:
        dpi = st.selectbox("Resolution (DPI)", [72, 150, 300, 600], index=2, key="dashboard_export_dpi")
        height = st.number_input("Hauteur (px)", 300, 3000, 800, key="dashboard_export_height")
    
    st.markdown("---")
    
    if st.button("Telecharger Dashboard", key="export_dashboard_btn"):
        _export_dashboard(df, viz_engine, num_rows, num_cols, export_format, width, height, dpi)


def _export_dashboard(df: pd.DataFrame, viz_engine, num_rows: int, num_cols: int, 
                     format: str, width: int, height: int, dpi: int) -> None:
    """Export the entire dashboard as a single image."""
    
    # Create figure with subplots
    fig_width = width / dpi
    fig_height = height / dpi
    
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height), dpi=dpi)
    
    # Handle single row/col case
    if num_rows == 1 and num_cols == 1:
        axes = [[axes]]
    elif num_rows == 1:
        axes = [axes]
    elif num_cols == 1:
        axes = [[ax] for ax in axes]
    
    for row in range(num_rows):
        for col in range(num_cols):
            chart_idx = row * num_cols + col
            ax = axes[row][col]
            
            config_dict = st.session_state.dashboard_configs.get(chart_idx, {})
            
            if not config_dict or not config_dict.get("y_columns"):
                ax.text(0.5, 0.5, f"Graphique {chart_idx + 1}\n(non configure)", 
                       ha='center', va='center', fontsize=12, color='gray',
                       transform=ax.transAxes)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                continue
            
            config = _build_chart_config(config_dict)
            if config:
                try:
                    # Create individual figure and extract data
                    mini_fig = viz_engine.create_matplotlib_figure(df, config)
                    if mini_fig:
                        # Copy content from mini_fig to ax
                        mini_ax = mini_fig.axes[0]
                        
                        # Copy lines
                        for line in mini_ax.get_lines():
                            ax.plot(line.get_xdata(), line.get_ydata(),
                                   color=line.get_color(),
                                   linewidth=line.get_linewidth(),
                                   linestyle=line.get_linestyle(),
                                   marker=line.get_marker(),
                                   markersize=line.get_markersize(),
                                   label=line.get_label())
                        
                        # Copy scatter
                        for coll in mini_ax.collections:
                            if hasattr(coll, 'get_offsets'):
                                offsets = coll.get_offsets()
                                if len(offsets) > 0:
                                    ax.scatter(offsets[:, 0], offsets[:, 1], 
                                              c=coll.get_facecolors(),
                                              s=coll.get_sizes())
                        
                        # Copy patches (bars, etc)
                        for patch in mini_ax.patches:
                            import copy
                            new_patch = copy.copy(patch)
                            ax.add_patch(new_patch)
                        
                        # Copy labels and title
                        ax.set_xlabel(mini_ax.get_xlabel())
                        ax.set_ylabel(mini_ax.get_ylabel())
                        ax.set_title(mini_ax.get_title())
                        ax.set_xlim(mini_ax.get_xlim())
                        ax.set_ylim(mini_ax.get_ylim())
                        
                        if mini_ax.get_legend():
                            ax.legend()
                        
                        plt.close(mini_fig)
                except Exception as e:
                    ax.text(0.5, 0.5, f"Erreur: {str(e)}", 
                           ha='center', va='center', fontsize=10, color='red',
                           transform=ax.transAxes)
    
    plt.tight_layout()
    
    # Export to bytes
    buf = BytesIO()
    format_lower = format.lower()
    
    if format_lower == "pdf":
        fig.savefig(buf, format='pdf', bbox_inches='tight', dpi=dpi)
        mime = "application/pdf"
    elif format_lower == "svg":
        fig.savefig(buf, format='svg', bbox_inches='tight')
        mime = "image/svg+xml"
    elif format_lower == "eps":
        fig.savefig(buf, format='eps', bbox_inches='tight')
        mime = "application/postscript"
    else:  # PNG
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        mime = "image/png"
    
    buf.seek(0)
    plt.close(fig)
    
    # Offer download
    st.download_button(
        label=f"Telecharger Dashboard.{format_lower}",
        data=buf.getvalue(),
        file_name=f"dashboard.{format_lower}",
        mime=mime,
        key="download_dashboard_file",
    )


def get_dashboard_layout() -> tuple[int, int]:
    """Get current dashboard layout from session state."""
    rows = st.session_state.get("dashboard_rows", 1)
    cols = st.session_state.get("dashboard_cols", 2)
    return int(rows), int(cols)
