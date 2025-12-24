"""File uploader component with drag & drop support."""

import streamlit as st
from typing import Optional, Any
import pandas as pd

from core import DataLoader


def render_file_uploader() -> Optional[pd.DataFrame]:
    """
    Render the file upload component with drag & drop.
    
    Returns:
        DataFrame if file uploaded successfully, None otherwise
    """
    st.markdown("**Charger vos données**")
    
    # Supported formats info
    st.caption("Formats: CSV, JSON, YAML, Excel, Parquet")
    
    # File uploader with drag & drop
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre fichier ici",
        type=["csv", "tsv", "json", "yaml", "yml", "xlsx", "xls", "parquet"],
        help="Taille max: 100 Mo",
        label_visibility="collapsed",
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.caption(f"**{uploaded_file.name}** ({file_size_mb:.2f} Mo)")
        
        # Check file size
        if file_size_mb > 100:
            st.error("Le fichier dépasse la limite de 100 Mo")
            return None
        
        # Load data
        loader = DataLoader()
        
        with st.spinner("Chargement..."):
            df = loader.load(uploaded_file)
        
        if df is None:
            st.error(f"{loader.last_error}")
            return None
        
        st.success(f"{len(df):,} lignes × {len(df.columns)} colonnes")
        
        return df
    
    # Sample data option
    st.markdown("---")
    st.markdown("**Données d'exemple**")
    
    if st.button("Charger l'exemple", use_container_width=True):
        return _get_sample_data()
    
    return None


def _get_sample_data() -> pd.DataFrame:
    """Generate sample data for demonstration."""
    import numpy as np
    
    np.random.seed(42)
    n = 100
    
    # Create sample DataFrame
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="D"),
        "temperature": 20 + 10 * np.sin(np.linspace(0, 4 * np.pi, n)) + np.random.randn(n) * 2,
        "humidity": 50 + 20 * np.cos(np.linspace(0, 4 * np.pi, n)) + np.random.randn(n) * 5,
        "category": np.random.choice(["A", "B", "C", "D"], n),
        "value": np.random.exponential(10, n),
        "score": np.random.randint(0, 100, n),
    })
    
    return df
