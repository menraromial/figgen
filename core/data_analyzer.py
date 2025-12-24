"""Data analysis module for FigGen - automatic type detection and chart suggestions."""

import pandas as pd
import numpy as np
from typing import Optional, Any
from .models import (
    DataProfile,
    ColumnProfile,
    ColumnType,
    ChartType,
    ChartSuggestion,
)


class DataAnalyzer:
    """Analyze DataFrames to detect types and suggest visualizations."""
    
    # Thresholds for type detection
    CATEGORICAL_THRESHOLD = 20  # Max unique values for categorical
    DATETIME_FORMATS = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze(self, df: pd.DataFrame) -> DataProfile:
        """
        Perform complete analysis of a DataFrame.
        
        Args:
            df: pandas DataFrame to analyze
            
        Returns:
            DataProfile with complete analysis results
        """
        columns = []
        for col in df.columns:
            try:
                columns.append(self._analyze_column(df, col))
            except Exception as e:
                # Skip columns that fail analysis (e.g., complex nested objects)
                columns.append(ColumnProfile(
                    name=col,
                    dtype=str(df[col].dtype),
                    column_type=ColumnType.UNKNOWN,
                    null_count=int(df[col].isnull().sum()),
                    null_percentage=0.0,
                    unique_count=0,
                    sample_values=[],
                ))
        
        # Calculate memory usage
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        # Check for missing values
        has_missing = df.isnull().any().any()
        
        # Generate chart suggestions
        suggestions = self._suggest_charts(df, columns)
        
        return DataProfile(
            row_count=len(df),
            column_count=len(df.columns),
            columns=columns,
            memory_usage_mb=round(memory_mb, 2),
            has_missing_values=has_missing,
            suggested_charts=[s.chart_type.value for s in suggestions[:5]],
        )
    
    def _analyze_column(self, df: pd.DataFrame, column: str) -> ColumnProfile:
        """Analyze a single column."""
        series = df[column]
        
        # Check if column contains unhashable types (dicts, lists, etc.)
        if self._contains_complex_objects(series):
            return ColumnProfile(
                name=column,
                dtype=str(series.dtype),
                column_type=ColumnType.UNKNOWN,
                null_count=int(series.isnull().sum()),
                null_percentage=round(series.isnull().sum() / len(df) * 100, 2) if len(df) > 0 else 0,
                unique_count=0,
                sample_values=[str(v)[:50] for v in series.dropna().head(3).tolist()],
            )
        
        # Basic stats
        null_count = int(series.isnull().sum())
        null_pct = round(null_count / len(df) * 100, 2) if len(df) > 0 else 0
        
        try:
            unique_count = int(series.nunique())
        except TypeError:
            unique_count = 0
        
        # Detect column type
        col_type = self._detect_column_type(series, unique_count)
        
        # Get sample values (non-null)
        try:
            sample_values = series.dropna().head(5).tolist()
            # Convert any non-serializable values to strings
            sample_values = [self._safe_value(v) for v in sample_values]
        except Exception:
            sample_values = []
        
        # Build profile
        profile = ColumnProfile(
            name=column,
            dtype=str(series.dtype),
            column_type=col_type,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            sample_values=sample_values,
        )
        
        # Add numeric stats if applicable
        if col_type == ColumnType.NUMERIC:
            try:
                profile.min_value = float(series.min()) if not pd.isna(series.min()) else None
                profile.max_value = float(series.max()) if not pd.isna(series.max()) else None
                profile.mean_value = float(series.mean()) if not pd.isna(series.mean()) else None
                profile.std_value = float(series.std()) if not pd.isna(series.std()) else None
            except (ValueError, TypeError):
                pass
        
        # Add categorical stats if applicable
        if col_type == ColumnType.CATEGORICAL:
            try:
                top_cats = series.value_counts().head(10).to_dict()
                profile.top_categories = {str(k): int(v) for k, v in top_cats.items()}
            except Exception:
                pass
        
        return profile
    
    def _contains_complex_objects(self, series: pd.Series) -> bool:
        """Check if series contains unhashable types like dicts or lists."""
        if series.dtype != object:
            return False
        
        # Check first few non-null values
        sample = series.dropna().head(10)
        for val in sample:
            if isinstance(val, (dict, list, set)):
                return True
        return False
    
    def _safe_value(self, value: Any) -> Any:
        """Convert complex values to safe serializable types."""
        if isinstance(value, (dict, list, set)):
            return str(value)[:100]
        if isinstance(value, (pd.Timestamp, np.datetime64)):
            return str(value)
        return value
    
    def _detect_column_type(self, series: pd.Series, unique_count: int) -> ColumnType:
        """Detect the semantic type of a column."""
        dtype = series.dtype
        
        # Check for boolean
        try:
            if dtype == bool or set(series.dropna().unique()).issubset({True, False, 0, 1}):
                if unique_count <= 2:
                    return ColumnType.BOOLEAN
        except TypeError:
            pass
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return ColumnType.TEMPORAL
        
        # Try to parse as datetime if object type
        if dtype == object:
            if self._is_datetime_column(series):
                return ColumnType.TEMPORAL
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(dtype):
            # High cardinality numeric = truly numeric
            if unique_count > self.CATEGORICAL_THRESHOLD:
                return ColumnType.NUMERIC
            # Low cardinality might be categorical
            return ColumnType.NUMERIC
        
        # Check for categorical (object/string with low cardinality)
        if dtype == object or pd.api.types.is_string_dtype(dtype):
            if unique_count <= self.CATEGORICAL_THRESHOLD:
                return ColumnType.CATEGORICAL
            else:
                return ColumnType.TEXT
        
        return ColumnType.UNKNOWN
    
    def _is_datetime_column(self, series: pd.Series) -> bool:
        """Check if a string column contains datetime values."""
        sample = series.dropna().head(100)
        if len(sample) == 0:
            return False
        
        # Check if values are strings first
        if not all(isinstance(v, str) for v in sample.head(5)):
            return False
        
        try:
            pd.to_datetime(sample, format='mixed')
            return True
        except (ValueError, TypeError):
            return False
    
    def suggest_charts(self, df: pd.DataFrame) -> list[ChartSuggestion]:
        """
        Suggest appropriate chart types based on the data.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List of ChartSuggestion objects sorted by relevance
        """
        columns = [self._analyze_column(df, col) for col in df.columns]
        return self._suggest_charts(df, columns)
    
    def _suggest_charts(
        self, 
        df: pd.DataFrame, 
        columns: list[ColumnProfile]
    ) -> list[ChartSuggestion]:
        """Generate chart suggestions based on column profiles."""
        suggestions = []
        
        numeric_cols = [c for c in columns if c.column_type == ColumnType.NUMERIC]
        categorical_cols = [c for c in columns if c.column_type == ColumnType.CATEGORICAL]
        temporal_cols = [c for c in columns if c.column_type == ColumnType.TEMPORAL]
        
        # Time series: temporal x, numeric y
        if temporal_cols and numeric_cols:
            for temp_col in temporal_cols[:1]:
                for num_col in numeric_cols[:3]:
                    suggestions.append(ChartSuggestion(
                        chart_type=ChartType.LINE,
                        x_column=temp_col.name,
                        y_columns=[num_col.name],
                        reasoning=f"Série temporelle: {num_col.name} en fonction du temps",
                        score=0.95,
                    ))
        
        # Scatter: 2 numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.SCATTER,
                x_column=numeric_cols[0].name,
                y_columns=[numeric_cols[1].name],
                color_column=categorical_cols[0].name if categorical_cols else None,
                reasoning=f"Corrélation entre {numeric_cols[0].name} et {numeric_cols[1].name}",
                score=0.9,
            ))
        
        # Bar chart: categorical x, numeric y
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            if cat_col.unique_count <= 15:  # Reasonable number of bars
                suggestions.append(ChartSuggestion(
                    chart_type=ChartType.BAR,
                    x_column=cat_col.name,
                    y_columns=[numeric_cols[0].name],
                    reasoning=f"Comparaison de {numeric_cols[0].name} par {cat_col.name}",
                    score=0.85,
                ))
        
        # Histogram: single numeric
        for num_col in numeric_cols[:2]:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.HISTOGRAM,
                x_column=num_col.name,
                y_columns=[],
                reasoning=f"Distribution de {num_col.name}",
                score=0.7,
            ))
        
        # Box plot: numeric by categorical
        if categorical_cols and numeric_cols:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.BOX,
                x_column=categorical_cols[0].name,
                y_columns=[numeric_cols[0].name],
                reasoning=f"Distribution de {numeric_cols[0].name} par {categorical_cols[0].name}",
                score=0.75,
            ))
        
        # Heatmap: correlation matrix for multiple numeric
        if len(numeric_cols) >= 3:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.HEATMAP,
                x_column="__correlation__",
                y_columns=[c.name for c in numeric_cols],
                reasoning="Matrice de corrélation des variables numériques",
                score=0.65,
            ))
        
        # Sort by score
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions
    
    def get_column_stats(self, df: pd.DataFrame, column: str) -> dict:
        """Get detailed statistics for a specific column."""
        series = df[column]
        stats = {
            "count": int(series.count()),
            "null_count": int(series.isnull().sum()),
        }
        
        try:
            stats["unique"] = int(series.nunique())
        except TypeError:
            stats["unique"] = 0
        
        if pd.api.types.is_numeric_dtype(series):
            try:
                stats.update({
                    "min": float(series.min()) if not pd.isna(series.min()) else None,
                    "max": float(series.max()) if not pd.isna(series.max()) else None,
                    "mean": float(series.mean()) if not pd.isna(series.mean()) else None,
                    "median": float(series.median()) if not pd.isna(series.median()) else None,
                    "std": float(series.std()) if not pd.isna(series.std()) else None,
                    "q25": float(series.quantile(0.25)) if not pd.isna(series.quantile(0.25)) else None,
                    "q75": float(series.quantile(0.75)) if not pd.isna(series.quantile(0.75)) else None,
                })
            except (ValueError, TypeError):
                pass
        
        return stats
