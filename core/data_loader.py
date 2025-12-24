"""Data loading module for FigGen - supports CSV, JSON, YAML, Excel."""

import io
from pathlib import Path
from typing import Union, BinaryIO
import pandas as pd
import json
import yaml


class DataLoader:
    """Load data from various file formats into pandas DataFrames."""
    
    SUPPORTED_FORMATS = {
        ".csv": "csv",
        ".tsv": "csv",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xlsx": "excel",
        ".xls": "excel",
        ".parquet": "parquet",
    }
    
    def __init__(self):
        """Initialize the data loader."""
        self._last_error: str | None = None
    
    @property
    def last_error(self) -> str | None:
        """Return the last error message."""
        return self._last_error
    
    def detect_format(self, file: Union[str, Path, BinaryIO]) -> str:
        """
        Detect the file format from extension or content.
        
        Args:
            file: File path or file-like object
            
        Returns:
            Format string: 'csv', 'json', 'yaml', 'excel', 'parquet', or 'unknown'
        """
        if isinstance(file, (str, Path)):
            ext = Path(file).suffix.lower()
            return self.SUPPORTED_FORMATS.get(ext, "unknown")
        
        # For file-like objects, try to get name attribute
        if hasattr(file, "name"):
            ext = Path(file.name).suffix.lower()
            return self.SUPPORTED_FORMATS.get(ext, "unknown")
        
        return "unknown"
    
    def load(self, file: Union[str, Path, BinaryIO], format: str | None = None) -> pd.DataFrame | None:
        """
        Load data from a file into a pandas DataFrame.
        
        Args:
            file: File path or file-like object
            format: Optional format override ('csv', 'json', 'yaml', 'excel', 'parquet')
            
        Returns:
            pandas DataFrame or None if loading fails
        """
        self._last_error = None
        
        # Detect format if not provided
        if format is None:
            format = self.detect_format(file)
        
        if format == "unknown":
            self._last_error = "Format de fichier non reconnu"
            return None
        
        try:
            if format == "csv":
                return self._load_csv(file)
            elif format == "json":
                return self._load_json(file)
            elif format == "yaml":
                return self._load_yaml(file)
            elif format == "excel":
                return self._load_excel(file)
            elif format == "parquet":
                return self._load_parquet(file)
            else:
                self._last_error = f"Format non supporté: {format}"
                return None
        except Exception as e:
            self._last_error = f"Erreur de chargement: {str(e)}"
            return None
    
    def _load_csv(self, file: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load CSV file with automatic delimiter detection."""
        # Try to detect delimiter
        if isinstance(file, (str, Path)):
            # Read a sample to detect delimiter
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                sample = f.read(4096)
        else:
            # For file-like objects
            pos = file.tell() if hasattr(file, "tell") else 0
            sample = file.read(4096)
            if isinstance(sample, bytes):
                sample = sample.decode("utf-8", errors="replace")
            if hasattr(file, "seek"):
                file.seek(pos)
        
        # Detect delimiter
        delimiter = self._detect_delimiter(sample)
        
        # Load with detected delimiter
        if isinstance(file, (str, Path)):
            return pd.read_csv(file, delimiter=delimiter, encoding="utf-8", on_bad_lines="skip")
        else:
            if hasattr(file, "seek"):
                file.seek(0)
            return pd.read_csv(file, delimiter=delimiter, encoding="utf-8", on_bad_lines="skip")
    
    def _detect_delimiter(self, sample: str) -> str:
        """Detect CSV delimiter from sample."""
        delimiters = [",", ";", "\t", "|"]
        counts = {d: sample.count(d) for d in delimiters}
        return max(counts, key=counts.get) if max(counts.values()) > 0 else ","
    
    def _load_json(self, file: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load JSON file - handles arrays and objects."""
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            if hasattr(file, "seek"):
                file.seek(0)
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            data = json.loads(content)
        
        # Handle different JSON structures
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Check if it's a records-style dict
            if all(isinstance(v, list) for v in data.values()):
                return pd.DataFrame(data)
            else:
                # Try to normalize nested structure
                return pd.json_normalize(data)
        else:
            raise ValueError("Structure JSON non supportée")
    
    def _load_yaml(self, file: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load YAML file."""
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            if hasattr(file, "seek"):
                file.seek(0)
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            data = yaml.safe_load(content)
        
        # Convert to DataFrame (similar to JSON)
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if all(isinstance(v, list) for v in data.values()):
                return pd.DataFrame(data)
            else:
                return pd.json_normalize(data)
        else:
            raise ValueError("Structure YAML non supportée")
    
    def _load_excel(self, file: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load Excel file (first sheet by default)."""
        return pd.read_excel(file, sheet_name=0)
    
    def _load_parquet(self, file: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(file)
    
    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        return list(self.SUPPORTED_FORMATS.keys())
