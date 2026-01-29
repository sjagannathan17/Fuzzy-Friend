# ============================================================================
# File 6: main.py - Main Application (Integrates All Tasks)
# ============================================================================
"""
Main Application: Pet Triage System

This file integrates all 4 tasks into a complete triage workflow:
1. Task 3.1 - LLM Selection & API Setup
2. Task 3.2 - Core Prompt Engineering
3. Task 3.3 - Input Guardrails
4. Task 3.4 - Output Guardrails

Flow:
User Input → Input Guardrails → (ER Check) → LLM Call → Output Guardrails → Response

NOTE: This file now imports from shared module for consistency.
"""

import json
from typing import Dict, Any, Optional

# Import from shared module (single source of truth)
from shared.constants import SUPPORTED_CATEGORIES, RiskLevel
from shared.red_flags import check_immediate_er
from shared.schemas import get_fallback_response

# Import from our task files
from llm_setup import (
    get_openai_client,
    call_llm,
    call_llm_with_image,
    select_model,
    get_er_template
)
from prompts import (
    get_intake_system_prompt,
    get_triage_system_prompt,
    get_fallback_system_prompt,
    build_intake_message,
    build_triage_message,
    build_case_summary
)
from input_guardrails import InputGuardrails
from output_guardrails import OutputGuardrails


# Initialize guardrails
input_guardrails = InputGuardrails()
output_guardrails = OutputGuardrails()


# ============================================================================
# Main Triage Function
# ============================================================================

def run_triage(
    species: str,
    category: str,
    structured_fields: Dict[str, Any],
    user_description: str = "",
    pet_profile: Dict[str, Any] = None,
    image_base64: str = None,
    image_type: str = None
) -> Dict[str, Any]:
    """
    Main triage function that runs the complete workflow
    
    Args:
        species: Pet species (dog/cat)
        category: Symptom category
        structured_fields: Structured fields from UI
        user_description: User's free text description
        pet_profile: Pet profile information
        image_base64: Base64 encoded image (optional)
        image_type: Image MIME type (optional)
        
    Returns:
        Triage result dictionary
    """
    
    result = {
        "success": False,
        "response": None,
        "error": None,
        "warnings": [],
        "is_er": False,
        "model_used": None
    }
    
    # =========================================================================
    # STEP 1: INPUT GUARDRAILS
    # =========================================================================
    print("\n[Step 1] Running input guardrails...")
    
    # Calculate image size if provided
    image_size = len(image_base64) if image_base64 else None
    
    guardrail_result = input_guardrails.validate_all(
        species=species,
        category=category,
        structured_fields=structured_fields,
        user_description=user_description,
        image_size=image_size,
        image_type=image_type
    )
    
    # Check for errors
    if not guardrail_result["passed"]:
        result["error"] = guardrail_result["error"]
        return result
    
    # Collect warnings
    result["warnings"] = guardrail_result["warnings"]
    
    # Use sanitized text
    sanitized_description = guardrail_result["sanitized_text"]
    
    # =========================================================================
    # STEP 2: CHECK FOR IMMEDIATE ER (Hard Routing)
    # =========================================================================
    print("[Step 2] Checking for immediate ER conditions...")
    
    if guardrail_result["is_er"]:
        print("  ⚠️  EMERGENCY DETECTED - Returning ER template")
        result["success"] = True
        result["response"] = guardrail_result["er_response"]
        result["is_er"] = True
        result["model_used"] = "none (hard-routed ER)"
        return result
    
    # =========================================================================
    # STEP 3: HANDLE FOLLOW-UP QUESTIONS (if needed)
    # =========================================================================
    if guardrail_result["needs_followup"]:
        print("[Step 3] Missing critical fields - returning follow-up questions")
        result["success"] = True
        result["response"] = {
            "risk_level": "PENDING",
            "category": category,
            "red_flags": [],
            "reasoning_summary": ["Need more information to complete assessment"],
            "recommended_actions": [],
            "what_to_monitor": [],
            "follow_up_questions": guardrail_result["followup_questions"],
            "disclaimer": "Please answer the follow-up questions for accurate triage."
        }
        result["model_used"] = "none (needs follow-up)"
        return result
    
    # =========================================================================
    # STEP 4: CALL LLM FOR TRIAGE
    # =========================================================================
    print("[Step 4] Calling LLM for triage...")
    
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Select model
        model = select_model(
            is_simple_case=False,
            needs_fallback=False,
            has_image=image_base64 is not None
        )
        result["model_used"] = model
        print(f"  Using model: {model}")
        
        # Build prompts
        system_prompt = get_triage_system_prompt()
        user_message = build_triage_message(
            species=species,
            category=category,
            structured_fields=structured_fields,
            user_description=sanitized_description,
            pet_profile=pet_profile,
            include_examples=True
        )
        
        # Call LLM
        llm_response = call_llm(
            client=client,
            model=model,
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.3,
            max_tokens=1000,
            json_mode=True
        )
        
        print("  LLM response received")
        
    except Exception as e:
        print(f"  ❌ LLM call failed: {e}")
        # Return fallback response
        result["success"] = True
        result["response"] = output_guardrails.get_fallback(str(e))
        result["model_used"] = "fallback"
        result["warnings"].append(f"LLM call failed, using fallback: {str(e)}")
        return result
    
    # =========================================================================
    # STEP 5: OUTPUT GUARDRAILS
    # =========================================================================
    print("[Step 5] Running output guardrails...")
    
    success, processed_response = output_guardrails.validate_and_process(llm_response)
    
    if not success:
        print("  ⚠️  Output validation failed, using fallback")
        result["warnings"].append("Output validation failed, using fallback response")
    
    if processed_response.get("_risk_escalated"):
        result["warnings"].append(
            f"Risk level was escalated: {processed_response.get('_escalation_reason', 'safety calibration')}"
        )
    
    result["success"] = True
    result["response"] = processed_response
    result["is_er"] = processed_response.get("risk_level") == "ER"
    
    return result


# ============================================================================
# Demo Function
# ============================================================================

def demo():
    """
    Demo function showing different triage scenarios
    """
    print("="*60)
    print("PET TRIAGE SYSTEM DEMO")
    print("="*60)
    
    # Demo Case 1: Normal low-risk case
    print("\n" + "="*60)
    print("DEMO CASE 1: Normal low-risk - Dog vomited once")
    print("="*60)
    
    result1 = run_triage(
        species="dog",
        category="Stomach Upset",
        structured_fields={
            "abdomen_distended": "No",
            "unproductive_retching": "No",
            "vomiting_frequency": "once",
            "blood_present": "No"
        },
        user_description="My dog vomited once this morning after eating grass. He seems fine now, eating and drinking normally.",
        pet_profile={
            "name": "Max",
            "age": "3 years",
            "breed": "Labrador Retriever",
            "weight": "30 kg"
        }
    )
    
    print("\nResult:")
    print(f"  Success: {result1['success']}")
    print(f"  Is ER: {result1['is_er']}")
    print(f"  Model used: {result1['model_used']}")
    if result1['response']:
        print(f"  Risk Level: {result1['response'].get('risk_level')}")
        print(f"  Next Steps: {result1['response'].get('next_steps_now', [])[:2]}...")
    
    # Demo Case 2: Emergency - Male cat urinary blockage
    print("\n" + "="*60)
    print("DEMO CASE 2: EMERGENCY - Male cat urinary blockage")
    print("="*60)
    
    result2 = run_triage(
        species="cat",
        category="Urinary & Genital",
        structured_fields={
            "sex": "male",
            "straining_no_urine": "Yes",
            "hours_since_urination": "12+",
            "crying_in_litterbox": "Yes"
        },
        user_description="My male cat has been going to the litter box every few minutes for the past 14 hours but nothing comes out. He's crying.",
        pet_profile={
            "name": "Whiskers",
            "age": "5 years",
            "breed": "Domestic Shorthair"
        }
    )
    
    print("\nResult:")
    print(f"  Success: {result2['success']}")
    print(f"  Is ER: {result2['is_er']}")
    print(f"  Model used: {result2['model_used']}")
    if result2['response']:
        print(f"  Risk Level: {result2['response'].get('risk_level')}")
        print(f"  Red Flags: {result2['response'].get('red_flags')}")
        print(f"  Next Steps: {result2['response'].get('next_steps_now')}")
    
    # Demo Case 3: Missing information
    print("\n" + "="*60)
    print("DEMO CASE 3: Missing critical fields")
    print("="*60)
    
    result3 = run_triage(
        species="cat",
        category="Breathing Issues",
        structured_fields={},  # No structured fields provided
        user_description="My cat seems to be breathing weird"
    )
    
    print("\nResult:")
    print(f"  Success: {result3['success']}")
    print(f"  Model used: {result3['model_used']}")
    if result3['response']:
        print(f"  Risk Level: {result3['response'].get('risk_level')}")
        print(f"  Follow-up Questions: {result3['response'].get('follow_up_questions')}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


# ============================================================================
# Test All Tasks
# ============================================================================

def test_all_tasks():
    """
    Run tests for all tasks
    """
    print("="*60)
    print("RUNNING ALL TASK TESTS")
    print("="*60)

    # Test Task 1
    print("\n--- Testing Task 1: LLM Setup ---")
    from tests.test_llm_setup import run_all_tests as test_llm_setup_all
    test_llm_setup_all()

    # Test Task 2
    print("\n--- Testing Task 2: Prompts ---")
    from tests.test_prompts import test_prompts, test_system_prompts
    test_prompts()
    test_system_prompts()

    # Test Task 3
    print("\n--- Testing Task 3: Input Guardrails ---")
    from tests.test_input_guardrails import test_input_guardrails
    test_input_guardrails()

    # Test Task 4
    print("\n--- Testing Task 4: Output Guardrails ---")
    from tests.test_output_guardrails import test_output_guardrails
    test_output_guardrails()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_all_tasks()
        elif sys.argv[1] == "demo":
            demo()
        else:
            print("Usage: python main.py [test|demo]")
    else:
        # Default: run demo
        demo()
