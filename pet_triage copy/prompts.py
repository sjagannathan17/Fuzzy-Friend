# ============================================================================
# prompts.py - Backward Compatibility Re-exports
# ============================================================================
"""
Prompt Templates - Re-exports from shared/prompts.py

NOTE: This file exists for backward compatibility only.
All prompt templates are defined in shared/prompts.py (single source of truth).

For new code, import directly from shared/prompts.py:
    from shared.prompts import (
        UNIFIED_SYSTEM_PROMPT,
        FEW_SHOT_EXAMPLES,
        build_triage_message,
        get_triage_system_prompt,
    )
"""

from typing import Dict, Any

# ============================================================================
# Re-export ALL from shared/prompts.py (single source of truth)
# ============================================================================
from shared.prompts import (
    # Core prompts
    UNIFIED_SYSTEM_PROMPT,
    DEVELOPER_PROMPT,
    RUNTIME_PROMPT_TEMPLATE,
    FEW_SHOT_EXAMPLES,
    INTAKE_PROMPT,
    FALLBACK_PROMPT,
    GLOBAL_SAFETY_RULES,

    # Functions
    build_runtime_prompt,
    build_case_summary,
    build_intake_message,
    build_triage_message,
    get_intake_system_prompt,
    get_triage_system_prompt,
    get_fallback_system_prompt,
    get_image_analysis_prompt,
)

# Legacy alias for backward compatibility
TRIAGE_PROMPT = UNIFIED_SYSTEM_PROMPT


# ============================================================================
# Image Analysis Message Builder (unique to this file)
# ============================================================================
# NOTE: The actual IMAGE_ANALYSIS_PROMPT used by the system is in
# RAG/image_analyzer.py (more detailed version for GPT-4V).
# This function is kept for any code that might reference it.

def build_image_analysis_message(symptom_context: str) -> str:
    """
    Build user message for image analysis.

    NOTE: For actual image analysis, use RAG/image_analyzer.py directly.
    This function is kept for backward compatibility.

    Args:
        symptom_context: Symptom context description

    Returns:
        User message text
    """
    prompt = get_image_analysis_prompt()
    return f"""
{prompt}

Symptom context reported by owner:
{symptom_context}

List relevant visual signals you observe in the photo.
"""


# ============================================================================
# Export list for `from prompts import *`
# ============================================================================
__all__ = [
    # Prompts
    "UNIFIED_SYSTEM_PROMPT",
    "DEVELOPER_PROMPT",
    "RUNTIME_PROMPT_TEMPLATE",
    "FEW_SHOT_EXAMPLES",
    "INTAKE_PROMPT",
    "FALLBACK_PROMPT",
    "GLOBAL_SAFETY_RULES",
    "TRIAGE_PROMPT",  # Legacy alias

    # Functions
    "build_runtime_prompt",
    "build_case_summary",
    "build_intake_message",
    "build_triage_message",
    "build_image_analysis_message",
    "get_intake_system_prompt",
    "get_triage_system_prompt",
    "get_fallback_system_prompt",
    "get_image_analysis_prompt",
]


