"""
PII Sanitizer & Anonymizer Module.
Strips personal identifiable information (emails, phone numbers, handles, order IDs, addresses).
"""
import re


class PIISanitizer:
    # Regex Patterns for PII Detection
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    )

    # Indian Phone Number Formats (+91 9876543210, 09876543210, 9876543210, 98765-43210)
    PHONE_PATTERN = re.compile(
        r'(?:\+?91[\s-]?)?(?:0?[6-9]\d{9}|\b[6-9]\d{4}[\s-]\d{5}\b|\b[6-9]\d{9}\b)'
    )

    # Social Media / App Handle Tags (@username)
    HANDLE_PATTERN = re.compile(r'@[\w_]+')

    # Order IDs & Transaction Hashes (e.g. Order #40928192, TXN-928103)
    ORDER_ID_PATTERN = re.compile(
        r'\b(?:order|ord|txn|ref|tracking)[\s#:-]*[A-Za-z0-9]{5,20}\b',
        re.IGNORECASE
    )

    # Indian 6-Digit Pincodes
    PINCODE_PATTERN = re.compile(r'\b[1-9][0-9]{5}\b')

    def sanitize(self, text: str) -> str:
        """Sanitize raw text by replacing detected PII with anonymized tags."""
        if not text:
            return ""

        sanitized = text

        # 1. Mask Email Addresses
        sanitized = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)

        # 2. Mask Phone Numbers
        sanitized = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)

        # 3. Mask Order / Tracking IDs
        sanitized = self.ORDER_ID_PATTERN.sub("[REDACTED_ORDER_ID]", sanitized)

        # 4. Mask Social Handles
        sanitized = self.HANDLE_PATTERN.sub("[REDACTED_HANDLE]", sanitized)

        # 5. Mask Indian Pincodes
        sanitized = self.PINCODE_PATTERN.sub("[REDACTED_PINCODE]", sanitized)

        # Clean excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        return sanitized
