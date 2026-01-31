# ============================================================================
# File 1: config.py - Configuration Settings
# ============================================================================
"""
Configuration file: Re-exports from shared module for backward compatibility.

NOTE: This file is kept for backward compatibility. New code should import
directly from shared.constants instead:

    from shared.constants import (
        SUPPORTED_SPECIES, SUPPORTED_CATEGORIES, RISK_LEVELS,
        MODEL_CONFIG, OUTPUT_LIMITS, INPUT_LIMITS
    )
"""

# Import from single source of truth
from shared.constants import (
    SUPPORTED_SPECIES,
    SUPPORTED_CATEGORIES,
    RISK_LEVEL_DESCRIPTIONS as RISK_LEVELS,  # Alias for backward compatibility
    MODEL_CONFIG,
    OUTPUT_LIMITS,
    INPUT_LIMITS,
    # Also export these for new code
    SymptomCategory,
    RiskLevel,
    SEVERITY_TO_RISK_LEVEL,
    normalize_risk_level,
    DEFAULT_DISCLAIMER,
    TIMEOUT_CONFIG,
)

# Re-export all for backward compatibility
__all__ = [
    "SUPPORTED_SPECIES",
    "SUPPORTED_CATEGORIES", 
    "RISK_LEVELS",
    "MODEL_CONFIG",
    "OUTPUT_LIMITS",
    "INPUT_LIMITS",
    "SymptomCategory",
    "RiskLevel",
    "SEVERITY_TO_RISK_LEVEL",
    "normalize_risk_level",
    "DEFAULT_DISCLAIMER",
    "TIMEOUT_CONFIG",
]
