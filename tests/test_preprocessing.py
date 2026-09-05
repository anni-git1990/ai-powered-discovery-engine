"""
Unit tests for Preprocessing Modules: PII Sanitizer, Slang Normalizer, Deduplicator.
"""
from src.preprocessing.pii_sanitizer import PIISanitizer
from src.preprocessing.slang_normalizer import SlangNormalizer
from src.preprocessing.deduplicator import Deduplicator


def test_pii_sanitizer_masks_emails_and_phones():
    sanitizer = PIISanitizer()
    text = "Call me at 9876543210 or email user@example.com regarding my order #40928192 @myntra_help."
    sanitized = sanitizer.sanitize(text)

    assert "9876543210" not in sanitized
    assert "user@example.com" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "[REDACTED_ORDER_ID]" in sanitized
    assert "[REDACTED_HANDLE]" in sanitized


def test_slang_normalizer_replaces_fashion_slang():
    normalizer = SlangNormalizer()
    text = "Great OOTD for BOGO sale! Was bakwas quality, chota size, MRP high."
    normalized = normalizer.normalize(text)

    assert "outfit of the day" in normalized
    assert "buy one get one" in normalized
    assert "poor quality" in normalized
    assert "size fit issue" in normalized
    assert "maximum retail price" in normalized


def test_deduplicator_identifies_exact_and_near_duplicates():
    dedup = Deduplicator(similarity_threshold=0.7)

    text1 = "Is this Myntra dress size true to fit?"
    text2 = "Is this Myntra dress size true to fit?"  # Exact duplicate
    text3 = "Is this Myntra dress size true to fit for women?"  # Near duplicate
    text4 = "Looking for Diwali sale discounts on ethnic wear."  # Unique

    assert not dedup.is_duplicate(text1)  # First time -> not duplicate
    assert dedup.is_duplicate(text2)      # Exact duplicate
    assert dedup.is_duplicate(text3)      # Near duplicate
    assert not dedup.is_duplicate(text4)  # Unique text
