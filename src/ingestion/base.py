"""
Base Connector Interface for Ingestion Modules.
"""
from abc import ABC, abstractmethod
from typing import List
from src.models.schemas import RawPost


class BaseConnector(ABC):
    @abstractmethod
    def fetch_posts(self, limit: int = 50) -> List[RawPost]:
        """Fetch raw posts from the source platform."""
        pass
