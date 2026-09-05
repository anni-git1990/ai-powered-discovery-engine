"""
Dashboard label formatting utilities.
Converts raw uppercase enum identifiers into user-friendly simple dashboard labels.
"""
from typing import Any

LABEL_MAP = {
    # Primary Blockers - Six Core Friction Themes
    "SIZE_FIT_UNCERTAINTY": "Size & Fit",
    "QUALITY_FABRIC_CONCERN": "Product Quality",
    "REVIEW_TRUST_DEFICIT": "Review Trust",
    "STYLING_OCCASION_UNCERTAINTY": "Styling & Occasion",
    "PRICE_VALUE_SKEPTICISM": "Price & Value",
    "DELIVERY_RETURN_FRICTION": "Delivery & Returns",
    "INVENTORY_STOCK_OUT": "Stock Availability",
    "EVENT_TIMING_POSTPONEMENT": "Event Timing Postponement",
    "NONE": "None",



    # Wishlist Motivations
    "HIGH_BUYING_INTENT": "High Buying Intent",
    "PRICE_DISCOUNT_WATCH": "Price & Discount Watch",
    "STYLING_OCCASION_MATCHING": "Styling & Occasion Matching",
    "COMPARISON_DECISION": "Comparison & Decision",
    "LOW_INTENT_BOOKMARKING": "Low Intent Bookmarking",

    # User Segments / Personas
    "BUDGET_SENSITIVE_SAVER": "Budget-Sensitive Saver",
    "FIT_CONSCIOUS_BUYER": "Fit-Conscious Buyer",
    "TREND_OCCASION_SHOPPER": "Trend & Occasion Shopper",
    "QUALITY_SEEKER": "Quality Seeker",
    "GENERAL_SHOPPER": "General Shopper",

    # Source Platforms
    "PLAY_STORE": "Play Store",
    "APP_STORE": "App Store",
    "REDDIT": "Reddit",
    "YOUTUBE": "YouTube",
    "FORUM": "Forum",
}


def format_label(value: Any) -> str:
    """
    Format enum or raw uppercase string into user-friendly simple dashboard label.
    Example:
        format_label("SIZE_FIT_UNCERTAINTY") -> "Size & Fit Uncertainty"
        format_label(PrimaryBlocker.SIZE_FIT_UNCERTAINTY) -> "Size & Fit Uncertainty"
    """
    if value is None:
        return ""
    val_str = str(value.value) if hasattr(value, "value") else str(value)
    if val_str in LABEL_MAP:
        return LABEL_MAP[val_str]
    
    # Fallback for any unmapped UPPER_SNAKE_CASE string
    formatted = val_str.replace("_", " ").title()
    formatted = formatted.replace(" And ", " & ")
    return formatted
