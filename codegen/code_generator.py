"""Code generator for reproducible Python scripts."""

from typing import Optional
from jinja2 import Template
import json
import yaml

from core.models import ChartConfig, ChartType


class CodeGenerator:
    """Generate Python code from chart configurations."""
    
    def __init__(self):
        """Initialize the code generator."""
        self._plotly_template = self._get_plotly_template()
        self._matplotlib_template = self._get_matplotlib_template()
    
    def generate_plotly_script(
        self,
        config: ChartConfig,
        data_path: str = "data.csv",
        include_imports: bool = True,
    ) -> str:
        """
        Generate a standalone Plotly Python script.
        
        Args:
            config: Chart configuration
            data_path: Path to the data file
            include_imports: Whether to include import statements
            
        Returns:
            Python script as string
        """
        template = Template(self._plotly_template)
        
        return template.render(
            config=config,
            data_path=data_path,
            include_imports=include_imports,
            chart_type=config.chart_type.value,
            y_columns=config.y_columns,
            has_color=config.color_column is not None,
            has_size=config.size_column is not None,
        )
    
    def generate_matplotlib_script(
        self,
        config: ChartConfig,
        data_path: str = "data.csv",
        include_imports: bool = True,
    ) -> str:
        """
        Generate a standalone Matplotlib Python script.
        
        Args:
            config: Chart configuration
            data_path: Path to the data file
            include_imports: Whether to include import statements
            
        Returns:
            Python script as string
        """
        template = Template(self._matplotlib_template)
        
        return template.render(
            config=config,
            data_path=data_path,
            include_imports=include_imports,
            chart_type=config.chart_type.value,
            y_columns=config.y_columns,
        )
    
    def export_config_json(self, config: ChartConfig) -> str:
        """Export configuration as JSON."""
        return config.to_json()
    
    def export_config_yaml(self, config: ChartConfig) -> str:
        """Export configuration as YAML."""
        return config.to_yaml()
    
    def load_config_json(self, json_str: str) -> ChartConfig:
        """Load configuration from JSON."""
        return ChartConfig.from_json(json_str)
    
    def load_config_yaml(self, yaml_str: str) -> ChartConfig:
        """Load configuration from YAML."""
        return ChartConfig.from_yaml(yaml_str)
    
    def _get_plotly_template(self) -> str:
        """Get the Plotly code template."""
        return '''"""
Figure générée avec FigGen
{{ config.title }}
"""
{% if include_imports %}
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
{% endif %}

# Charger les données
df = pd.read_csv("{{ data_path }}")

{% if chart_type == "line" %}
# Graphique en ligne
fig = go.Figure()
{% for y_col in y_columns %}
fig.add_trace(go.Scatter(
    x=df["{{ config.x_column }}"],
    y=df["{{ y_col }}"],
    mode='lines+markers',
    name="{{ y_col }}",
    line=dict(width={{ config.line_width }}),
    marker=dict(size={{ config.marker_size }}),
))
{% endfor %}

{% elif chart_type == "scatter" %}
# Nuage de points
fig = px.scatter(
    df,
    x="{{ config.x_column }}",
    y="{{ y_columns[0] }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
    {% if has_size %}size="{{ config.size_column }}",{% endif %}
    opacity={{ config.opacity }},
)
fig.update_traces(marker=dict(size={{ config.marker_size }}))

{% elif chart_type == "bar" %}
# Graphique à barres
fig = px.bar(
    df,
    x="{{ config.x_column }}",
    y="{{ y_columns[0] }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
    opacity={{ config.opacity }},
)

{% elif chart_type == "histogram" %}
# Histogramme
fig = px.histogram(
    df,
    x="{{ config.x_column }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
    opacity={{ config.opacity }},
    nbins=30,
)

{% elif chart_type == "box" %}
# Box plot
fig = px.box(
    df,
    x="{{ config.x_column }}",
    y="{{ y_columns[0] }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
)

{% elif chart_type == "violin" %}
# Violin plot
fig = px.violin(
    df,
    x="{{ config.x_column }}",
    y="{{ y_columns[0] }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
    box=True,
)

{% elif chart_type == "heatmap" %}
# Heatmap de corrélation
import numpy as np
{% if config.x_column == "__correlation__" %}
numeric_cols = {{ y_columns }}
corr_matrix = df[numeric_cols].corr()
fig = px.imshow(
    corr_matrix,
    labels=dict(x="Variable", y="Variable", color="Corrélation"),
    color_continuous_scale="RdBu_r",
)
fig.update_traces(text=np.round(corr_matrix.values, 2), texttemplate="%{text}")
{% else %}
fig = px.density_heatmap(df, x="{{ config.x_column }}", y="{{ y_columns[0] }}")
{% endif %}

{% elif chart_type == "area" %}
# Graphique en aire
fig = go.Figure()
{% for y_col in y_columns %}
fig.add_trace(go.Scatter(
    x=df["{{ config.x_column }}"],
    y=df["{{ y_col }}"],
    mode='lines',
    name="{{ y_col }}",
    fill='{% if loop.first %}tozeroy{% else %}tonexty{% endif %}',
    line=dict(width={{ config.line_width }}),
    opacity={{ config.opacity }},
))
{% endfor %}

{% elif chart_type == "pie" %}
# Graphique circulaire
fig = px.pie(
    df,
    names="{{ config.x_column }}",
    values="{{ y_columns[0] }}",
)

{% elif chart_type == "bubble" %}
# Graphique à bulles
fig = px.scatter(
    df,
    x="{{ config.x_column }}",
    y="{{ y_columns[0] }}",
    size="{{ config.size_column }}",
    {% if has_color %}color="{{ config.color_column }}",{% endif %}
    opacity={{ config.opacity }},
)
{% endif %}

# Configuration du style
fig.update_layout(
    template="{{ config.theme }}",
    title=dict(
        text="{{ config.title }}",
        x=0.5,
        xanchor='center',
    ),
    {% if config.x_axis.label %}xaxis_title="{{ config.x_axis.label }}",{% endif %}
    {% if config.y_axis.label %}yaxis_title="{{ config.y_axis.label }}",{% endif %}
    showlegend={{ config.legend.show | lower }},
)

{% if config.x_axis.log_scale %}
fig.update_xaxes(type="log")
{% endif %}
{% if config.y_axis.log_scale %}
fig.update_yaxes(type="log")
{% endif %}

# Afficher le graphique
fig.show()

# Sauvegarder (optionnel)
# fig.write_image("figure.png", width=1200, height=800, scale=3)
# fig.write_html("figure.html")
'''
    
    def _get_matplotlib_template(self) -> str:
        """Get the Matplotlib code template."""
        return '''"""
Figure générée avec FigGen
{{ config.title }}
"""
{% if include_imports %}
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
{% endif %}

# Charger les données
df = pd.read_csv("{{ data_path }}")

# Créer la figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

{% if chart_type == "line" %}
# Graphique en ligne
{% for y_col in y_columns %}
ax.plot(df["{{ config.x_column }}"], df["{{ y_col }}"], 
        label="{{ y_col }}", linewidth={{ config.line_width }},
        marker='o', markersize={{ config.marker_size // 2 }})
{% endfor %}
ax.legend()

{% elif chart_type == "scatter" %}
# Nuage de points
ax.scatter(df["{{ config.x_column }}"], df["{{ y_columns[0] }}"],
           s={{ config.marker_size * 5 }}, alpha={{ config.opacity }})

{% elif chart_type == "bar" %}
# Graphique à barres
ax.bar(df["{{ config.x_column }}"], df["{{ y_columns[0] }}"],
       alpha={{ config.opacity }})
plt.xticks(rotation=45, ha='right')

{% elif chart_type == "histogram" %}
# Histogramme
ax.hist(df["{{ config.x_column }}"], bins=30, alpha={{ config.opacity }},
        edgecolor='white')

{% elif chart_type == "box" %}
# Box plot
df.boxplot(column="{{ y_columns[0] }}", by="{{ config.x_column }}", ax=ax)
plt.suptitle('')
plt.xticks(rotation=45, ha='right')

{% elif chart_type == "heatmap" %}
# Heatmap
{% if config.x_column == "__correlation__" %}
numeric_cols = {{ y_columns }}
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0, ax=ax)
{% endif %}
{% endif %}

# Configuration du style
ax.set_title("{{ config.title }}", fontsize=14, fontweight='bold')
{% if config.x_axis.label %}ax.set_xlabel("{{ config.x_axis.label }}"){% endif %}
{% if config.y_axis.label %}ax.set_ylabel("{{ config.y_axis.label }}"){% endif %}

ax.grid(True, alpha=0.3)

{% if config.x_axis.log_scale %}
ax.set_xscale('log')
{% endif %}
{% if config.y_axis.log_scale %}
ax.set_yscale('log')
{% endif %}

plt.tight_layout()

# Afficher le graphique
plt.show()

# Sauvegarder (optionnel)
# fig.savefig("figure.png", dpi=300, bbox_inches='tight')
# fig.savefig("figure.svg", format='svg', bbox_inches='tight')
# fig.savefig("figure.pdf", format='pdf', bbox_inches='tight')
'''
    
    def get_full_notebook(
        self,
        config: ChartConfig,
        data_path: str = "data.csv",
    ) -> str:
        """
        Generate a Jupyter notebook-style script with both backends.
        
        Args:
            config: Chart configuration
            data_path: Path to the data file
            
        Returns:
            Complete notebook script
        """
        plotly_code = self.generate_plotly_script(config, data_path)
        matplotlib_code = self.generate_matplotlib_script(config, data_path, include_imports=False)
        
        return f'''# %% [markdown]
# # Figure: {config.title}
# 
# Script reproductible généré par FigGen

# %% [markdown]
# ## Version Plotly (Interactive)

# %%
{plotly_code}

# %% [markdown]
# ## Version Matplotlib (Publication)

# %%
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

{matplotlib_code}
'''
