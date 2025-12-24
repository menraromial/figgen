"""Template manager for saving and loading chart configurations."""

import json
import os
from pathlib import Path
from typing import Optional
from core.models import ChartConfig


# Template storage directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def ensure_templates_dir():
    """Ensure the templates directory exists."""
    TEMPLATES_DIR.mkdir(exist_ok=True)


def save_template(name: str, config: ChartConfig) -> bool:
    """
    Save a chart configuration as a template.
    
    Args:
        name: Template name (used as filename)
        config: ChartConfig to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        ensure_templates_dir()
        filepath = TEMPLATES_DIR / f"{name}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(config.to_json())
        
        return True
    except Exception:
        return False


def load_template(name: str) -> Optional[ChartConfig]:
    """
    Load a chart configuration template.
    
    Args:
        name: Template name
        
    Returns:
        ChartConfig if loaded successfully, None otherwise
    """
    try:
        filepath = TEMPLATES_DIR / f"{name}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return ChartConfig.from_json(f.read())
    except Exception:
        return None


def delete_template(name: str) -> bool:
    """
    Delete a template.
    
    Args:
        name: Template name
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        filepath = TEMPLATES_DIR / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    except Exception:
        return False


def list_templates() -> list[str]:
    """
    List all saved templates.
    
    Returns:
        List of template names
    """
    ensure_templates_dir()
    templates = []
    
    for file in TEMPLATES_DIR.glob("*.json"):
        templates.append(file.stem)
    
    return sorted(templates)


# Built-in presets
PRESETS = {
    "scatter_simple": ChartConfig(
        title="Nuage de points",
        marker_size=10,
        opacity=0.7,
    ),
    "line_clean": ChartConfig(
        title="Courbe",
        line_width=2,
        marker_size=6,
    ),
    "bar_grouped": ChartConfig(
        title="Barres groupées",
        opacity=0.9,
    ),
    "publication_nature": ChartConfig(
        title="Figure",
        theme="nature",
        line_width=1,
        marker_size=4,
    ),
}


def get_preset(name: str) -> Optional[ChartConfig]:
    """Get a built-in preset configuration."""
    return PRESETS.get(name)


def list_presets() -> list[str]:
    """List available presets."""
    return list(PRESETS.keys())
