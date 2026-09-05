"""
Semantic & Processing Cache Module.
Prevents duplicate LLM calls and processing for identical text inputs.
"""
import hashlib
from typing import Any, Dict, Optional


class ProcessingCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    def _hash_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[Any]:
        key = self._hash_key(text)
        if key in self._cache:
            self.hits += 1
            return self._cache[key]
        self.misses += 1
        return None

    def set(self, text: str, value: Any) -> None:
        key = self._hash_key(text)
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, int]:
        return {
            "cached_entries": len(self._cache),
            "hits": self.hits,
            "misses": self.misses
        }
