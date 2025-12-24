"""Pydantic models for FigGen configuration and data structures."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
import json
import yaml


class ChartType(str, Enum):
    """Supported chart types."""
    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    AREA = "area"
    PIE = "pie"
    BUBBLE = "bubble"
    # New chart types
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    RADAR = "radar"
    PARALLEL_COORDS = "parallel_coords"
    CANDLESTICK = "candlestick"
    WATERFALL = "waterfall"
    POLAR = "polar"
    CONTOUR = "contour"
    DENSITY = "density"


class ColumnType(str, Enum):
    """Detected column types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class ExportFormat(str, Enum):
    """Supported export formats."""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    HTML = "html"


class ColumnProfile(BaseModel):
    """Profile information for a single column."""
    name: str
    dtype: str
    column_type: ColumnType
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: list[Any] = Field(default_factory=list)
    
    # Numeric stats (optional)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    std_value: Optional[float] = None
    
    # Categorical stats (optional)
    top_categories: Optional[dict[str, int]] = None


class DataProfile(BaseModel):
    """Complete profile of a dataset."""
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    memory_usage_mb: float
    has_missing_values: bool
    suggested_charts: list[str] = Field(default_factory=list)
    
    def get_numeric_columns(self) -> list[str]:
        """Return names of numeric columns."""
        return [c.name for c in self.columns if c.column_type == ColumnType.NUMERIC]
    
    def get_categorical_columns(self) -> list[str]:
        """Return names of categorical columns."""
        return [c.name for c in self.columns if c.column_type == ColumnType.CATEGORICAL]
    
    def get_temporal_columns(self) -> list[str]:
        """Return names of temporal columns."""
        return [c.name for c in self.columns if c.column_type == ColumnType.TEMPORAL]


class AxisConfig(BaseModel):
    """Configuration for chart axes."""
    label: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    log_scale: bool = False
    show_grid: bool = True
    tick_format: Optional[str] = None
    start_zero: bool = False  # Force axis to start from 0


class GridConfig(BaseModel):
    """Configuration for chart grid lines."""
    show: bool = True
    color: str = "#CCCCCC"  # Grid line color
    width: float = 1.0  # Grid line width
    style: str = "solid"  # solid, dashed, dotted, dashdot
    opacity: float = 0.5  # Grid line opacity (0.0 - 1.0)
    show_minor: bool = False  # Show minor grid lines
    minor_color: str = "#EEEEEE"
    minor_width: float = 0.5
    minor_opacity: float = 0.3


class LegendConfig(BaseModel):
    """Configuration for chart legend."""
    show: bool = True
    position: str = "right"  # right, left, top, bottom, inside_top_right, inside_top_left, inside_bottom_right, inside_bottom_left
    orientation: str = "vertical"  # vertical, horizontal
    title: Optional[str] = None
    font_size: int = 10
    background_alpha: float = 0.8  # Transparency of legend background


class AnnotationType(str, Enum):
    """Types of annotations."""
    TEXT = "text"
    ARROW = "arrow"
    LINE = "line"
    RECT = "rect"
    VLINE = "vline"
    HLINE = "hline"


class ArrowHeadStyle(str, Enum):
    """Arrow head styles."""
    TRIANGLE = "triangle"  # Standard arrow head
    OPEN = "open"  # Open arrow (V shape)
    NONE = "none"  # No head (just line)
    CIRCLE = "circle"  # Circle at end
    SQUARE = "square"  # Square at end
    DIAMOND = "diamond"  # Diamond at end


class AnnotationConfig(BaseModel):
    """Configuration for a single annotation."""
    type: AnnotationType = AnnotationType.TEXT
    text: str = ""
    x: float = 0.5  # X position (data coords or relative)
    y: float = 0.5  # Y position (data coords or relative)
    x_end: Optional[float] = None  # For arrows/lines
    y_end: Optional[float] = None
    font_size: int = 12
    color: str = "#333333"  # Text / line color
    arrow_head: bool = True  # Kept for backwards compatibility
    arrow_head_style: ArrowHeadStyle = ArrowHeadStyle.TRIANGLE
    line_width: float = 2.0  # Changed to float for values < 1
    use_data_coords: bool = True  # Use data coordinates vs relative
    
    # Advanced styling
    opacity: float = 1.0  # 0.0 - 1.0
    background_color: Optional[str] = None  # Background color (for text/rect)
    background_opacity: float = 0.3  # Background transparency
    border_color: Optional[str] = None  # Border color
    border_width: float = 1.0  # Changed to float for values < 1
    fill_opacity: float = 0.2  # Fill opacity for shapes (rect)


class RegressionType(str, Enum):
    """Types of regression."""
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"


class RegressionConfig(BaseModel):
    """Configuration for regression/trend lines."""
    enabled: bool = False
    type: RegressionType = RegressionType.LINEAR
    degree: int = 2  # For polynomial
    show_equation: bool = True
    show_r2: bool = True
    line_color: str = "#ff0000"
    line_width: int = 2
    line_style: str = "dash"  # solid, dash, dot


class ChartConfig(BaseModel):
    """Complete chart configuration."""
    # Chart type
    chart_type: ChartType = ChartType.SCATTER
    
    # Data mapping
    x_column: Optional[str] = None
    y_columns: list[str] = Field(default_factory=list)
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    facet_column: Optional[str] = None
    
    # Secondary Y axis (dual axis support)
    y2_columns: list[str] = Field(default_factory=list)  # Columns for secondary Y axis
    y2_axis: AxisConfig = Field(default_factory=AxisConfig)
    
    # Aggregation
    aggregation: Optional[str] = None  # mean, sum, count, etc.
    group_by: Optional[str] = None
    
    # Title and labels
    title: str = "Figure"
    subtitle: Optional[str] = None
    
    # Axes
    x_axis: AxisConfig = Field(default_factory=AxisConfig)
    y_axis: AxisConfig = Field(default_factory=AxisConfig)
    
    # Legend
    legend: LegendConfig = Field(default_factory=LegendConfig)
    
    # Grid configuration
    grid: GridConfig = Field(default_factory=GridConfig)
    
    # Styling
    theme: str = "plotly_white"
    color_palette: Optional[list[str]] = None
    marker_size: float = 8.0  # Changed to float for values < 1
    line_width: float = 2.0  # Changed to float for values < 1
    opacity: float = 0.8
    marker_style: str = "circle"  # circle, square, diamond, cross, x, triangle
    line_style: str = "solid"  # solid, dash, dot, dashdot
    
    # Annotations
    show_values: bool = False
    annotations: list[AnnotationConfig] = Field(default_factory=list)
    
    # Regression/Trend line
    regression: RegressionConfig = Field(default_factory=RegressionConfig)
    
    def to_yaml(self) -> str:
        """Export configuration to YAML."""
        return yaml.dump(self.model_dump(), default_flow_style=False, allow_unicode=True)
    
    def to_json(self) -> str:
        """Export configuration to JSON."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "ChartConfig":
        """Load configuration from YAML."""
        return cls(**yaml.safe_load(yaml_str))
    
    @classmethod
    def from_json(cls, json_str: str) -> "ChartConfig":
        """Load configuration from JSON."""
        return cls(**json.loads(json_str))


class ExportConfig(BaseModel):
    """Configuration for figure export."""
    format: ExportFormat = ExportFormat.PNG
    width: int = 1200
    height: int = 800
    dpi: int = 300
    transparent_background: bool = False
    
    # For publication
    font_family: str = "Arial"
    font_size: int = 12
    
    def get_scale(self) -> float:
        """Calculate scale factor for export."""
        return self.dpi / 100


class ChartSuggestion(BaseModel):
    """A suggested chart type with reasoning."""
    chart_type: ChartType
    x_column: str
    y_columns: list[str]
    color_column: Optional[str] = None
    reasoning: str
    score: float = 1.0  # Relevance score (0-1)
