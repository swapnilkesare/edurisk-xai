import pandas as pd
from .base import DataSource
import os

class CSVDataSource(DataSource):
    """Data source for loading student records from a CSV file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def fetch_data(self) -> pd.DataFrame:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file not found at {self.file_path}")
        return pd.read_csv(self.file_path)
        
    def get_source_name(self) -> str:
        return f"CSV Source ({os.path.basename(self.file_path)})"
