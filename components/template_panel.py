"""Template panel component for saving and loading chart configurations."""

import streamlit as st
from typing import Optional
from core.models import ChartConfig
from core.template_manager import (
    save_template, load_template, delete_template, 
    list_templates, list_presets, get_preset
)


def render_template_panel(current_config: Optional[ChartConfig] = None) -> Optional[ChartConfig]:
    """
    Render the template management panel.
    
    Args:
        current_config: Current chart configuration to save
        
    Returns:
        Loaded ChartConfig if user loads a template, None otherwise
    """
    loaded_config = None
    
    with st.expander("Templates", expanded=False):
        tab1, tab2 = st.tabs(["Charger", "Sauvegarder"])
        
        with tab1:
            # Load from presets
            st.markdown("**Préréglages**")
            presets = list_presets()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                preset_name = st.selectbox(
                    "Préréglage",
                    options=presets,
                    format_func=lambda x: {
                        "scatter_simple": "Nuage de points simple",
                        "line_clean": "Courbe propre",
                        "bar_grouped": "Barres groupées",
                        "publication_nature": "Publication Nature",
                    }.get(x, x),
                    key="preset_select",
                    label_visibility="collapsed",
                )
            with col2:
                if st.button("Appliquer", key="apply_preset", use_container_width=True):
                    loaded_config = get_preset(preset_name)
                    if loaded_config:
                        st.success("Préréglage appliqué")
            
            st.markdown("---")
            
            # Load from saved templates
            st.markdown("**Templates sauvegardés**")
            templates = list_templates()
            
            if templates:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    template_name = st.selectbox(
                        "Template",
                        options=templates,
                        key="template_select",
                        label_visibility="collapsed",
                    )
                with col2:
                    if st.button("Charger", key="load_template", use_container_width=True):
                        loaded_config = load_template(template_name)
                        if loaded_config:
                            st.success("Template chargé")
                with col3:
                    if st.button("Suppr", key="delete_template", use_container_width=True):
                        if delete_template(template_name):
                            st.success("Supprimé")
                            st.rerun()
            else:
                st.caption("Aucun template sauvegardé")
        
        with tab2:
            # Save current config
            st.markdown("**Sauvegarder la configuration actuelle**")
            
            new_name = st.text_input(
                "Nom du template",
                value="",
                key="new_template_name",
                placeholder="mon_template",
            )
            
            if st.button("Sauvegarder", key="save_template", use_container_width=True):
                if new_name and current_config:
                    # Clean name
                    clean_name = "".join(c for c in new_name if c.isalnum() or c in "_-")
                    if clean_name:
                        if save_template(clean_name, current_config):
                            st.success(f"Template '{clean_name}' sauvegardé")
                            st.rerun()
                        else:
                            st.error("Erreur lors de la sauvegarde")
                    else:
                        st.warning("Nom invalide")
                elif not new_name:
                    st.warning("Entrez un nom")
                else:
                    st.warning("Configurez d'abord un graphique")
    
    return loaded_config
