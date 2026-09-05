"""
Base Agent Interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from src.models.schemas import RawPost


class BaseAgent(ABC):
    @abstractmethod
    def process(self, post: RawPost) -> Dict[str, Any]:
        """Process a RawPost and return structured classification results."""
        pass
