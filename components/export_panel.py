"""Export panel component for downloading figures and code."""

import streamlit as st
import pandas as pd
from typing import Optional
import plotly.graph_objects as go
import io
import re
from datetime import datetime

from core.models import ChartConfig, ExportConfig, ExportFormat
from viz import VizEngine
from codegen import CodeGenerator


def render_export_panel(
    df: pd.DataFrame,
    config: Optional[ChartConfig] = None,
    fig: Optional[go.Figure] = None,
    is_dashboard: bool = False,
):
    """
    Render the export panel with download options.
    Adapts to single chart or dashboard mode.
    
    Args:
        df: DataFrame with the data
        config: ChartConfig with visualization settings (None for dashboard)
        fig: Optional pre-rendered Plotly figure (None for dashboard)
        is_dashboard: If True, export dashboard grid instead of single chart
    """
    st.markdown("### Export")
    
    if is_dashboard:
        # Dashboard mode
        _render_dashboard_export(df)
    elif fig is None:
        st.info("Creez d'abord un graphique pour l'exporter")
        return
    else:
        # Single chart mode
        # Export format tabs
        tab1, tab2, tab3 = st.tabs(["Image", "Configuration", "Donnees"])
        
        with tab1:
            _render_image_export(df, fig, config)
        
        with tab2:
            _render_config_export(config)
        
        with tab3:
            _render_data_export(df)


def _render_image_export(df: pd.DataFrame, fig: go.Figure, config: ChartConfig):
    """Render image export options."""
    st.markdown("##### Format d'export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Backend selection
        backend = st.radio(
            "Moteur de rendu",
            options=["Plotly (Interactif)", "Matplotlib (Publication)"],
            key="export_backend",
            horizontal=True,
        )
        
        format_option = st.selectbox(
            "Format",
            options=["PNG", "SVG", "PDF"] + (["HTML"] if "Plotly" in backend else []),
            key="export_format",
        )
        
        width = st.number_input("Largeur (px)", 400, 4000, 1200, key="export_width")
    
    with col2:
        dpi = st.selectbox("Résolution (DPI)", [72, 150, 300, 600], index=2, key="export_dpi")
        height = st.number_input("Hauteur (px)", 300, 3000, 800, key="export_height")
    
    st.markdown("---")
    
    # Generate filename
    filename = _generate_filename(config.title, format_option.lower())
    st.text_input("Nom du fichier", value=filename, key="export_filename", disabled=True)
    
    # Export button
    if "Plotly" in backend:
        _export_plotly(fig, config, format_option, width, height, dpi, filename)
    else:
        _export_matplotlib(df, config, format_option, width, height, dpi, filename)


def _export_plotly(fig: go.Figure, config: ChartConfig, format_option: str, 
                   width: int, height: int, dpi: int, filename: str):
    """Export using Plotly backend."""
    if format_option == "HTML":
        html_content = fig.to_html(include_plotlyjs=True)
        st.download_button(
            label="Télécharger HTML (Interactif)",
            data=html_content,
            file_name=filename,
            mime="text/html",
            use_container_width=True,
        )
    else:
        try:
            img_bytes = fig.to_image(
                format=format_option.lower(),
                width=width,
                height=height,
                scale=dpi / 100,
            )
            
            mime_types = {
                "PNG": "image/png",
                "SVG": "image/svg+xml",
                "PDF": "application/pdf",
            }
            
            st.download_button(
                label=f"Télécharger {format_option} (Plotly)",
                data=img_bytes,
                file_name=filename,
                mime=mime_types[format_option],
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Erreur d'export Plotly: {str(e)}")
            st.info("Pour l'export d'images, installez: `pip install kaleido`")


def _export_matplotlib(df: pd.DataFrame, config: ChartConfig, format_option: str,
                       width: int, height: int, dpi: int, filename: str):
    """Export using Matplotlib backend (publication-ready)."""
    try:
        engine = VizEngine()
        mpl_fig = engine.create_matplotlib_figure(df, config)
        
        if mpl_fig is None:
            st.error(f"Erreur: {engine.last_error}")
            return
        
        # Set figure size based on width/height
        mpl_fig.set_size_inches(width / dpi, height / dpi)
        
        # Export to bytes
        buffer = io.BytesIO()
        mpl_fig.savefig(
            buffer,
            format=format_option.lower(),
            dpi=dpi,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none',
        )
        buffer.seek(0)
        
        # Clean up matplotlib figure
        import matplotlib.pyplot as plt
        plt.close(mpl_fig)
        
        mime_types = {
            "PNG": "image/png",
            "SVG": "image/svg+xml",
            "PDF": "application/pdf",
        }
        
        st.download_button(
            label=f"Télécharger {format_option} (Publication)",
            data=buffer.getvalue(),
            file_name=filename,
            mime=mime_types[format_option],
            use_container_width=True,
        )
        
        st.success("Figure publication-ready générée avec Matplotlib")
        
    except Exception as e:
        st.error(f"Erreur d'export Matplotlib: {str(e)}")


def _render_config_export(config: ChartConfig):
    """Render configuration export options."""
    st.markdown("##### Sauvegarder la configuration")
    
    # Generate config filename
    config_filename = _generate_filename(config.title, "json", prefix="config_")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        json_config = config.to_json()
        st.download_button(
            label="Configuration JSON",
            data=json_config,
            file_name=config_filename,
            mime="application/json",
            use_container_width=True,
        )
    
    with col2:
        # YAML export
        yaml_config = config.to_yaml()
        yaml_filename = config_filename.replace(".json", ".yaml")
        st.download_button(
            label="Configuration YAML",
            data=yaml_config,
            file_name=yaml_filename,
            mime="text/yaml",
            use_container_width=True,
        )
    
    st.markdown("---")
    st.markdown("##### Charger une configuration")
    
    uploaded_config = st.file_uploader(
        "Importer une configuration",
        type=["json", "yaml", "yml"],
        key="config_upload",
    )
    
    if uploaded_config:
        try:
            content = uploaded_config.read().decode("utf-8")
            if uploaded_config.name.endswith(".json"):
                loaded_config = ChartConfig.from_json(content)
            else:
                loaded_config = ChartConfig.from_yaml(content)
            
            st.success("Configuration chargée!")
            st.json(loaded_config.model_dump())
            
            # Store in session state for use
            st.session_state["loaded_config"] = loaded_config
            
        except Exception as e:
            st.error(f"Erreur de chargement: {str(e)}")


def _render_data_export(df: pd.DataFrame):
    """Render data export options."""
    st.markdown("##### Exporter les données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Données CSV",
            data=csv_data,
            file_name="figgen_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    
    with col2:
        # Excel export
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        
        st.download_button(
            label="Données Excel",
            data=buffer.getvalue(),
            file_name="figgen_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def _generate_filename(title: str, extension: str, prefix: str = "figure_") -> str:
    """
    Generate a proper filename from title.
    
    Args:
        title: Chart title
        extension: File extension (without dot)
        prefix: Prefix for the filename
        
    Returns:
        Sanitized filename with extension
    """
    # Start with the title or a default
    if not title or title.strip() == "" or title.lower() == "figure":
        # Use timestamp for unique naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{prefix}{timestamp}"
    else:
        # Sanitize the title
        base_name = title.strip()
        # Remove invalid characters
        base_name = re.sub(r'[<>:"/\\|?*]', '', base_name)
        # Replace spaces and special chars with underscores
        base_name = re.sub(r'[\s\-]+', '_', base_name)
        # Remove consecutive underscores
        base_name = re.sub(r'_+', '_', base_name)
        # Remove leading/trailing underscores
        base_name = base_name.strip('_')
        # Limit length
        base_name = base_name[:50] if len(base_name) > 50 else base_name
        # Add prefix if title doesn't start with it
        if prefix and not base_name.lower().startswith(prefix.lower().rstrip('_')):
            base_name = f"{prefix}{base_name}"
    
    # Ensure we have a valid base name
    if not base_name:
        base_name = f"{prefix}export"
    
    return f"{base_name}.{extension}"


def _render_dashboard_export(df: pd.DataFrame) -> None:
    """Render export options for dashboard mode."""
    from io import BytesIO
    import matplotlib.pyplot as plt
    from core.models import ChartConfig, ChartType, AxisConfig, GridConfig, LegendConfig
    
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
        num_rows = st.session_state.get("dashboard_num_rows", 1)
        num_cols = st.session_state.get("dashboard_num_cols", 2)
        
        # Create figure
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
        
        engine = VizEngine()
        configs = st.session_state.get("dashboard_configs", {})
        
        for row in range(num_rows):
            for col in range(num_cols):
                chart_idx = row * num_cols + col
                ax = axes[row][col]
                
                config_dict = configs.get(chart_idx, {})
                
                if not config_dict or not config_dict.get("y_columns"):
                    ax.text(0.5, 0.5, f"Graphique {chart_idx + 1}\n(non configure)", 
                           ha='center', va='center', fontsize=12, color='gray',
                           transform=ax.transAxes)
                    ax.axis('off')
                    continue
                
                try:
                    config = ChartConfig(
                        chart_type=ChartType(config_dict["chart_type"]),
                        x_column=config_dict.get("x_column"),
                        y_columns=config_dict.get("y_columns", []),
                        y2_columns=config_dict.get("y2_columns", []),
                        title=config_dict.get("title", ""),
                        color_column=config_dict.get("color_column"),
                        marker_size=config_dict.get("marker_size", 8.0),
                        line_width=config_dict.get("line_width", 2.0),
                        opacity=config_dict.get("opacity", 0.8),
                        x_axis=AxisConfig(label=config_dict.get("x_label", "")),
                        y_axis=AxisConfig(label=config_dict.get("y_label", "")),
                    )
                    
                    # Create mini figure and copy to ax
                    mini_fig = engine.create_matplotlib_figure(df, config)
                    if mini_fig and mini_fig.axes:
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
                        
                        # Copy labels
                        ax.set_xlabel(mini_ax.get_xlabel())
                        ax.set_ylabel(mini_ax.get_ylabel())
                        ax.set_title(mini_ax.get_title())
                        ax.set_xlim(mini_ax.get_xlim())
                        ax.set_ylim(mini_ax.get_ylim())
                        
                        if mini_ax.get_legend():
                            ax.legend()
                        
                        plt.close(mini_fig)
                except Exception as e:
                    ax.text(0.5, 0.5, f"Erreur", ha='center', va='center', 
                           fontsize=10, color='red', transform=ax.transAxes)
        
        plt.tight_layout()
        
        # Export
        buf = BytesIO()
        format_lower = export_format.lower()
        
        if format_lower == "pdf":
            fig.savefig(buf, format='pdf', bbox_inches='tight', dpi=dpi)
            mime = "application/pdf"
        elif format_lower == "svg":
            fig.savefig(buf, format='svg', bbox_inches='tight')
            mime = "image/svg+xml"
        elif format_lower == "eps":
            fig.savefig(buf, format='eps', bbox_inches='tight')
            mime = "application/postscript"
        else:
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
            mime = "image/png"
        
        buf.seek(0)
        plt.close(fig)
        
        st.download_button(
            label=f"Telecharger Dashboard.{format_lower}",
            data=buf.getvalue(),
            file_name=f"dashboard.{format_lower}",
            mime=mime,
            key="download_dashboard_file",
        )

