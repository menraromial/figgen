"""Annotation panel component for adding text, arrows, shapes to charts."""

import streamlit as st
from typing import Optional
from core.models import AnnotationConfig, AnnotationType, ArrowHeadStyle


def render_annotation_panel() -> list[AnnotationConfig]:
    """
    Render the annotation panel for adding annotations to charts.
    
    Returns:
        List of annotation configurations
    """
    annotations = []
    
    # Initialize session state for annotations
    # Check if annotations were loaded from a config file
    if "annotations" in st.session_state and st.session_state.annotations:
        st.session_state.chart_annotations = list(st.session_state.annotations)
        del st.session_state["annotations"]  # Clear to avoid re-loading
    elif "chart_annotations" not in st.session_state:
        st.session_state.chart_annotations = []
    
    with st.expander("Annotations", expanded=False):
        # Add new annotation
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ann_type = st.selectbox(
                "Type",
                options=[t.value for t in AnnotationType],
                format_func=lambda x: {
                    "text": "Texte",
                    "arrow": "Flèche",
                    "line": "Ligne",
                    "rect": "Rectangle",
                    "vline": "Ligne verticale",
                    "hline": "Ligne horizontale",
                }.get(x, x),
                key="ann_type_select"
            )
        
        with col2:
            if st.button("Ajouter", key="add_annotation", use_container_width=True):
                new_ann = AnnotationConfig(
                    type=AnnotationType(ann_type),
                    text="Annotation" if ann_type in ["text", "arrow"] else "",
                    x=50,
                    y=50,
                    x_end=100 if ann_type in ["arrow", "line", "rect"] else None,
                    y_end=100 if ann_type in ["arrow", "line", "rect"] else None,
                )
                st.session_state.chart_annotations.append(new_ann)
                st.rerun()
        
        # Display and edit existing annotations
        if st.session_state.chart_annotations:
            st.markdown("---")
            
            to_delete = []
            
            for i, ann in enumerate(st.session_state.chart_annotations):
                st.markdown(f"**{i+1}. {_get_type_label(ann.type)}**")
                
                # Delete button
                col_del = st.columns([4, 1])
                with col_del[1]:
                    if st.button("Suppr", key=f"del_ann_{i}", use_container_width=True):
                        to_delete.append(i)
                
                # Type-specific controls
                if ann.type in [AnnotationType.TEXT, AnnotationType.ARROW]:
                    text = st.text_input(
                        "Texte",
                        value=ann.text,
                        key=f"ann_text_{i}",
                    )
                    st.session_state.chart_annotations[i].text = text
                
                # Position controls based on type
                if ann.type == AnnotationType.TEXT:
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.number_input("X", value=float(ann.x), key=f"ann_x_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x = x
                    with col2:
                        y = st.number_input("Y", value=float(ann.y), key=f"ann_y_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y = y
                
                elif ann.type == AnnotationType.ARROW:
                    st.caption("Pointe de la flèche")
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.number_input("X (pointe)", value=float(ann.x), key=f"ann_x_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x = x
                    with col2:
                        y = st.number_input("Y (pointe)", value=float(ann.y), key=f"ann_y_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y = y
                    
                    st.caption("Origine de la flèche")
                    col1, col2 = st.columns(2)
                    with col1:
                        x_end = st.number_input("X (origine)", value=float(ann.x_end if ann.x_end is not None else ann.x - 20), key=f"ann_xe_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x_end = x_end
                    with col2:
                        y_end = st.number_input("Y (origine)", value=float(ann.y_end if ann.y_end is not None else ann.y - 20), key=f"ann_ye_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y_end = y_end
                    
                    # Arrow head style
                    head_style = st.selectbox(
                        "Style de tête",
                        options=[s.value for s in ArrowHeadStyle],
                        index=[s.value for s in ArrowHeadStyle].index(ann.arrow_head_style.value) if hasattr(ann, 'arrow_head_style') else 0,
                        format_func=lambda x: {
                            "triangle": "Triangle ▶",
                            "open": "Ouverte >",
                            "none": "Aucune —",
                            "circle": "Cercle ●",
                            "square": "Carré ■",
                            "diamond": "Losange ◆",
                        }.get(x, x),
                        key=f"ann_head_{i}",
                    )
                    st.session_state.chart_annotations[i].arrow_head_style = ArrowHeadStyle(head_style)
                
                elif ann.type == AnnotationType.LINE:
                    st.caption("Point de départ")
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.number_input("X1", value=float(ann.x), key=f"ann_x_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x = x
                    with col2:
                        y = st.number_input("Y1", value=float(ann.y), key=f"ann_y_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y = y
                    
                    st.caption("Point d'arrivée")
                    col1, col2 = st.columns(2)
                    with col1:
                        x_end = st.number_input("X2", value=float(ann.x_end if ann.x_end is not None else ann.x + 20), key=f"ann_xe_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x_end = x_end
                    with col2:
                        y_end = st.number_input("Y2", value=float(ann.y_end if ann.y_end is not None else ann.y), key=f"ann_ye_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y_end = y_end
                
                elif ann.type == AnnotationType.RECT:
                    st.caption("Position (coin haut-gauche)")
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.number_input("X", value=float(ann.x), key=f"ann_x_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].x = x
                    with col2:
                        y = st.number_input("Y", value=float(ann.y), key=f"ann_y_{i}", format="%.1f")
                        st.session_state.chart_annotations[i].y = y
                    
                    st.caption("Dimensions")
                    col1, col2 = st.columns(2)
                    
                    # Calculate current width/height
                    current_width = (ann.x_end if ann.x_end is not None else ann.x + 10) - ann.x
                    current_height = (ann.y_end if ann.y_end is not None else ann.y + 10) - ann.y
                    
                    with col1:
                        width = st.number_input("Largeur", value=float(abs(current_width)), min_value=0.1, key=f"ann_w_{i}", format="%.1f")
                    with col2:
                        height = st.number_input("Hauteur", value=float(abs(current_height)), min_value=0.1, key=f"ann_h_{i}", format="%.1f")
                    
                    # Update x_end and y_end based on width/height
                    st.session_state.chart_annotations[i].x_end = ann.x + width
                    st.session_state.chart_annotations[i].y_end = ann.y + height
                
                elif ann.type == AnnotationType.VLINE:
                    x = st.number_input("Position X", value=float(ann.x), key=f"ann_x_{i}", format="%.1f")
                    st.session_state.chart_annotations[i].x = x
                    
                    text = st.text_input("Label (optionnel)", value=ann.text or "", key=f"ann_text_{i}")
                    st.session_state.chart_annotations[i].text = text
                
                elif ann.type == AnnotationType.HLINE:
                    y = st.number_input("Position Y", value=float(ann.y), key=f"ann_y_{i}", format="%.1f")
                    st.session_state.chart_annotations[i].y = y
                    
                    text = st.text_input("Label (optionnel)", value=ann.text or "", key=f"ann_text_{i}")
                    st.session_state.chart_annotations[i].text = text
                
                # Color picker for all types
                col1, col2 = st.columns(2)
                with col1:
                    color = st.color_picker("Couleur", value=ann.color, key=f"ann_color_{i}")
                    st.session_state.chart_annotations[i].color = color
                
                with col2:
                    if ann.type in [AnnotationType.TEXT, AnnotationType.ARROW]:
                        font_size = st.number_input("Taille police", value=ann.font_size, min_value=6, max_value=48, key=f"ann_fs_{i}")
                        st.session_state.chart_annotations[i].font_size = font_size
                
                # Advanced styling expander
                with st.expander("Style avancé", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        opacity = st.slider("Opacité", 0.0, 1.0, float(ann.opacity if hasattr(ann, 'opacity') else 1.0), 
                                           step=0.1, key=f"ann_opacity_{i}")
                        st.session_state.chart_annotations[i].opacity = opacity
                        
                        line_width = st.number_input(
                            "Épaisseur ligne", 
                            value=float(ann.line_width if hasattr(ann, 'line_width') else 2.0),
                            min_value=0.1, max_value=20.0, step=0.1, format="%.1f",
                            key=f"ann_lw_{i}",
                            help="Valeurs < 1 possibles pour traits fins"
                        )
                        st.session_state.chart_annotations[i].line_width = line_width
                    
                    with col2:
                        if ann.type in [AnnotationType.TEXT, AnnotationType.RECT]:
                            # Background color
                            use_bg = st.checkbox("Fond coloré", value=ann.background_color is not None if hasattr(ann, 'background_color') else False, 
                                                key=f"ann_use_bg_{i}")
                            if use_bg:
                                bg_color = st.color_picker("Couleur fond", value=ann.background_color or "#FFFFFF", key=f"ann_bg_{i}")
                                st.session_state.chart_annotations[i].background_color = bg_color
                                
                                bg_opacity = st.slider("Opacité fond", 0.0, 1.0, 
                                                      float(ann.background_opacity if hasattr(ann, 'background_opacity') else 0.3),
                                                      step=0.1, key=f"ann_bg_opacity_{i}")
                                st.session_state.chart_annotations[i].background_opacity = bg_opacity
                            else:
                                st.session_state.chart_annotations[i].background_color = None
                    
                    # Border for rectangles
                    if ann.type == AnnotationType.RECT:
                        col1, col2 = st.columns(2)
                        with col1:
                            fill_opacity = st.slider("Opacité remplissage", 0.0, 1.0,
                                                    float(ann.fill_opacity if hasattr(ann, 'fill_opacity') else 0.2),
                                                    step=0.1, key=f"ann_fill_{i}")
                            st.session_state.chart_annotations[i].fill_opacity = fill_opacity
                        with col2:
                            border_width = st.number_input(
                                "Épaisseur bordure", 
                                value=float(ann.border_width if hasattr(ann, 'border_width') else 1.0),
                                min_value=0.0, max_value=20.0, step=0.1, format="%.1f",
                                key=f"ann_bw_{i}",
                                help="Valeurs < 1 possibles"
                            )
                            st.session_state.chart_annotations[i].border_width = border_width
                
                st.markdown("---")
            
            # Remove deleted annotations
            for idx in reversed(to_delete):
                st.session_state.chart_annotations.pop(idx)
                st.rerun()
        
        annotations = [ann.model_copy() for ann in st.session_state.chart_annotations]
    
    return annotations


def _get_type_label(ann_type: AnnotationType) -> str:
    """Get display label for annotation type."""
    return {
        AnnotationType.TEXT: "Texte",
        AnnotationType.ARROW: "Flèche",
        AnnotationType.LINE: "Ligne",
        AnnotationType.RECT: "Rectangle",
        AnnotationType.VLINE: "Ligne verticale",
        AnnotationType.HLINE: "Ligne horizontale",
    }.get(ann_type, str(ann_type))


def clear_annotations():
    """Clear all annotations from session state."""
    if "chart_annotations" in st.session_state:
        st.session_state.chart_annotations = []
