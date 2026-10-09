"""
E-Waste Classification Service

This is a BASELINE/RULE-BASED classifier for demo purposes.
NO trained ML model is used - this is keyword matching only.

In production, replace with:
- Trained computer vision model (ResNet, EfficientNet, etc.)
- Cloud ML service (AWS Rekognition Custom Labels, Google AutoML Vision)
- Fine-tuned model on e-waste dataset

The confidence scores returned are ESTIMATED based on keyword matches,
not actual ML confidence scores.
"""

from typing import List, Dict, Optional
import re


# E-waste categories and their keyword patterns
CATEGORY_KEYWORDS = {
    "mobile_phone": [
        "phone", "mobile", "smartphone", "iphone", "android", "samsung", "nokia",
        "motorola", "oneplus", "xiaomi", "oppo", "vivo", "realme"
    ],
    "laptop": [
        "laptop", "notebook", "macbook", "thinkpad", "chromebook", "ultrabook"
    ],
    "battery": [
        "battery", "batteries", "cell", "lithium", "aa", "aaa", "power bank",
        "rechargeable"
    ],
    "cable": [
        "cable", "wire", "charger", "usb", "hdmi", "adapter", "cord", "connector",
        "plug"
    ],
    "monitor": [
        "monitor", "display", "screen", "lcd", "led", "crt", "television", "tv"
    ],
    "keyboard": [
        "keyboard", "keys", "mechanical keyboard"
    ],
    "mouse": [
        "mouse", "mice", "trackpad", "touchpad"
    ],
    "tablet": [
        "tablet", "ipad", "kindle"
    ],
    "printer": [
        "printer", "scanner", "fax", "copier", "ink", "toner"
    ],
    "hard_drive": [
        "hard drive", "hdd", "ssd", "storage", "disk", "usb drive", "flash drive"
    ],
    "router": [
        "router", "modem", "access point", "networking equipment"
    ],
    "camera": [
        "camera", "webcam", "gopro", "dslr", "camcorder"
    ],
}


# Safety tips by category
SAFETY_TIPS = {
    "mobile_phone": [
        "Remove SIM card and memory card before disposal",
        "Factory reset the device to erase personal data",
        "Handle lithium battery with care - do not puncture or expose to heat",
        "Keep device dry and away from flammable materials"
    ],
    "laptop": [
        "Remove all personal data and perform a factory reset",
        "Remove the battery if possible",
        "Handle lithium batteries with extreme care",
        "Keep away from moisture and heat sources",
        "Remove any external storage devices"
    ],
    "battery": [
        "⚠️ CRITICAL: Do not puncture, crush, or short-circuit batteries",
        "Keep terminals covered with tape to prevent short circuits",
        "Store in a cool, dry place away from flammable materials",
        "Never throw in regular trash - batteries contain hazardous materials",
        "Lithium batteries can catch fire if damaged"
    ],
    "cable": [
        "Wrap cables neatly to prevent tangling",
        "Check for exposed wires that could be hazardous",
        "Safe to handle - low risk category"
    ],
    "monitor": [
        "Handle with care - screens can shatter",
        "CRT monitors contain hazardous materials - extra caution required",
        "Keep upright during transport",
        "Do not attempt to disassemble"
    ],
    "keyboard": [
        "Clean and dry before disposal",
        "Low risk category - safe to handle"
    ],
    "mouse": [
        "Remove batteries if wireless",
        "Low risk category - safe to handle"
    ],
    "tablet": [
        "Factory reset to erase personal data",
        "Handle lithium battery with care",
        "Do not puncture or expose to heat",
        "Keep away from moisture"
    ],
    "printer": [
        "Remove ink/toner cartridges separately",
        "Cartridges should be recycled separately",
        "Handle with care - may contain sharp edges"
    ],
    "hard_drive": [
        "⚠️ Contains personal data - securely wipe before disposal",
        "Consider professional data destruction services",
        "Physical destruction recommended for sensitive data",
        "Safe to handle but fragile"
    ],
    "router": [
        "Factory reset to erase network settings",
        "Remove any SIM cards or storage",
        "Low risk category"
    ],
    "camera": [
        "Remove memory cards and batteries",
        "Factory reset if digital camera",
        "Handle lenses with care to avoid breakage"
    ],
}


# Estimated weights (kg) - baseline estimates
ESTIMATED_WEIGHTS = {
    "mobile_phone": 0.15,
    "laptop": 2.0,
    "battery": 0.05,
    "cable": 0.02,
    "monitor": 5.0,
    "keyboard": 0.5,
    "mouse": 0.1,
    "tablet": 0.4,
    "printer": 4.0,
    "hard_drive": 0.3,
    "router": 0.3,
    "camera": 0.5,
}


# Special care categories (high risk)
SPECIAL_CARE_CATEGORIES = {"battery", "monitor", "laptop", "mobile_phone", "tablet"}


def classify_ewaste(item_name: str) -> Dict[str, any]:
    """
    Classify e-waste item using rule-based keyword matching.

    BASELINE IMPLEMENTATION - Not a trained ML model.

    Args:
        item_name: Name or description of the e-waste item

    Returns:
        Classification result with category, confidence, safety tips, etc.
    """
    item_lower = item_name.lower().strip()

    if not item_lower:
        return {
            "category": "unknown",
            "confidence_score": 0.0,
            "safety_tips": ["Unable to classify - please provide item description"],
            "estimated_weight_kg": None,
            "raw_label": item_name,
            "special_care_needed": False,
            "classifier_type": "baseline_keywords",
            "warning": "This is a baseline classifier, not a trained ML model"
        }

    # Find matching category with scoring based on keyword specificity
    best_match = None
    max_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in item_lower:
                # Longer keywords get higher weight (more specific)
                word_weight = len(keyword.split())
                score += word_weight

        if score > max_score:
            max_score = score
            best_match = category

    # If no match found, classify as "other_ewaste"
    if best_match is None or max_score == 0:
        return {
            "category": "other_ewaste",
            "confidence_score": 0.3,  # Low confidence for unknown items
            "safety_tips": [
                "General e-waste item detected",
                "Handle with care and keep dry",
                "Do not attempt to disassemble",
                "Consult with recycler for proper handling"
            ],
            "estimated_weight_kg": 1.0,  # Default estimate
            "raw_label": item_name,
            "special_care_needed": True,  # Unknown items need caution
            "classifier_type": "baseline_keywords",
            "warning": "This is a baseline classifier, not a trained ML model"
        }

    # Calculate estimated confidence based on keyword matches
    # This is NOT a real ML confidence score, just an estimate
    total_keywords = len(CATEGORY_KEYWORDS[best_match])
    confidence = min(0.95, 0.6 + (max_score / (total_keywords * 2)) * 0.35)

    return {
        "category": best_match,
        "confidence_score": round(confidence, 3),
        "safety_tips": SAFETY_TIPS.get(best_match, ["Handle with care"]),
        "estimated_weight_kg": ESTIMATED_WEIGHTS.get(best_match, 1.0),
        "raw_label": item_name,
        "special_care_needed": best_match in SPECIAL_CARE_CATEGORIES,
        "classifier_type": "baseline_keywords",
        "warning": "This is a baseline classifier, not a trained ML model"
    }


def get_supported_categories() -> List[str]:
    """Get list of supported e-waste categories."""
    return list(CATEGORY_KEYWORDS.keys()) + ["other_ewaste"]


def get_category_info(category: str) -> Optional[Dict[str, any]]:
    """Get information about a specific category."""
    if category not in CATEGORY_KEYWORDS and category != "other_ewaste":
        return None

    return {
        "category": category,
        "safety_tips": SAFETY_TIPS.get(category, ["Handle with care"]),
        "estimated_weight_kg": ESTIMATED_WEIGHTS.get(category, 1.0),
        "special_care_needed": category in SPECIAL_CARE_CATEGORIES,
    }
