"""
Text Deduplication Engine using Shingle Hashes and Jaccard Similarity.
Detects cross-platform duplicate posts and spam.
"""
import hashlib
import re
from typing import List, Set


class Deduplicator:
    def __init__(self, similarity_threshold: float = 0.7, k_shingle: int = 2):
        self.similarity_threshold = similarity_threshold
        self.k_shingle = k_shingle
        self.seen_exact_hashes: Set[str] = set()
        self.seen_shingle_sets: List[Set[str]] = []

    def _get_exact_hash(self, text: str) -> str:
        """Generate SHA-256 hash of normalized text."""
        clean = re.sub(r'\W+', '', text.lower())
        return hashlib.sha256(clean.encode('utf-8')).hexdigest()

    def _get_shingles(self, text: str) -> Set[str]:
        """Extract word k-shingles from text."""
        words = re.findall(r'\w+', text.lower())
        if len(words) < self.k_shingle:
            return set(words)
        return {" ".join(words[i:i + self.k_shingle]) for i in range(len(words) - self.k_shingle + 1)}

    def _jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Compute Jaccard similarity coefficient between two shingle sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0

    def is_duplicate(self, text: str) -> bool:
        """Check if text is an exact or near-duplicate of previously processed text."""
        if not text or len(text.strip()) == 0:
            return True

        # 1. Exact Match Check
        exact_hash = self._get_exact_hash(text)
        if exact_hash in self.seen_exact_hashes:
            return True

        # 2. Near-Duplicate Jaccard Check
        current_shingles = self._get_shingles(text)
        for existing_shingles in self.seen_shingle_sets:
            similarity = self._jaccard_similarity(current_shingles, existing_shingles)
            if similarity >= self.similarity_threshold:
                return True

        # Mark as seen
        self.seen_exact_hashes.add(exact_hash)
        self.seen_shingle_sets.append(current_shingles)
        return False

    def reset(self) -> None:
        """Reset deduplication state."""
        self.seen_exact_hashes.clear()
        self.seen_shingle_sets.clear()
