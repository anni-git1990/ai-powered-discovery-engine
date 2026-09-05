"""
Slang Normalizer Module.
Standardizes Indian e-commerce, fashion, and Hinglish terminology into canonical forms.
"""
import re
from typing import Dict


class SlangNormalizer:
    SLANG_DICTIONARY: Dict[str, str] = {
        r'\b(ootd)\b': 'outfit of the day',
        r'\b(cod)\b': 'cash on delivery',
        r'\b(bogo)\b': 'buy one get one',
        r'\b(mrp)\b': 'maximum retail price',
        r'\b(eors)\b': 'end of reason sale',
        r'\b(bff)\b': 'big fashion festival',
        r'\b(paisa\s+vasool)\b': 'value for money',
        r'\b(bakwas|bekar|ganda|ghatiya)\b': 'poor quality',
        r'\b(chota|choti|fitting\s+issue|size\s+mismatch)\b': 'size fit issue',
        r'\b(bada|badi)\b': 'oversized fit',
        r'\b(wishlisted|wishlisting)\b': 'add to wishlist',
        r'\b(haul)\b': 'product review collection',
    }

    def normalize(self, text: str) -> str:
        """Normalize slang, abbreviations, and Hinglish fashion terms."""
        if not text:
            return ""

        normalized = text
        for pattern, replacement in self.SLANG_DICTIONARY.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
