"""Chart preview component with real-time rendering."""

import streamlit as st
import pandas as pd
from typing import Optional
import plotly.graph_objects as go

from core.models import ChartConfig
from viz import VizEngine


def render_chart_preview(
    df: pd.DataFrame, 
    config: ChartConfig,
    key_suffix: str = "",
) -> Optional[go.Figure]:
    """
    Render the chart preview with real-time updates.
    
    Args:
        df: DataFrame with the data
        config: ChartConfig with visualization settings
        key_suffix: Suffix for unique keys
        
    Returns:
        Plotly Figure if successful, None otherwise
    """
    st.markdown('<div class="section-header"><span class="material-icons-outlined">preview</span><h3>Aperçu</h3></div>', unsafe_allow_html=True)
    
    # Validate configuration
    if not _validate_config(config):
        st.info("Configurez les axes pour voir le graphique")
        return None
    
    # Create visualization engine
    engine = VizEngine()
    
    # Render tabs for different backends
    tab1, tab2 = st.tabs(["Plotly (Interactif)", "Matplotlib (Publication)"])
    
    plotly_fig = None
    
    with tab1:
        plotly_fig = _render_plotly_preview(engine, df, config, key_suffix)
    
    with tab2:
        _render_matplotlib_preview(engine, df, config, key_suffix)
    
    return plotly_fig


def _validate_config(config: ChartConfig) -> bool:
    """Check if configuration is valid for rendering."""
    # Heatmap needs multiple y columns
    if config.chart_type.value == "heatmap":
        return len(config.y_columns) >= 2
    
    # Histogram only needs x
    if config.chart_type.value == "histogram":
        return config.x_column is not None
    
    # Most charts need at least x or y
    return config.x_column is not None or len(config.y_columns) > 0


def _render_plotly_preview(
    engine: VizEngine,
    df: pd.DataFrame,
    config: ChartConfig,
    key_suffix: str,
) -> Optional[go.Figure]:
    """Render Plotly interactive preview."""
    try:
        fig = engine.create_plotly_figure(df, config)
        
        if fig is None:
            st.error(f"{engine.last_error}")
            return None
        
        # Update layout for better display
        fig.update_layout(
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
        )
        
        # Display the figure
        st.plotly_chart(fig, use_container_width=True, key=f"plotly_chart{key_suffix}")
        
        return fig
        
    except Exception as e:
        st.error(f"Erreur de rendu: {str(e)}")
        return None


def _render_matplotlib_preview(
    engine: VizEngine,
    df: pd.DataFrame,
    config: ChartConfig,
    key_suffix: str,
):
    """Render Matplotlib static preview."""
    try:
        fig = engine.create_matplotlib_figure(df, config)
        
        if fig is None:
            st.error(f"{engine.last_error}")
            return
        
        # Display the figure
        st.pyplot(fig, use_container_width=True)
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
        
    except Exception as e:
        st.error(f"Erreur Matplotlib: {str(e)}")


def render_comparison_view(
    df: pd.DataFrame,
    configs: list[ChartConfig],
):
    """
    Render multiple charts side by side for comparison.
    
    Args:
        df: DataFrame with the data
        configs: List of ChartConfig to compare
    """
    st.markdown('<div class="section-header"><span class="material-icons-outlined">compare</span><h3>Comparaison</h3></div>', unsafe_allow_html=True)
    
    if len(configs) < 2:
        st.info("Ajoutez au moins 2 configurations pour comparer")
        return
    
    engine = VizEngine()
    
    # Create columns for side by side display
    cols = st.columns(min(len(configs), 3))
    
    for i, config in enumerate(configs[:3]):
        with cols[i]:
            st.markdown(f"**Configuration {i+1}**")
            st.caption(f"{config.chart_type.value} - {config.theme}")
            
            fig = engine.create_plotly_figure(df, config)
            if fig:
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key=f"compare_{i}")
