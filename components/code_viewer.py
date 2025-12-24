"""Code viewer component for displaying generated Python code."""

import streamlit as st
from typing import Optional

from core.models import ChartConfig
from codegen import CodeGenerator


def render_code_viewer(config: ChartConfig, data_filename: str = "data.csv"):
    """
    Render the code viewer with generated Python scripts.
    
    Args:
        config: ChartConfig with visualization settings
        data_filename: Name of the data file for the script
    """
    st.markdown('<div class="section-header"><span class="material-icons-outlined">code</span><h3>Code Python</h3></div>', unsafe_allow_html=True)
    
    generator = CodeGenerator()
    
    # Tabs for different code outputs
    tab1, tab2, tab3 = st.tabs(["Plotly", "Matplotlib", "Notebook"])
    
    with tab1:
        _render_plotly_code(generator, config, data_filename)
    
    with tab2:
        _render_matplotlib_code(generator, config, data_filename)
    
    with tab3:
        _render_notebook_code(generator, config, data_filename)


def _render_plotly_code(generator: CodeGenerator, config: ChartConfig, data_filename: str):
    """Render Plotly code."""
    code = generator.generate_plotly_script(config, data_filename)
    
    st.code(code, language="python", line_numbers=True)
    
    st.download_button(
        label="Télécharger le script Plotly",
        data=code,
        file_name="figure_plotly.py",
        mime="text/x-python",
        use_container_width=True,
    )


def _render_matplotlib_code(generator: CodeGenerator, config: ChartConfig, data_filename: str):
    """Render Matplotlib code."""
    code = generator.generate_matplotlib_script(config, data_filename)
    
    st.code(code, language="python", line_numbers=True)
    
    st.download_button(
        label="Télécharger le script Matplotlib",
        data=code,
        file_name="figure_matplotlib.py",
        mime="text/x-python",
        use_container_width=True,
    )


def _render_notebook_code(generator: CodeGenerator, config: ChartConfig, data_filename: str):
    """Render combined notebook-style code."""
    code = generator.get_full_notebook(config, data_filename)
    
    st.code(code, language="python", line_numbers=True)
    
    st.download_button(
        label="Télécharger le notebook (.py)",
        data=code,
        file_name="figure_notebook.py",
        mime="text/x-python",
        use_container_width=True,
    )
    
    st.info("Ce fichier peut être ouvert comme notebook dans VS Code ou JupyterLab (format percent)")
