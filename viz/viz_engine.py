"""Visualization engine for FigGen - creates Plotly and Matplotlib figures."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import seaborn as sns
from typing import Optional, Union, Any
import io
import base64

from core.models import ChartConfig, ChartType, ExportConfig
from .themes import get_theme, apply_theme, get_color_palette


class VizEngine:
    """Multi-backend visualization engine."""
    
    def __init__(self):
        """Initialize the visualization engine."""
        self._last_error: str | None = None
    
    @property
    def last_error(self) -> str | None:
        """Return the last error message."""
        return self._last_error
    
    def create_plotly_figure(
        self, 
        df: pd.DataFrame, 
        config: ChartConfig
    ) -> go.Figure | None:
        """
        Create an interactive Plotly figure.
        
        Args:
            df: pandas DataFrame with the data
            config: ChartConfig with visualization settings
            
        Returns:
            Plotly Figure or None if creation fails
        """
        self._last_error = None
        
        try:
            chart_type = config.chart_type
            
            if chart_type == ChartType.LINE:
                fig = self._create_line_chart(df, config)
            elif chart_type == ChartType.SCATTER:
                fig = self._create_scatter_chart(df, config)
            elif chart_type == ChartType.BAR:
                fig = self._create_bar_chart(df, config)
            elif chart_type == ChartType.HISTOGRAM:
                fig = self._create_histogram(df, config)
            elif chart_type == ChartType.BOX:
                fig = self._create_box_chart(df, config)
            elif chart_type == ChartType.VIOLIN:
                fig = self._create_violin_chart(df, config)
            elif chart_type == ChartType.HEATMAP:
                fig = self._create_heatmap(df, config)
            elif chart_type == ChartType.AREA:
                fig = self._create_area_chart(df, config)
            elif chart_type == ChartType.PIE:
                fig = self._create_pie_chart(df, config)
            elif chart_type == ChartType.BUBBLE:
                fig = self._create_bubble_chart(df, config)
            # New chart types
            elif chart_type == ChartType.FUNNEL:
                fig = self._create_funnel_chart(df, config)
            elif chart_type == ChartType.TREEMAP:
                fig = self._create_treemap(df, config)
            elif chart_type == ChartType.SUNBURST:
                fig = self._create_sunburst(df, config)
            elif chart_type == ChartType.RADAR:
                fig = self._create_radar_chart(df, config)
            elif chart_type == ChartType.PARALLEL_COORDS:
                fig = self._create_parallel_coords(df, config)
            elif chart_type == ChartType.CANDLESTICK:
                fig = self._create_candlestick(df, config)
            elif chart_type == ChartType.WATERFALL:
                fig = self._create_waterfall(df, config)
            elif chart_type == ChartType.POLAR:
                fig = self._create_polar_chart(df, config)
            elif chart_type == ChartType.CONTOUR:
                fig = self._create_contour(df, config)
            elif chart_type == ChartType.DENSITY:
                fig = self._create_density(df, config)
            else:
                self._last_error = f"Type de graphique non supporté: {chart_type}"
                return None
            
            # Apply theme and common styling
            fig = self._apply_common_styling(fig, config)
            
            return fig
            
        except Exception as e:
            self._last_error = f"Erreur de création: {str(e)}"
            return None
    
    def _create_line_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a line chart with optional secondary Y axis."""
        colors = config.color_palette or get_color_palette("default")
        
        # Check if we need secondary Y axis
        has_y2 = len(config.y2_columns) > 0
        
        if has_y2:
            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # List of symbols to cycle through for multiple curves
            symbol_list = ["circle", "square", "diamond", "triangle-up", "triangle-down", "star", "cross", "x"]
            
            # Add primary Y axis traces
            for i, y_col in enumerate(config.y_columns):
                curve_symbol = symbol_list[i % len(symbol_list)]
                fig.add_trace(
                    go.Scatter(
                        x=df[config.x_column] if config.x_column else df.index,
                        y=df[y_col],
                        mode='lines+markers',
                        name=f"{y_col} (gauche)",
                        line=dict(width=config.line_width, color=colors[i % len(colors)]),
                        marker=dict(size=config.marker_size, symbol=curve_symbol),
                    ),
                    secondary_y=False,
                )
            
            # Add secondary Y axis traces
            for i, y_col in enumerate(config.y2_columns):
                color_idx = len(config.y_columns) + i
                # Use different symbol set for secondary axis to distinguish
                y2_symbol = symbol_list[(len(config.y_columns) + i) % len(symbol_list)]
                fig.add_trace(
                    go.Scatter(
                        x=df[config.x_column] if config.x_column else df.index,
                        y=df[y_col],
                        mode='lines+markers',
                        name=f"{y_col} (droite)",
                        line=dict(width=config.line_width, color=colors[color_idx % len(colors)], dash='dash'),
                        marker=dict(size=config.marker_size, symbol=y2_symbol),
                    ),
                    secondary_y=True,
                )
            
            # Update secondary axis labels
            if config.y_axis.label:
                fig.update_yaxes(title_text=config.y_axis.label, secondary_y=False)
            if config.y2_axis.label:
                fig.update_yaxes(title_text=config.y2_axis.label, secondary_y=True)
            
            # Start from zero for dual axis
            if config.y_axis.start_zero:
                fig.update_yaxes(rangemode="tozero", secondary_y=False)
            if config.y2_axis.start_zero:
                fig.update_yaxes(rangemode="tozero", secondary_y=True)
            
        elif config.y_columns:
            # Single Y axis - multiple columns
            fig = go.Figure()
            
            # List of symbols to cycle through for multiple curves
            symbol_list = ["circle", "square", "diamond", "triangle-up", "triangle-down", "star", "cross", "x"]
            
            for i, y_col in enumerate(config.y_columns):
                # Cycle through symbols for each curve
                curve_symbol = symbol_list[i % len(symbol_list)]
                fig.add_trace(go.Scatter(
                    x=df[config.x_column] if config.x_column else df.index,
                    y=df[y_col],
                    mode='lines+markers',
                    name=y_col,
                    line=dict(width=config.line_width, color=colors[i % len(colors)]),
                    marker=dict(size=config.marker_size, symbol=curve_symbol),
                ))
        else:
            fig = px.line(
                df,
                x=config.x_column,
                y=config.y_columns[0] if config.y_columns else None,
                color=config.color_column,
            )
        
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a scatter plot."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.scatter(
            df,
            x=config.x_column,
            y=y_col,
            color=config.color_column,
            size=config.size_column,
            opacity=config.opacity,
        )
        
        fig.update_traces(marker=dict(size=config.marker_size))
        
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a bar chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        # Apply aggregation if specified
        if config.aggregation and config.x_column:
            agg_df = df.groupby(config.x_column).agg({y_col: config.aggregation}).reset_index()
        else:
            agg_df = df
        
        fig = px.bar(
            agg_df,
            x=config.x_column,
            y=y_col,
            color=config.color_column,
            opacity=config.opacity,
        )
        
        return fig
    
    def _create_histogram(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a histogram."""
        fig = px.histogram(
            df,
            x=config.x_column,
            color=config.color_column,
            opacity=config.opacity,
            nbins=30,
        )
        
        return fig
    
    def _create_box_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a box plot."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.box(
            df,
            x=config.x_column,
            y=y_col,
            color=config.color_column,
        )
        
        return fig
    
    def _create_violin_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a violin plot."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.violin(
            df,
            x=config.x_column,
            y=y_col,
            color=config.color_column,
            box=True,
        )
        
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a heatmap (correlation matrix or pivot)."""
        if config.x_column == "__correlation__":
            # Correlation matrix
            numeric_cols = config.y_columns if config.y_columns else df.select_dtypes(include=[np.number]).columns.tolist()
            corr_matrix = df[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                labels=dict(x="Variable", y="Variable", color="Corrélation"),
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                color_continuous_scale="RdBu_r",
                aspect="auto",
            )
            fig.update_traces(text=np.round(corr_matrix.values, 2), texttemplate="%{text}")
        else:
            # Pivot table heatmap
            y_col = config.y_columns[0] if config.y_columns else None
            fig = px.density_heatmap(
                df,
                x=config.x_column,
                y=y_col,
            )
        
        return fig
    
    def _create_area_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create an area chart with optional secondary Y axis."""
        colors = config.color_palette or get_color_palette("default")
        
        # Check if we need secondary Y axis
        has_y2 = len(config.y2_columns) > 0
        
        if has_y2:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Primary Y axis traces
            for i, y_col in enumerate(config.y_columns):
                fig.add_trace(
                    go.Scatter(
                        x=df[config.x_column] if config.x_column else df.index,
                        y=df[y_col],
                        mode='lines',
                        name=f"{y_col} (gauche)",
                        fill='tozeroy' if i == 0 else 'tonexty',
                        line=dict(width=config.line_width, color=colors[i % len(colors)]),
                        opacity=config.opacity,
                    ),
                    secondary_y=False,
                )
            
            # Secondary Y axis traces
            for i, y_col in enumerate(config.y2_columns):
                color_idx = len(config.y_columns) + i
                fig.add_trace(
                    go.Scatter(
                        x=df[config.x_column] if config.x_column else df.index,
                        y=df[y_col],
                        mode='lines',
                        name=f"{y_col} (droite)",
                        line=dict(width=config.line_width, color=colors[color_idx % len(colors)], dash='dash'),
                        opacity=config.opacity,
                    ),
                    secondary_y=True,
                )
            
            if config.y_axis.label:
                fig.update_yaxes(title_text=config.y_axis.label, secondary_y=False)
            if config.y2_axis.label:
                fig.update_yaxes(title_text=config.y2_axis.label, secondary_y=True)
        else:
            fig = go.Figure()
            for i, y_col in enumerate(config.y_columns):
                fig.add_trace(go.Scatter(
                    x=df[config.x_column] if config.x_column else df.index,
                    y=df[y_col],
                    mode='lines',
                    name=y_col,
                    fill='tonexty' if i > 0 else 'tozeroy',
                    line=dict(width=config.line_width, color=colors[i % len(colors)]),
                    opacity=config.opacity,
                ))
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a pie chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.pie(
            df,
            names=config.x_column,
            values=y_col,
        )
        
        return fig
    
    def _create_bubble_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a bubble chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.scatter(
            df,
            x=config.x_column,
            y=y_col,
            size=config.size_column,
            color=config.color_column,
            opacity=config.opacity,
        )
        
        return fig
    
    # ========== NEW CHART TYPES ==========
    
    def _create_funnel_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a funnel chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.funnel(
            df,
            x=y_col,
            y=config.x_column,
            color=config.color_column,
        )
        
        return fig
    
    def _create_treemap(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a treemap visualization."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        # Use x_column as category, y_column as values
        path = [config.x_column] if config.x_column else [df.columns[0]]
        if config.color_column and config.color_column != config.x_column:
            path = [config.color_column, config.x_column]
        
        fig = px.treemap(
            df,
            path=path,
            values=y_col,
            color=y_col,
            color_continuous_scale='Viridis',
        )
        
        return fig
    
    def _create_sunburst(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a sunburst chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        path = [config.x_column] if config.x_column else [df.columns[0]]
        if config.color_column and config.color_column != config.x_column:
            path = [config.color_column, config.x_column]
        
        fig = px.sunburst(
            df,
            path=path,
            values=y_col,
            color=y_col,
            color_continuous_scale='Viridis',
        )
        
        return fig
    
    def _create_radar_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a radar/spider chart."""
        fig = go.Figure()
        colors = config.color_palette or get_color_palette("default")
        
        # Use y_columns as the dimensions for the radar
        if config.y_columns:
            categories = config.y_columns
            
            # If we have a categorical column, create traces for each category
            if config.color_column and config.color_column in df.columns:
                for idx, group_val in enumerate(df[config.color_column].unique()):
                    group_df = df[df[config.color_column] == group_val]
                    values = [group_df[col].mean() for col in categories]
                    values.append(values[0])  # Close the polygon
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories + [categories[0]],
                        fill='toself',
                        name=str(group_val),
                        line=dict(color=colors[idx % len(colors)]),
                        opacity=config.opacity,
                    ))
            else:
                # Single trace with mean values
                values = [df[col].mean() for col in categories]
                values.append(values[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name='Données',
                    line=dict(color=colors[0]),
                    opacity=config.opacity,
                ))
        
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
        
        return fig
    
    def _create_parallel_coords(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a parallel coordinates plot."""
        # Use numeric columns for dimensions
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if config.y_columns:
            dimensions = [col for col in config.y_columns if col in numeric_cols]
        else:
            dimensions = numeric_cols[:6]  # Limit to 6 dimensions
        
        color_col = None
        if config.color_column and config.color_column in numeric_cols:
            color_col = df[config.color_column]
        elif dimensions:
            color_col = df[dimensions[0]]
        
        fig = px.parallel_coordinates(
            df,
            dimensions=dimensions,
            color=color_col.name if color_col is not None else None,
            color_continuous_scale='Viridis',
        )
        
        return fig
    
    def _create_candlestick(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a candlestick/OHLC chart."""
        # Expect columns: open, high, low, close (or use first 4 numeric)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 4:
            open_col, high_col, low_col, close_col = numeric_cols[:4]
        elif config.y_columns and len(config.y_columns) >= 4:
            open_col, high_col, low_col, close_col = config.y_columns[:4]
        else:
            # Create a simple OHLC from available data
            y_col = config.y_columns[0] if config.y_columns else numeric_cols[0]
            open_col = high_col = low_col = close_col = y_col
        
        x_data = df[config.x_column] if config.x_column else df.index
        
        fig = go.Figure(data=[go.Candlestick(
            x=x_data,
            open=df[open_col],
            high=df[high_col],
            low=df[low_col],
            close=df[close_col],
        )])
        
        return fig
    
    def _create_waterfall(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a waterfall chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        # Determine measure types (relative/total)
        measures = ["relative"] * len(df)
        if len(df) > 0:
            measures[-1] = "total"
        
        fig = go.Figure(go.Waterfall(
            name="Waterfall",
            orientation="v",
            x=df[config.x_column] if config.x_column else df.index,
            y=df[y_col] if y_col else [],
            measure=measures,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        return fig
    
    def _create_polar_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a polar/rose chart."""
        y_col = config.y_columns[0] if config.y_columns else None
        colors = config.color_palette or get_color_palette("default")
        
        fig = px.bar_polar(
            df,
            r=y_col,
            theta=config.x_column,
            color=config.color_column if config.color_column else config.x_column,
            color_discrete_sequence=colors,
        )
        
        return fig
    
    def _create_contour(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a 2D contour plot."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.density_contour(
            df,
            x=config.x_column,
            y=y_col,
            color=config.color_column,
        )
        fig.update_traces(contours_coloring="fill")
        
        return fig
    
    def _create_density(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a 2D density/KDE plot."""
        y_col = config.y_columns[0] if config.y_columns else None
        
        fig = px.density_heatmap(
            df,
            x=config.x_column,
            y=y_col,
            marginal_x="histogram",
            marginal_y="histogram",
            color_continuous_scale='Viridis',
        )
        
        return fig
    
    def _apply_common_styling(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Apply common styling to a figure."""
        # Apply theme
        fig = apply_theme(fig, config.theme)
        
        # Set title
        fig.update_layout(
            title=dict(
                text=config.title,
                x=0.5,
                xanchor='center',
            ),
        )
        
        # Set subtitle if present
        if config.subtitle:
            fig.add_annotation(
                text=config.subtitle,
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.05,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        
        # Configure axes
        if config.x_axis.label:
            fig.update_xaxes(title_text=config.x_axis.label)
        if config.y_axis.label:
            fig.update_yaxes(title_text=config.y_axis.label)
        
        # Log scale
        if config.x_axis.log_scale:
            fig.update_xaxes(type="log")
        if config.y_axis.log_scale:
            fig.update_yaxes(type="log")
        
        # Axis ranges
        if config.x_axis.min_value is not None or config.x_axis.max_value is not None:
            fig.update_xaxes(range=[config.x_axis.min_value, config.x_axis.max_value])
        if config.y_axis.min_value is not None or config.y_axis.max_value is not None:
            fig.update_yaxes(range=[config.y_axis.min_value, config.y_axis.max_value])
        
        # Start from zero option for Y axis
        if config.y_axis.start_zero:
            fig.update_yaxes(rangemode="tozero")
        
        # Grid - using GridConfig options
        grid_dash_map = {
            "solid": None,
            "dashed": "dash",
            "dotted": "dot",
            "dashdot": "dashdot",
        }
        grid_dash = grid_dash_map.get(config.grid.style, None)
        
        fig.update_xaxes(
            showgrid=config.x_axis.show_grid and config.grid.show,
            gridcolor=config.grid.color,
            gridwidth=config.grid.width,
            griddash=grid_dash,
        )
        fig.update_yaxes(
            showgrid=config.y_axis.show_grid and config.grid.show,
            gridcolor=config.grid.color,
            gridwidth=config.grid.width,
            griddash=grid_dash,
        )
        
        # Legend
        if config.legend.show:
            # Calculate legend position based on config
            legend_pos = config.legend.position
            
            # Position mapping for inside positions
            inside_positions = {
                "inside_top_right": {"x": 0.98, "y": 0.98, "xanchor": "right", "yanchor": "top"},
                "inside_top_left": {"x": 0.02, "y": 0.98, "xanchor": "left", "yanchor": "top"},
                "inside_top_center": {"x": 0.5, "y": 0.98, "xanchor": "center", "yanchor": "top"},
                "inside_bottom_right": {"x": 0.98, "y": 0.02, "xanchor": "right", "yanchor": "bottom"},
                "inside_bottom_left": {"x": 0.02, "y": 0.02, "xanchor": "left", "yanchor": "bottom"},
                "inside_bottom_center": {"x": 0.5, "y": 0.02, "xanchor": "center", "yanchor": "bottom"},
            }
            
            # Position mapping for outside positions
            outside_positions = {
                "right": {"x": 1.02, "y": 0.5, "xanchor": "left", "yanchor": "middle"},
                "left": {"x": -0.15, "y": 0.5, "xanchor": "right", "yanchor": "middle"},
                "top": {"x": 0.5, "y": 1.05, "xanchor": "center", "yanchor": "bottom"},
                "bottom": {"x": 0.5, "y": -0.15, "xanchor": "center", "yanchor": "top"},
                "top_center": {"x": 0.5, "y": 1.08, "xanchor": "center", "yanchor": "bottom"},
                "bottom_center": {"x": 0.5, "y": -0.18, "xanchor": "center", "yanchor": "top"},
            }
            
            # Get position config
            if legend_pos in inside_positions:
                pos_config = inside_positions[legend_pos]
            else:
                pos_config = outside_positions.get(legend_pos, outside_positions["right"])
            
            # Determine orientation
            orientation = "h" if config.legend.orientation == "horizontal" else "v"
            
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    title=config.legend.title,
                    orientation=orientation,
                    x=pos_config["x"],
                    y=pos_config["y"],
                    xanchor=pos_config["xanchor"],
                    yanchor=pos_config["yanchor"],
                    font=dict(size=config.legend.font_size),
                    bgcolor=f"rgba(255,255,255,{config.legend.background_alpha})",
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1 if config.legend.background_alpha > 0 else 0,
                ),
            )
        else:
            fig.update_layout(showlegend=False)
        
        # Hover mode
        fig.update_layout(hovermode="x unified")
        
        # Apply marker and line styles to all traces
        # Map marker style string to Plotly symbol
        marker_symbol_map = {
            "circle": "circle",
            "square": "square",
            "diamond": "diamond",
            "cross": "cross",
            "x": "x",
            "triangle-up": "triangle-up",
            "triangle-down": "triangle-down",
            "star": "star",
        }
        marker_symbol = marker_symbol_map.get(config.marker_style, "circle")
        
        # Map line style to Plotly dash
        line_dash_map = {
            "solid": "solid",
            "dash": "dash",
            "dot": "dot",
            "dashdot": "dashdot",
            "longdash": "longdash",
            "longdashdot": "longdashdot",
        }
        line_dash = line_dash_map.get(config.line_style, "solid")
        
        # Note: We don't update marker symbols globally here because
        # multiple Y column charts set unique symbols per trace in _create_line_chart
        # Only apply line dash style to traces that don't already have specific styling
        if len(config.y_columns) <= 1:
            # Single curve - apply configured marker style
            fig.update_traces(
                marker=dict(symbol=marker_symbol),
                selector=dict(type="scatter"),
            )
        
        # Apply line dash style
        fig.update_traces(
            line=dict(dash=line_dash),
            selector=dict(type="scatter", mode="lines+markers"),
        )
        fig.update_traces(
            line=dict(dash=line_dash),
            selector=dict(type="scatter", mode="lines"),
        )
        
        # Add regression line if enabled
        if config.regression.enabled and config.x_column and config.y_columns:
            fig = self._add_regression_line(df, fig, config)
        
        # Add annotations if any
        if config.annotations:
            fig = self._add_annotations(fig, config)
        
        return fig
    
    def _add_annotations(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Add annotations to the figure."""
        from core.models import AnnotationType
        
        for ann in config.annotations:
            try:
                if ann.type == AnnotationType.TEXT:
                    # Build background color with opacity
                    bgcolor = None
                    if hasattr(ann, 'background_color') and ann.background_color:
                        bg_opacity = ann.background_opacity if hasattr(ann, 'background_opacity') else 0.3
                        # Convert hex to rgba
                        bg_hex = ann.background_color.lstrip('#')
                        bg_r, bg_g, bg_b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                        bgcolor = f"rgba({bg_r},{bg_g},{bg_b},{bg_opacity})"
                    
                    fig.add_annotation(
                        x=ann.x,
                        y=ann.y,
                        text=ann.text,
                        showarrow=False,
                        font=dict(size=ann.font_size, color=ann.color),
                        xref="x" if ann.use_data_coords else "paper",
                        yref="y" if ann.use_data_coords else "paper",
                        bgcolor=bgcolor,
                        opacity=ann.opacity if hasattr(ann, 'opacity') else 1.0,
                        bordercolor=ann.border_color if hasattr(ann, 'border_color') and ann.border_color else None,
                        borderwidth=ann.border_width if hasattr(ann, 'border_width') else 0,
                    )
                elif ann.type == AnnotationType.ARROW:
                    from core.models import ArrowHeadStyle
                    
                    # Map arrow head styles to Plotly arrowhead numbers
                    # 0=none, 1=open, 2=filled triangle, 3=filled square, 4=circle
                    head_style_map = {
                        ArrowHeadStyle.TRIANGLE: 2,
                        ArrowHeadStyle.OPEN: 1,
                        ArrowHeadStyle.NONE: 0,
                        ArrowHeadStyle.CIRCLE: 4,
                        ArrowHeadStyle.SQUARE: 3,
                        ArrowHeadStyle.DIAMOND: 5,
                    }
                    arrowhead = head_style_map.get(ann.arrow_head_style, 2)
                    
                    fig.add_annotation(
                        x=ann.x,
                        y=ann.y,
                        ax=ann.x_end if ann.x_end is not None else ann.x - 20,
                        ay=ann.y_end if ann.y_end is not None else ann.y - 20,
                        text=ann.text,
                        showarrow=True,
                        arrowhead=arrowhead,
                        arrowsize=1.5,
                        arrowwidth=ann.line_width if hasattr(ann, 'line_width') else 2,
                        arrowcolor=ann.color,
                        font=dict(size=ann.font_size, color=ann.color),
                        xref="x" if ann.use_data_coords else "paper",
                        yref="y" if ann.use_data_coords else "paper",
                        axref="x" if ann.use_data_coords else "pixel",
                        ayref="y" if ann.use_data_coords else "pixel",
                    )
                elif ann.type == AnnotationType.VLINE:
                    fig.add_vline(
                        x=ann.x,
                        line_color=ann.color,
                        line_width=2,
                        line_dash="dash",
                        annotation_text=ann.text if ann.text else None,
                    )
                elif ann.type == AnnotationType.HLINE:
                    fig.add_hline(
                        y=ann.y,
                        line_color=ann.color,
                        line_width=2,
                        line_dash="dash",
                        annotation_text=ann.text if ann.text else None,
                    )
                elif ann.type == AnnotationType.RECT:
                    # Get fill opacity
                    fill_opacity = ann.fill_opacity if hasattr(ann, 'fill_opacity') else 0.2
                    line_width = ann.line_width if hasattr(ann, 'line_width') else 2
                    
                    # Convert hex color to rgba for fill
                    hex_color = ann.color.lstrip('#')
                    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    fillcolor = f"rgba({r},{g},{b},{fill_opacity})"
                    
                    fig.add_shape(
                        type="rect",
                        x0=ann.x,
                        y0=ann.y,
                        x1=ann.x_end if ann.x_end else ann.x + 1,
                        y1=ann.y_end if ann.y_end else ann.y + 1,
                        line=dict(color=ann.color, width=line_width),
                        fillcolor=fillcolor,
                        opacity=ann.opacity if hasattr(ann, 'opacity') else 1.0,
                    )
                elif ann.type == AnnotationType.LINE:
                    fig.add_shape(
                        type="line",
                        x0=ann.x,
                        y0=ann.y,
                        x1=ann.x_end if ann.x_end else ann.x + 1,
                        y1=ann.y_end if ann.y_end else ann.y,
                        line=dict(color=ann.color, width=2),
                    )
            except Exception:
                # Skip invalid annotations
                pass
        
        return fig
    
    def _add_regression_line(self, df: pd.DataFrame, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Add regression/trend line to the figure."""
        from core.models import RegressionType
        
        try:
            x_data = df[config.x_column]
            y_col = config.y_columns[0] if config.y_columns else None
            if y_col is None:
                return fig
            
            y_data = df[y_col]
            
            # Convert to numeric if needed
            if not np.issubdtype(x_data.dtype, np.number):
                x_numeric = np.arange(len(x_data))
            else:
                x_numeric = x_data.values
            
            y_numeric = pd.to_numeric(y_data, errors='coerce').values
            
            # Remove NaN values
            mask = ~(np.isnan(x_numeric) | np.isnan(y_numeric))
            x_clean = x_numeric[mask]
            y_clean = y_numeric[mask]
            
            if len(x_clean) < 2:
                return fig
            
            # Calculate regression
            if config.regression.type == RegressionType.LINEAR:
                coeffs = np.polyfit(x_clean, y_clean, 1)
                poly = np.poly1d(coeffs)
                equation = f"y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}"
            else:  # Polynomial
                degree = config.regression.degree
                coeffs = np.polyfit(x_clean, y_clean, degree)
                poly = np.poly1d(coeffs)
                terms = [f"{coeffs[i]:.4f}x^{degree-i}" for i in range(len(coeffs)-1)]
                terms.append(f"{coeffs[-1]:.4f}")
                equation = "y = " + " + ".join(terms)
            
            # Calculate R²
            y_pred = poly(x_clean)
            ss_res = np.sum((y_clean - y_pred) ** 2)
            ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Generate smooth regression line
            x_line = np.linspace(x_clean.min(), x_clean.max(), 100)
            y_line = poly(x_line)
            
            # Create label
            label_parts = ["Tendance"]
            if config.regression.show_equation:
                label_parts.append(equation)
            if config.regression.show_r2:
                label_parts.append(f"R² = {r2:.4f}")
            
            # Add regression trace
            dash_map = {"solid": "solid", "dash": "dash", "dot": "dot"}
            
            fig.add_trace(go.Scatter(
                x=x_line if np.issubdtype(x_data.dtype, np.number) else x_data.values[:len(x_line)],
                y=y_line,
                mode='lines',
                name="<br>".join(label_parts),
                line=dict(
                    color=config.regression.line_color,
                    width=config.regression.line_width,
                    dash=dash_map.get(config.regression.line_style, "dash"),
                ),
            ))
            
        except Exception as e:
            # Silently fail - regression is optional
            pass
        
        return fig
    
    def create_matplotlib_figure(
        self, 
        df: pd.DataFrame, 
        config: ChartConfig
    ) -> plt.Figure | None:
        """
        Create a publication-ready Matplotlib figure.
        
        Args:
            df: pandas DataFrame with the data
            config: ChartConfig with visualization settings
            
        Returns:
            Matplotlib Figure or None if creation fails
        """
        self._last_error = None
        
        try:
            theme = get_theme(config.theme)
            
            # Set up the figure
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor(theme["background_color"])
            ax.set_facecolor(theme["background_color"])
            
            colors = config.color_palette or theme["colors"]
            chart_type = config.chart_type
            
            if chart_type == ChartType.LINE:
                self._mpl_line(ax, df, config, colors)
            elif chart_type == ChartType.SCATTER:
                self._mpl_scatter(ax, df, config, colors)
            elif chart_type == ChartType.BAR:
                self._mpl_bar(ax, df, config, colors)
            elif chart_type == ChartType.HISTOGRAM:
                self._mpl_histogram(ax, df, config, colors)
            elif chart_type == ChartType.BOX:
                self._mpl_box(ax, df, config, colors)
            elif chart_type == ChartType.HEATMAP:
                self._mpl_heatmap(ax, df, config)
            else:
                self._last_error = f"Type non supporté pour Matplotlib: {chart_type}"
                return None
            
            # Common styling
            ax.set_title(config.title, fontsize=theme["font_size"] + 2, fontweight='bold')
            if config.x_axis.label:
                ax.set_xlabel(config.x_axis.label, fontsize=theme["font_size"])
            if config.y_axis.label:
                ax.set_ylabel(config.y_axis.label, fontsize=theme["font_size"])
            
            # Legend configuration
            if config.legend.show:
                # Get legend handles from all axes (including secondary Y if exists)
                handles, labels = ax.get_legend_handles_labels()
                
                # Check for secondary y-axis and get its handles
                for other_ax in fig.axes:
                    if other_ax != ax:
                        h, l = other_ax.get_legend_handles_labels()
                        handles.extend(h)
                        labels.extend(l)
                
                if handles:
                    # Configure position with bbox_to_anchor for outside positions
                    bbox = None
                    loc = "best"
                    
                    if config.legend.position == "right":
                        loc = "center left"
                        bbox = (1.02, 0.5)
                    elif config.legend.position == "left":
                        loc = "center right"
                        bbox = (-0.15, 0.5)
                    elif config.legend.position == "top":
                        loc = "lower center"
                        bbox = (0.5, 1.02)
                    elif config.legend.position == "bottom":
                        loc = "upper center"
                        bbox = (0.5, -0.12)
                    elif config.legend.position == "top_center":
                        loc = "lower center"
                        bbox = (0.5, 1.05)
                    elif config.legend.position == "bottom_center":
                        loc = "upper center"
                        bbox = (0.5, -0.15)
                    elif config.legend.position == "inside_top_right":
                        loc = "upper right"
                    elif config.legend.position == "inside_top_left":
                        loc = "upper left"
                    elif config.legend.position == "inside_top_center":
                        loc = "upper center"
                    elif config.legend.position == "inside_bottom_right":
                        loc = "lower right"
                    elif config.legend.position == "inside_bottom_left":
                        loc = "lower left"
                    elif config.legend.position == "inside_bottom_center":
                        loc = "lower center"
                    
                    ncol = 1 if config.legend.orientation == "vertical" else len(handles)
                    
                    ax.legend(
                        handles, labels,
                        loc=loc,
                        fontsize=config.legend.font_size,
                        framealpha=config.legend.background_alpha,
                        ncol=ncol,
                        bbox_to_anchor=bbox,
                    )
            
            # Grid - using GridConfig options
            if config.grid.show and (config.x_axis.show_grid or config.y_axis.show_grid):
                linestyle_map = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":",
                    "dashdot": "-.",
                }
                grid_linestyle = linestyle_map.get(config.grid.style, "-")
                
                ax.grid(
                    True,
                    color=config.grid.color,
                    linewidth=config.grid.width,
                    linestyle=grid_linestyle,
                    alpha=config.grid.opacity,
                )
                ax.set_axisbelow(True)  # Grid behind data
            else:
                ax.grid(False)
            
            # Apply start_zero to primary Y axis
            if config.y_axis.start_zero:
                ax.set_ylim(bottom=0)
            
            # Add annotations if any
            if config.annotations:
                self._add_mpl_annotations(ax, config)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            self._last_error = f"Erreur Matplotlib: {str(e)}"
            return None
    
    def _add_mpl_annotations(self, ax, config: ChartConfig) -> None:
        """Add annotations to Matplotlib figure."""
        from core.models import AnnotationType
        import matplotlib.patches as patches
        
        for ann in config.annotations:
            try:
                if ann.type == AnnotationType.TEXT:
                    # Get style options
                    opacity = ann.opacity if hasattr(ann, 'opacity') else 1.0
                    
                    # Build bbox for background
                    bbox_props = None
                    if hasattr(ann, 'background_color') and ann.background_color:
                        bg_opacity = ann.background_opacity if hasattr(ann, 'background_opacity') else 0.3
                        bbox_props = dict(
                            facecolor=ann.background_color,
                            alpha=bg_opacity,
                            edgecolor=ann.border_color if hasattr(ann, 'border_color') and ann.border_color else 'none',
                            linewidth=ann.border_width if hasattr(ann, 'border_width') else 0,
                            boxstyle='round,pad=0.3',
                        )
                    
                    ax.annotate(
                        ann.text,
                        xy=(ann.x, ann.y),
                        fontsize=ann.font_size,
                        color=ann.color,
                        alpha=opacity,
                        ha='center', va='center',
                        bbox=bbox_props,
                    )
                elif ann.type == AnnotationType.ARROW:
                    from core.models import ArrowHeadStyle
                    
                    # x, y = arrow tip (where it points to)
                    # x_end, y_end = arrow origin (where arrow starts from, also where text is)
                    x_origin = ann.x_end if ann.x_end is not None else ann.x - 20
                    y_origin = ann.y_end if ann.y_end is not None else ann.y - 20
                    
                    # Map arrow head styles to Matplotlib arrowstyles
                    head_style_map = {
                        ArrowHeadStyle.TRIANGLE: '-|>',  # Filled triangle
                        ArrowHeadStyle.OPEN: '->',  # Open arrow
                        ArrowHeadStyle.NONE: '-',  # No head
                        ArrowHeadStyle.CIRCLE: '-o',  # Circle (custom marker needed)
                        ArrowHeadStyle.SQUARE: '-s',  # Square
                        ArrowHeadStyle.DIAMOND: '-D',  # Diamond
                    }
                    
                    # Default arrow styles work for most, special handling for circle/square/diamond
                    style = ann.arrow_head_style if hasattr(ann, 'arrow_head_style') else ArrowHeadStyle.TRIANGLE
                    
                    if style in [ArrowHeadStyle.CIRCLE, ArrowHeadStyle.SQUARE, ArrowHeadStyle.DIAMOND]:
                        # Draw line + marker for these styles
                        ax.plot([x_origin, ann.x], [y_origin, ann.y], 
                               color=ann.color, lw=ann.line_width if hasattr(ann, 'line_width') else 2)
                        marker_map = {
                            ArrowHeadStyle.CIRCLE: 'o',
                            ArrowHeadStyle.SQUARE: 's',
                            ArrowHeadStyle.DIAMOND: 'D',
                        }
                        ax.plot(ann.x, ann.y, marker=marker_map[style], 
                               markersize=10, color=ann.color)
                        ax.text(x_origin, y_origin, ann.text,
                               fontsize=ann.font_size, color=ann.color,
                               ha='center', va='center')
                    else:
                        # Standard arrow annotation
                        arrowstyle = head_style_map.get(style, '->')
                        ax.annotate(
                            ann.text,
                            xy=(ann.x, ann.y),  # Arrow tip
                            xytext=(x_origin, y_origin),  # Arrow origin / text position
                            fontsize=ann.font_size,
                            color=ann.color,
                            xycoords='data',
                            textcoords='data',
                            arrowprops=dict(
                                arrowstyle=arrowstyle,
                                color=ann.color,
                                lw=ann.line_width if hasattr(ann, 'line_width') else 2,
                                shrinkA=0,
                                shrinkB=0,
                            ),
                            ha='center', va='center',
                        )
                elif ann.type == AnnotationType.VLINE:
                    ax.axvline(x=ann.x, color=ann.color, linestyle='--', linewidth=2, alpha=0.7)
                    if ann.text:
                        ax.text(ann.x, ax.get_ylim()[1], ann.text, 
                               rotation=90, va='top', ha='right', color=ann.color)
                elif ann.type == AnnotationType.HLINE:
                    ax.axhline(y=ann.y, color=ann.color, linestyle='--', linewidth=2, alpha=0.7)
                    if ann.text:
                        ax.text(ax.get_xlim()[1], ann.y, ann.text, 
                               va='bottom', ha='right', color=ann.color)
                elif ann.type == AnnotationType.RECT:
                    x0, y0 = ann.x, ann.y
                    width = (ann.x_end or ann.x + 10) - ann.x
                    height = (ann.y_end or ann.y + 10) - ann.y
                    
                    # Get style options
                    fill_opacity = ann.fill_opacity if hasattr(ann, 'fill_opacity') else 0.2
                    line_width = ann.line_width if hasattr(ann, 'line_width') else 2
                    opacity = ann.opacity if hasattr(ann, 'opacity') else 1.0
                    
                    rect = patches.Rectangle(
                        (x0, y0), width, height,
                        linewidth=line_width, 
                        edgecolor=ann.color,
                        facecolor=ann.color, 
                        alpha=fill_opacity * opacity,
                    )
                    # Add to plot
                    ax.add_patch(rect)
                    
                    # Add border separately for better control
                    rect_border = patches.Rectangle(
                        (x0, y0), width, height,
                        linewidth=line_width,
                        edgecolor=ann.color,
                        facecolor='none',
                        alpha=opacity,
                    )
                    ax.add_patch(rect_border)
                elif ann.type == AnnotationType.LINE:
                    ax.plot(
                        [ann.x, ann.x_end or ann.x + 10],
                        [ann.y, ann.y_end or ann.y],
                        color=ann.color, linewidth=2,
                    )
            except Exception:
                # Skip invalid annotations
                pass
    
    def _mpl_line(self, ax, df, config, colors):
        """Create matplotlib line chart with optional dual Y-axis."""
        x_data = df[config.x_column] if config.x_column else df.index
        
        # Map marker styles from config
        marker_style_map = {
            "circle": "o",
            "square": "s",
            "diamond": "D",
            "cross": "+",
            "x": "x",
            "triangle-up": "^",
            "triangle-down": "v",
            "star": "*",
        }
        marker = marker_style_map.get(config.marker_style, "o")
        
        # Map line styles from config
        line_style_map = {
            "solid": "-",
            "dash": "--",
            "dot": ":",
            "dashdot": "-.",
            "longdash": "--",
            "longdashdot": "-.",
        }
        linestyle = line_style_map.get(config.line_style, "-")
        
        # List of markers to cycle through for multiple curves
        marker_list = ["o", "s", "D", "^", "v", "*", "+", "x", "p", "h"]
        
        # Primary Y axis - each curve gets a different marker
        for i, y_col in enumerate(config.y_columns):
            # Cycle through markers for each curve
            curve_marker = marker_list[i % len(marker_list)]
            ax.plot(x_data, df[y_col], label=y_col, 
                   color=colors[i % len(colors)],
                   linewidth=config.line_width,
                   linestyle=linestyle,
                   marker=curve_marker, markersize=config.marker_size / 2)
        
        # Secondary Y axis if y2_columns are specified
        if config.y2_columns:
            ax2 = ax.twinx()
            
            # Use different marker set for secondary Y axis (offset from primary)
            for i, y_col in enumerate(config.y2_columns):
                color_idx = len(config.y_columns) + i
                # Offset marker index for Y2 to ensure different markers
                y2_marker = marker_list[(len(config.y_columns) + i) % len(marker_list)]
                
                ax2.plot(x_data, df[y_col], label=y_col, 
                        color=colors[color_idx % len(colors)],
                        linewidth=config.line_width,
                        linestyle='--',  # Secondary Y uses dashed to distinguish
                        marker=y2_marker, markersize=config.marker_size / 2)
            
            if config.y2_axis.label:
                ax2.set_ylabel(config.y2_axis.label)
            
            # Start from zero for secondary Y axis
            if config.y2_axis.start_zero:
                ax2.set_ylim(bottom=0)
            
            # Apply grid for secondary Y axis (optional - less prominent)
            if config.y_axis.show_grid and config.grid.show:
                ax2.grid(False)  # Avoid overlapping grids, primary axis handles it
            
            # Combine legends from both axes
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='best')
    
    def _mpl_scatter(self, ax, df, config, colors):
        """Create matplotlib scatter plot."""
        x_data = df[config.x_column] if config.x_column else df.index
        y_col = config.y_columns[0] if config.y_columns else None
        
        # Map marker styles from config
        marker_style_map = {
            "circle": "o",
            "square": "s",
            "diamond": "D",
            "cross": "+",
            "x": "x",
            "triangle-up": "^",
            "triangle-down": "v",
            "star": "*",
        }
        marker = marker_style_map.get(config.marker_style, "o")
        
        ax.scatter(x_data, df[y_col], s=config.marker_size * 10, 
                  alpha=config.opacity,
                  c=colors[0],
                  marker=marker)
    
    def _mpl_bar(self, ax, df, config, colors):
        """Create matplotlib bar chart."""
        x_data = df[config.x_column] if config.x_column else df.index
        y_col = config.y_columns[0] if config.y_columns else None
        ax.bar(x_data, df[y_col], color=colors[0], alpha=config.opacity)
        plt.xticks(rotation=45, ha='right')
    
    def _mpl_histogram(self, ax, df, config, colors):
        """Create matplotlib histogram."""
        ax.hist(df[config.x_column], bins=30, color=colors[0], 
               alpha=config.opacity, edgecolor='white')
    
    def _mpl_box(self, ax, df, config, colors):
        """Create matplotlib box plot."""
        if config.x_column and config.y_columns:
            groups = df.groupby(config.x_column)[config.y_columns[0]].apply(list).to_dict()
            ax.boxplot(groups.values(), labels=groups.keys())
            plt.xticks(rotation=45, ha='right')
    
    def _mpl_heatmap(self, ax, df, config):
        """Create matplotlib heatmap."""
        if config.x_column == "__correlation__":
            numeric_cols = config.y_columns if config.y_columns else df.select_dtypes(include=[np.number]).columns.tolist()
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0, ax=ax)
    
    def export_figure(
        self,
        fig: Union[go.Figure, plt.Figure],
        export_config: ExportConfig,
    ) -> bytes:
        """
        Export a figure to bytes in the specified format.
        
        Args:
            fig: Plotly or Matplotlib figure
            export_config: Export configuration
            
        Returns:
            Bytes of the exported figure
        """
        if isinstance(fig, go.Figure):
            return self._export_plotly(fig, export_config)
        else:
            return self._export_matplotlib(fig, export_config)
    
    def _export_plotly(self, fig: go.Figure, config: ExportConfig) -> bytes:
        """Export Plotly figure."""
        if config.format.value == "html":
            return fig.to_html(include_plotlyjs=True).encode("utf-8")
        else:
            return fig.to_image(
                format=config.format.value,
                width=config.width,
                height=config.height,
                scale=config.get_scale(),
            )
    
    def _export_matplotlib(self, fig: plt.Figure, config: ExportConfig) -> bytes:
        """Export Matplotlib figure."""
        buffer = io.BytesIO()
        fig.savefig(
            buffer,
            format=config.format.value,
            dpi=config.dpi,
            bbox_inches='tight',
            transparent=config.transparent_background,
        )
        buffer.seek(0)
        return buffer.read()
    
    def figure_to_base64(self, fig: go.Figure) -> str:
        """Convert Plotly figure to base64 PNG for embedding."""
        img_bytes = fig.to_image(format="png", width=800, height=600)
        return base64.b64encode(img_bytes).decode("utf-8")
