# ============================================================================
# File 4: task3_input_guardrails.py - Task 3.3 Input Guardrails
# ============================================================================
"""
Task 3.3: Input Guardrails

This file implements the 5-layer input guardrails from the document:
Layer A - Scope Guardrails (MVP boundaries)
Layer B - Structured Field Completeness Check
Layer C - Immediate ER Pre-check (Rule engine first)
Layer D - Input Quality Guardrails (Sanitization and limits)
Layer E - Prompt Injection & Unsafe Request Detection

According to the document:
"We enforce guardrails in a fixed order to ensure safety and efficiency"

NOTE: This file now imports from shared module for consistency.
"""

import re
from typing import Dict, Any, Tuple, Optional, List

# Import from shared module (single source of truth)
from shared.constants import (
    SUPPORTED_SPECIES,
    SUPPORTED_CATEGORIES,
    INPUT_LIMITS,
)
from shared.red_flags import check_immediate_er
from llm_setup import get_er_template


# ============================================================================
# Part 1: Layer A - Scope Guardrails (MVP Boundaries)
# ============================================================================

class ScopeGuardrails:
    """
    Layer A: Scope Guardrails
    
    Check if input is within MVP support scope:
    - Only dogs and cats
    - Only 9 symptom categories
    """
    
    @staticmethod
    def check_species(species: str) -> Tuple[bool, Optional[str]]:
        """
        Check if pet species is supported
        
        Returns: (passed, error_message)
        """
        if not species:
            return False, "Please select your pet type (dog or cat)"
        
        species_lower = species.lower().strip()
        
        if species_lower not in ["dog", "cat"]:
            return False, f"Sorry, we currently only support dogs and cats. '{species}' is not supported."
        
        return True, None
    
    @staticmethod
    def check_category(category: str) -> Tuple[bool, Optional[str]]:
        """
        Check if symptom category is supported
        
        Returns: (passed, error_message)
        """
        if not category:
            return False, "Please select a symptom category"
        
        if category not in SUPPORTED_CATEGORIES:
            return False, f"Unsupported category: {category}. Please select from supported categories."
        
        return True, None
    
    @staticmethod
    def check_symptom_input(symptom_text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if symptom input is valid
        
        Returns: (passed, error_message)
        """
        if not symptom_text or not symptom_text.strip():
            return False, "Please describe your pet's symptoms"
        
        # Check if too short/meaningless
        cleaned = symptom_text.strip()
        if len(cleaned) < 5:
            return False, "Please provide more detailed symptom description"
        
        # Check if just a greeting
        greetings = ["hi", "hello", "hey", "help", "help me"]
        if cleaned.lower() in greetings:
            return False, "Please describe your pet's specific symptoms"
        
        return True, None


# ============================================================================
# Part 2: Layer B - Structured Field Completeness Check
# ============================================================================

class StructuredFieldsGuardrails:
    """
    Layer B: Structured Field Completeness Check
    
    Check if minimum required structured fields exist for each category
    """
    
    # Required fields per category
    REQUIRED_FIELDS = {
        "Breathing Issues": {
            "any_of": ["open_mouth_breathing", "gum_color", "respiratory_rate", "breathing_posture"],
            "message": "Please answer at least one breathing-related question"
        },
        "Urinary & Genital": {
            "all_of": ["sex"],
            "any_of": ["straining_no_urine", "hours_since_urination"],
            "message": "Please provide pet's sex and urination status"
        },
        "Concerning Behaviour Changes": {
            "any_of": ["seizure_status", "seizure_duration", "collapse"],
            "message": "Please describe specific behavior changes (seizures, collapse, etc.)"
        },
        "Stomach Upset": {
            "any_of": ["abdomen_distended", "unproductive_retching", "vomiting_frequency", "blood_present"],
            "message": "Please describe the gastrointestinal symptoms"
        },
        "Injury & Bleeding": {
            "any_of": ["heavy_bleeding", "bleeding_stopped_after_pressure", "wound_depth"],
            "message": "Please describe the wound and bleeding status"
        },
        "Ears, Eyes, and Mouth": {
            "any_of": ["eye_popped_out", "sudden_eye_bulging", "eye_discharge", "facial_swelling"],
            "message": "Please describe the eye/ear/mouth symptoms"
        },
        "Toxic Ingestion & Poisoning": {
            "any_of": ["suspected_ingestion", "what_was_eaten", "time_since_ingestion"],
            "message": "Please describe what was eaten and when"
        },
        "Itching & Skin Issues": {
            "any_of": ["facial_swelling", "hives_spreading", "breathing_changes_with_swelling"],
            "message": "Please describe the skin issue details"
        }
    }
    
    @classmethod
    def check_completeness(
        cls, 
        category: str, 
        structured_fields: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Check if structured fields are complete
        
        Args:
            category: Symptom category
            structured_fields: User-provided structured fields
            
        Returns:
            (is_complete, error_message, suggested_followup_questions)
        """
        if category not in cls.REQUIRED_FIELDS:
            return True, None, []
        
        requirements = cls.REQUIRED_FIELDS[category]
        
        # Check all_of (must have all)
        if "all_of" in requirements:
            for field in requirements["all_of"]:
                if not structured_fields.get(field):
                    return False, requirements["message"], cls._get_follow_up_questions(category)
        
        # Check any_of (must have at least one)
        if "any_of" in requirements:
            has_any = any(
                structured_fields.get(field) 
                for field in requirements["any_of"]
            )
            if not has_any:
                return False, requirements["message"], cls._get_follow_up_questions(category)
        
        return True, None, []
    
    @classmethod
    def _get_follow_up_questions(cls, category: str) -> List[str]:
        """
        Get follow-up questions for the category (max 2)
        """
        questions = {
            "Breathing Issues": [
                "Is your pet breathing with mouth open right now?",
                "What color are the gums? (pink/pale/blue-purple)"
            ],
            "Urinary & Genital": [
                "When was the last normal urination?",
                "Is there repeated straining with no urine produced?"
            ],
            "Concerning Behaviour Changes": [
                "Is there seizure activity? If so, how long?",
                "Is there collapse or inability to stand?"
            ],
            "Stomach Upset": [
                "Does the abdomen look swollen or distended?",
                "Is there unproductive retching (trying to vomit but nothing comes out)?"
            ],
            "Injury & Bleeding": [
                "Is the bleeding heavy? Does it stop with pressure?",
                "How deep is the wound? Can you see muscle or bone?"
            ],
            "Ears, Eyes, and Mouth": [
                "Is there obvious eye abnormality (bulging, swelling, discharge)?",
                "Is there facial swelling?"
            ],
            "Toxic Ingestion & Poisoning": [
                "What do you know or suspect was eaten?",
                "Approximately how long ago did this happen?"
            ],
            "Itching & Skin Issues": [
                "Is there facial swelling?",
                "Is the rash spreading quickly?"
            ]
        }
        return questions.get(category, [])[:2]


# ============================================================================
# Part 3: Layer C - Immediate ER Pre-check
# ============================================================================

class ERPreCheckGuardrails:
    """
    Layer C: Immediate ER Pre-check
    
    Run deterministic ER red flag check before calling LLM
    """
    
    # Text keyword fallback detection
    TEXT_ER_KEYWORDS = {
        "breathing": [
            "open mouth breathing", "can't breathe", "gasping", "blue gums",
            "choking", "struggling to breathe", "labored breathing",
            "breathing with mouth open", "mouth open", "cat panting",
            "panting cat", "cat breathing with mouth"
        ],
        "urinary": [
            "can't urinate", "straining to pee", "no urine", "blocked",
            "keeps going to litter box", "crying in litter box"
        ],
        "seizure": [
            "seizure", "convulsion", "fitting", "shaking uncontrollably"
        ],
        "bloat": [
            "bloat", "stomach twisted", "retching", "belly swollen",
            "trying to vomit nothing comes out"
        ],
        "bleeding": [
            "heavy bleeding", "won't stop bleeding", "gushing blood"
        ],
        "poisoning": [
            "ate chocolate", "ate grapes", "poisoning", "ate rat poison",
            "ate lilies", "ate xylitol", "ate antifreeze"
        ],
        "collapse": [
            "collapsed", "can't stand", "unresponsive", "unconscious"
        ]
    }
    
    @classmethod
    def check_text_for_er(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect ER keywords from text (fallback method)
        
        Returns: (is_er_detected, detected_category)
        """
        if not text:
            return False, None
        
        text_lower = text.lower()
        
        keyword_to_category = {
            "breathing": "Breathing Issues",
            "urinary": "Urinary & Genital",
            "seizure": "Concerning Behaviour Changes",
            "bloat": "Stomach Upset",
            "bleeding": "Injury & Bleeding",
            "poisoning": "Toxic Ingestion & Poisoning",
            "collapse": "Concerning Behaviour Changes"
        }
        
        for key, keywords in cls.TEXT_ER_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return True, keyword_to_category[key]
        
        return False, None
    
    @classmethod
    def run_er_precheck(
        cls, 
        structured_fields: Dict[str, Any], 
        user_text: str = ""
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Run complete ER pre-check
        
        Args:
            structured_fields: Structured fields
            user_text: User free text description
            
        Returns:
            (is_er_triggered, er_template_response)
        """
        # First check structured fields (more reliable)
        # Use shared module's check_immediate_er function (returns dict)
        er_result = check_immediate_er(structured_fields)
        
        if er_result["is_er"]:
            return True, get_er_template(er_result["category"])
        
        # If structured fields didn't trigger, check text keywords (fallback)
        is_text_er, text_category = cls.check_text_for_er(user_text)
        
        if is_text_er:
            return True, get_er_template(text_category)
        
        return False, None


# ============================================================================
# Part 4: Layer D - Input Quality Guardrails
# ============================================================================

class InputQualityGuardrails:
    """
    Layer D: Input Quality Guardrails
    
    Clean and validate input data
    """
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text input
        """
        if not text:
            return ""
        
        # Trim whitespace
        text = text.strip()
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text
    
    @staticmethod
    def check_text_length(text: str, max_length: int = None) -> Tuple[bool, str]:
        """
        Check text length and truncate if needed
        
        Returns: (is_within_limit, processed_text)
        """
        if max_length is None:
            max_length = INPUT_LIMITS["max_text_length"]
        
        if len(text) <= max_length:
            return True, text
        
        # Truncate
        truncated = text[:max_length]
        # Try to cut at sentence boundary
        last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
        
        if last_period > max_length * 0.7:
            truncated = truncated[:last_period + 1]
        
        return False, truncated
    
    @staticmethod
    def validate_image(
        file_size_bytes: int, 
        content_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate image file
        
        Returns: (is_valid, error_message)
        """
        # Check file type
        if content_type.lower() not in INPUT_LIMITS["allowed_image_types"]:
            return False, "Only JPG and PNG image formats are supported"
        
        # Check file size
        max_size = INPUT_LIMITS["max_image_size_mb"] * 1024 * 1024
        if file_size_bytes > max_size:
            return False, f"Image too large. Please upload an image smaller than {INPUT_LIMITS['max_image_size_mb']}MB"
        
        return True, None


# ============================================================================
# Part 5: Layer E - Prompt Injection & Unsafe Request Detection
# ============================================================================

class SafetyGuardrails:
    """
    Layer E: Prompt Injection & Unsafe Request Detection
    
    According to the document:
    "We do not block users from getting help, but we ignore instruction-like text 
     and enforce triage-only behavior."
    """
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r'ignore.*(previous|above|all|prior).*(instructions?|rules?|prompts?)',
        r'forget.*(your|all).*(instructions?|rules?)',
        r'pretend you are',
        r'act as if',
        r'reveal.*(system|hidden).*(prompt|instructions?)',
        r'disregard.*instructions',
        r'override.*rules',
    ]
    
    # Unsafe request patterns
    UNSAFE_REQUEST_PATTERNS = [
        r'give.*(dosage|dose)',
        r'how much.*medication',
        r'prescribe',
        r'definitive diagnosis',
        r'guarantee',
        r'100%.*safe',
        r'what disease does.*have',
    ]
    
    @classmethod
    def detect_injection(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect prompt injection attempts
        
        Returns: (is_injection_detected, detected_pattern)
        """
        if not text:
            return False, None
        
        text_lower = text.lower()
        
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, pattern
        
        return False, None
    
    @classmethod
    def detect_unsafe_request(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect unsafe requests (e.g., medication dosing)
        
        Returns: (is_detected, detected_pattern)
        """
        if not text:
            return False, None
        
        text_lower = text.lower()
        
        for pattern in cls.UNSAFE_REQUEST_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, pattern
        
        return False, None
    
    @classmethod
    def sanitize_for_safety(cls, text: str) -> str:
        """
        Sanitize text to remove potentially unsafe content
        """
        if not text:
            return ""
        
        # Remove obvious injection attempts
        for pattern in cls.INJECTION_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()


# ============================================================================
# Part 6: Unified Input Guardrails Class
# ============================================================================

class InputGuardrails:
    """
    Unified Input Guardrails Class
    
    Executes all checks in the order specified by the document:
    1. Sanitize and normalize input text
    2. Scope validation (species + supported categories)
    3. Structured field completeness check
    4. Immediate ER pre-check (structured first, then text fallback)
    5. Prompt injection / unsafe request detection
    6. If missing fields → return ≤2 follow-up questions
    """
    
    def __init__(self):
        self.scope = ScopeGuardrails()
        self.fields = StructuredFieldsGuardrails()
        self.er_check = ERPreCheckGuardrails()
        self.quality = InputQualityGuardrails()
        self.safety = SafetyGuardrails()
    
    def validate_all(
        self,
        species: str,
        category: str,
        structured_fields: Dict[str, Any],
        user_description: str = "",
        image_size: int = None,
        image_type: str = None
    ) -> Dict[str, Any]:
        """
        Run all input guardrail checks
        
        Returns a result dictionary:
        {
            "passed": bool,              # Whether all checks passed
            "error": str or None,        # Error message
            "is_er": bool,               # Whether ER was triggered
            "er_response": dict or None, # ER template response
            "needs_followup": bool,      # Whether follow-up questions needed
            "followup_questions": list,  # Follow-up question list
            "sanitized_text": str,       # Sanitized text
            "warnings": list             # Warning messages
        }
        """
        result = {
            "passed": False,
            "error": None,
            "is_er": False,
            "er_response": None,
            "needs_followup": False,
            "followup_questions": [],
            "sanitized_text": "",
            "warnings": []
        }
        
        # ===== Step 1: Sanitize and normalize input =====
        sanitized_text = self.quality.sanitize_text(user_description)
        within_limit, sanitized_text = self.quality.check_text_length(sanitized_text)
        if not within_limit:
            result["warnings"].append("Input text was truncated")
        result["sanitized_text"] = sanitized_text
        
        # ===== Step 2: Scope validation =====
        # Check species
        passed, error = self.scope.check_species(species)
        if not passed:
            result["error"] = error
            return result
        
        # Check category
        passed, error = self.scope.check_category(category)
        if not passed:
            result["error"] = error
            return result
        
        # Check symptom input
        passed, error = self.scope.check_symptom_input(sanitized_text)
        if not passed and not structured_fields:
            result["error"] = error
            return result
        
        # ===== Step 3: Structured field completeness =====
        complete, error, followup_questions = self.fields.check_completeness(
            category, structured_fields
        )
        if not complete:
            result["needs_followup"] = True
            result["followup_questions"] = followup_questions
        
        # ===== Step 4: Immediate ER pre-check =====
        # Include species and category in structured_fields for ER check
        er_check_fields = {
            "species": species,
            "category": category,
            **structured_fields
        }
        is_er, er_response = self.er_check.run_er_precheck(
            er_check_fields, sanitized_text
        )
        if is_er:
            result["passed"] = True
            result["is_er"] = True
            result["er_response"] = er_response
            return result
        
        # ===== Step 5: Safety detection =====
        is_injection, pattern = self.safety.detect_injection(sanitized_text)
        if is_injection:
            result["warnings"].append("Unusual input pattern detected and ignored")
            sanitized_text = self.safety.sanitize_for_safety(sanitized_text)
            result["sanitized_text"] = sanitized_text
        
        is_unsafe, pattern = self.safety.detect_unsafe_request(sanitized_text)
        if is_unsafe:
            result["warnings"].append("Note: We only provide triage guidance, not medication dosing or diagnosis")
        
        # ===== Step 6: Image validation (if provided) =====
        if image_size is not None and image_type is not None:
            passed, error = self.quality.validate_image(image_size, image_type)
            if not passed:
                result["error"] = error
                return result
        
        # ===== All checks passed =====
        result["passed"] = True
        return result


