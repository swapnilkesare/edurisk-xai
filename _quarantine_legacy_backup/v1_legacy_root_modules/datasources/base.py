from abc import ABC, abstractmethod
import pandas as pd

class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """Fetch data and return as a pandas DataFrame."""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name/identifier of this data source."""
        pass
