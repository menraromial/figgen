"""Visualization themes for publication-ready figures."""

import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt


# Scientific journal themes
THEMES = {
    "nature": {
        "name": "Nature",
        "description": "Style inspiré du journal Nature",
        "plotly_template": "plotly_white",
        "colors": ["#0077B6", "#D62828", "#2A9D8F", "#E9C46A", "#264653"],
        "font_family": "Arial",
        "font_size": 12,
        "line_width": 2,
        "marker_size": 8,
        "background_color": "white",
        "grid_color": "#E0E0E0",
        "axis_color": "#333333",
    },
    "science": {
        "name": "Science",
        "description": "Style inspiré du journal Science",
        "plotly_template": "plotly_white",
        "colors": ["#1B4F72", "#922B21", "#196F3D", "#B9770E", "#5B2C6F"],
        "font_family": "Helvetica",
        "font_size": 11,
        "line_width": 1.5,
        "marker_size": 7,
        "background_color": "white",
        "grid_color": "#D5D8DC",
        "axis_color": "#2C3E50",
    },
    "ieee": {
        "name": "IEEE",
        "description": "Style IEEE pour publications techniques",
        "plotly_template": "plotly_white",
        "colors": ["#00629B", "#E87722", "#78BE20", "#C4D600", "#A05EB5"],
        "font_family": "Times New Roman",
        "font_size": 10,
        "line_width": 1.5,
        "marker_size": 6,
        "background_color": "white",
        "grid_color": "#E8E8E8",
        "axis_color": "#1A1A1A",
    },
    "modern_dark": {
        "name": "Modern Dark",
        "description": "Thème sombre moderne",
        "plotly_template": "plotly_dark",
        "colors": ["#00D4FF", "#FF6B6B", "#4ECDC4", "#FFE66D", "#C792EA"],
        "font_family": "Inter",
        "font_size": 12,
        "line_width": 2,
        "marker_size": 8,
        "background_color": "#1A1A2E",
        "grid_color": "#2D2D44",
        "axis_color": "#EAEAEA",
    },
    "minimal": {
        "name": "Minimal",
        "description": "Design minimaliste épuré",
        "plotly_template": "simple_white",
        "colors": ["#2C3E50", "#E74C3C", "#27AE60", "#F39C12", "#8E44AD"],
        "font_family": "Open Sans",
        "font_size": 11,
        "line_width": 1.5,
        "marker_size": 7,
        "background_color": "white",
        "grid_color": "rgba(0,0,0,0)",
        "axis_color": "#333333",
    },
    "seaborn": {
        "name": "Seaborn",
        "description": "Style Seaborn classique",
        "plotly_template": "seaborn",
        "colors": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"],
        "font_family": "DejaVu Sans",
        "font_size": 11,
        "line_width": 1.75,
        "marker_size": 7,
        "background_color": "#EAEAF2",
        "grid_color": "white",
        "axis_color": "#333333",
    },
    "vibrant": {
        "name": "Vibrant",
        "description": "Couleurs vives et dynamiques",
        "plotly_template": "plotly_white",
        "colors": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
        "font_family": "Roboto",
        "font_size": 12,
        "line_width": 2.5,
        "marker_size": 9,
        "background_color": "white",
        "grid_color": "#F0F0F0",
        "axis_color": "#333333",
    },
    "academic": {
        "name": "Academic",
        "description": "Style académique classique",
        "plotly_template": "plotly_white",
        "colors": ["#000000", "#666666", "#999999", "#CCCCCC", "#333333"],
        "font_family": "Serif",
        "font_size": 11,
        "line_width": 1.5,
        "marker_size": 6,
        "background_color": "white",
        "grid_color": "#D0D0D0",
        "axis_color": "#000000",
    },
}

# Color palettes for multiple series
COLOR_PALETTES = {
    "default": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"],
    "pastel": ["#B4D4E7", "#F8B4B4", "#B4E7B4", "#E7B4E7", "#F8E7B4", "#B4F8F8", "#F8B4D4", "#E7F8B4"],
    "bold": ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF"],
    "colorblind": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9", "#E69F00", "#000000"],
    "grayscale": ["#000000", "#333333", "#666666", "#999999", "#BBBBBB", "#DDDDDD", "#EEEEEE", "#F5F5F5"],
}


def get_theme(theme_name: str) -> dict:
    """
    Get a theme by name.
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        Theme dictionary or default theme if not found
    """
    return THEMES.get(theme_name, THEMES["nature"])


def get_color_palette(palette_name: str) -> list[str]:
    """Get a color palette by name."""
    return COLOR_PALETTES.get(palette_name, COLOR_PALETTES["default"])


def apply_theme(fig: go.Figure, theme_name: str) -> go.Figure:
    """
    Apply a theme to a Plotly figure.
    
    Args:
        fig: Plotly figure
        theme_name: Name of the theme to apply
        
    Returns:
        Updated Plotly figure
    """
    theme = get_theme(theme_name)
    
    fig.update_layout(
        template=theme["plotly_template"],
        font=dict(
            family=theme["font_family"],
            size=theme["font_size"],
            color=theme["axis_color"],
        ),
        paper_bgcolor=theme["background_color"],
        plot_bgcolor=theme["background_color"],
        xaxis=dict(
            gridcolor=theme["grid_color"],
            linecolor=theme["axis_color"],
        ),
        yaxis=dict(
            gridcolor=theme["grid_color"],
            linecolor=theme["axis_color"],
        ),
    )
    
    return fig


def apply_matplotlib_theme(theme_name: str):
    """
    Apply a theme to matplotlib.
    
    Args:
        theme_name: Name of the theme to apply
    """
    theme = get_theme(theme_name)
    
    plt.rcParams.update({
        'font.family': theme["font_family"],
        'font.size': theme["font_size"],
        'axes.labelcolor': theme["axis_color"],
        'axes.edgecolor': theme["axis_color"],
        'axes.facecolor': theme["background_color"],
        'figure.facecolor': theme["background_color"],
        'xtick.color': theme["axis_color"],
        'ytick.color': theme["axis_color"],
        'grid.color': theme["grid_color"],
        'lines.linewidth': theme["line_width"],
        'lines.markersize': theme["marker_size"],
    })


def get_theme_names() -> list[str]:
    """Get list of available theme names."""
    return list(THEMES.keys())


def get_theme_description(theme_name: str) -> str:
    """Get description of a theme."""
    theme = get_theme(theme_name)
    return theme.get("description", "")
