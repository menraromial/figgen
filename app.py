"""
FigGen - Scientific Figure Generator
A professional web application for creating publication-ready scientific figures.
100% Python - No code required.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from components import (
    render_file_uploader,
    render_data_explorer,
    render_chart_config,
    render_chart_preview,
    render_export_panel,
    render_code_viewer,
)
from components.data_filter import render_data_filter
from components.template_panel import render_template_panel
from components.annotation_panel import render_annotation_panel
from components.dashboard import render_dashboard_mode
from core import DataProfile
from viz import VizEngine


# Page configuration
st.set_page_config(
    page_title="FigGen - Scientific Figure Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean minimal CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    /* Base typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Minimal header */
    .main-header {
        border-bottom: 1px solid #e5e7eb;
        padding: 1rem 0 1.5rem 0;
        margin-bottom: 1.5rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #111827;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        margin: 0.25rem 0 0 0;
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #fafafa;
        border-right: 1px solid #e5e7eb;
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e5e7eb;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: #6b7280;
        border-radius: 0;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #111827;
        border-bottom: 2px solid #111827;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1rem 0;
    }
    
    /* Subtle buttons */
    .stButton > button {
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border: 1px solid #d1d5db;
        background: white;
        color: #374151;
        transition: all 0.15s ease;
    }
    
    .stButton > button:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: #111827;
        color: white;
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1f2937;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        background: #111827;
        color: white;
        border: none;
    }
    
    .stDownloadButton > button:hover {
        background: #1f2937;
    }
    
    /* Clean metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 1px dashed #d1d5db;
        border-radius: 8px;
        padding: 1rem;
        background: #fafafa;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #9ca3af;
    }
    
    /* Clean inputs */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 6px;
    }
    
    .stTextInput input, .stNumberInput input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 0.875rem;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #111827;
        box-shadow: none;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
    }
    
    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Alerts */
    .stAlert {
        border-radius: 6px;
        font-size: 0.875rem;
    }
    
    /* Sticky preview column - stays visible when scrolling config */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        position: sticky;
        top: 60px;
        align-self: flex-start;
        max-height: calc(100vh - 80px);
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Clean header
    st.markdown("""
    <div class="main-header">
        <h1>FigGen</h1>
        <p>Générateur de figures scientifiques</p>
    </div>
    """, unsafe_allow_html=True)

    
    # Initialize session state
    if "df" not in st.session_state:
        st.session_state.df = None
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "config" not in st.session_state:
        st.session_state.config = None
    if "fig" not in st.session_state:
        st.session_state.fig = None
    
    # Sidebar: Data loading and exploration
    with st.sidebar:
        st.markdown("**Données**")
        
        # File upload
        df = render_file_uploader()
        
        if df is not None:
            st.session_state.df = df
        
        # Data explorer (if data loaded)
        if st.session_state.df is not None:
            st.markdown("---")
            profile = render_data_explorer(st.session_state.df)
            st.session_state.profile = profile
    
    # Main content area
    if st.session_state.df is not None and st.session_state.profile is not None:
        # Data filtering
        filtered_df = render_data_filter(st.session_state.df)
        
        # Mode toggle
        mode = st.radio(
            "Mode",
            options=["Graphique unique", "Dashboard"],
            horizontal=True,
            key="app_mode",
        )
        
        if mode == "Dashboard":
            # Dashboard mode - handles its own config and rendering
            from viz.viz_engine import VizEngine
            engine = VizEngine()
            render_dashboard_mode(filtered_df, st.session_state.profile, engine)
        else:
            # Single chart mode - mark as not dashboard
            st.session_state.dashboard_mode = False
            
            # Two-column layout: Config + Preview
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Template panel
                loaded_template = render_template_panel(st.session_state.config)
                if loaded_template:
                    st.session_state.config = loaded_template
                
                # Chart configuration
                config = render_chart_config(
                    filtered_df, 
                    st.session_state.profile
                )
                st.session_state.config = config
                
                # Annotation panel
                annotations = render_annotation_panel()
                if annotations and st.session_state.config:
                    st.session_state.config.annotations = annotations
            
            with col2:
                # Chart preview
                if st.session_state.config:
                    fig = render_chart_preview(
                        filtered_df,
                        st.session_state.config
                    )
                    st.session_state.fig = fig
        
        # Bottom section: Unified Export Panel (works for both modes)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export panel - adapts to current mode
            is_dashboard = st.session_state.get("dashboard_mode", False)
            if is_dashboard:
                # Dashboard export
                render_export_panel(
                    st.session_state.df,
                    None,  # No single config
                    None,  # No single fig
                    is_dashboard=True,
                )
            elif st.session_state.config and st.session_state.fig:
                render_export_panel(
                    st.session_state.df,
                    st.session_state.config,
                    st.session_state.fig,
                    is_dashboard=False,
                )
        
        with col2:
            # Code viewer
            if st.session_state.config:
                render_code_viewer(st.session_state.config)
    
    else:
        # Welcome screen when no data loaded
        _render_welcome_screen()


def _render_welcome_screen():
    """Render the welcome screen with instructions."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## Bienvenue
        
        **FigGen** est un outil pour créer des graphiques scientifiques 
        de haute qualité sans écrire de code.
        
        ### Pour commencer
        
        1. Chargez vos données via le panneau latéral
        2. Explorez la structure de vos données
        3. Configurez votre graphique
        4. Exportez en PNG, SVG, PDF ou téléchargez le code Python
        
        ---
        
        ### Fonctionnalités
        
        | Fonctionnalité | Description |
        |----------------|-------------|
        | Multi-format | CSV, JSON, YAML, Excel, Parquet |
        | Auto-détection | Types de colonnes, données temporelles |
        | 20 types de graphiques | Lignes, scatter, barres, heatmaps... |
        | Thèmes publication | Nature, Science, IEEE |
        | Code reproductible | Scripts Python prêts à l'emploi |
        | Export HD | PNG, SVG, PDF jusqu'à 600 DPI |
        
        ---
        
        Cliquez sur **Charger des données d'exemple** dans le panneau latéral 
        pour tester l'application.
        """)


if __name__ == "__main__":
    main()
