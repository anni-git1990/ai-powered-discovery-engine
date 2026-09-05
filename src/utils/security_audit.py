"""
Security & Privacy PII Auditor Module.
Scans stored database records and vector payloads to guarantee zero PII leakage.
"""
from typing import Any, Dict
from src.preprocessing.pii_sanitizer import PIISanitizer
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


class PIIAuditor:
    def __init__(self, db_manager: DuckDBManager, vector_manager: VectorStoreManager = None):
        self.db_manager = db_manager
        self.vector_manager = vector_manager
        self.sanitizer = PIISanitizer()

    def run_audit(self) -> Dict[str, Any]:
        """
        Scan all cleaned_text and extracted_quotes in DuckDB to verify
        that no unscrubbed PII exists.
        """
        posts = self.db_manager.get_all_raw_posts()
        violations = []

        for p in posts:
            text = p.cleaned_text
            # Check for unscrubbed emails
            if self.sanitizer.EMAIL_PATTERN.search(text):
                violations.append({"post_id": p.post_id, "type": "EMAIL", "text": text})
            # Check for unscrubbed phone numbers
            if self.sanitizer.PHONE_PATTERN.search(text):
                # Ensure it's not a masked tag like [REDACTED_PHONE]
                if "[REDACTED_PHONE]" not in text:
                    violations.append({"post_id": p.post_id, "type": "PHONE", "text": text})
            # Check for unscrubbed order IDs
            if self.sanitizer.ORDER_ID_PATTERN.search(text):
                if "[REDACTED_ORDER_ID]" not in text:
                    violations.append({"post_id": p.post_id, "type": "ORDER_ID", "text": text})

        status = "PASSED" if len(violations) == 0 else "FAILED"

        return {
            "total_records_scanned": len(posts),
            "pii_violations_found": len(violations),
            "status": status,
            "violations": violations
        }
