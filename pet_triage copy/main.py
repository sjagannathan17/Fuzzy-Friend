# ============================================================================
# File 6: main.py - Main Application (Integrates All Tasks)
# ============================================================================
"""
Main Application: Pet Triage System

This file supports TWO modes:
1. PIPELINE MODE (original): Linear workflow with single LLM call
2. AGENT MODE (new): LangChain Agent with autonomous tool selection

Flow (Pipeline Mode):
User Input → Input Guardrails → ER Check → LLM Call → Output Guardrails → Response

Flow (Agent Mode):
User Input → Input Guardrails → Agent Loop (autonomous tool calls) → Output Guardrails → Response

NOTE: This file now imports from shared module for consistency.
"""

import json
import sys
import os
from typing import Dict, Any, Optional

# Add RAG directory to path for agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RAG'))

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
# AGENT MODE: Autonomous Triage with Tool Selection
# ============================================================================

def run_triage_agent(
    species: str,
    category: str,
    structured_fields: Dict[str, Any],
    user_description: str = "",
    pet_profile: Dict[str, Any] = None,
    image_base64: str = None,
    image_type: str = None,
    image_path: str = None,
    latitude: float = None,
    longitude: float = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Agent-based triage function with autonomous tool selection.

    This function uses a LangChain Agent that can:
    - Decide which tools to call based on the situation
    - Chain multiple tools together (e.g., check emergency → search knowledge → analyze image)
    - Adapt strategy based on intermediate results

    The workflow is wrapped by mandatory Input/Output Guardrails.

    Args:
        species: Pet species (dog/cat)
        category: Symptom category
        structured_fields: Structured fields from UI
        user_description: User's free text description
        pet_profile: Pet profile information
        image_base64: Base64 encoded image (optional)
        image_type: Image MIME type (optional)
        image_path: Path to image file (optional)
        latitude: User latitude for vet finder (optional)
        longitude: User longitude for vet finder (optional)
        verbose: Print agent reasoning steps

    Returns:
        Triage result dictionary with:
            - success: bool
            - response: TriageResponse dict
            - is_er: bool
            - model_used: str
            - tools_used: List of tools called by agent
            - warnings: List of warnings
    """
    # Import agent here to avoid circular imports
    from RAG.agent import PetTriageAgent

    result = {
        "success": False,
        "response": None,
        "error": None,
        "warnings": [],
        "is_er": False,
        "model_used": None,
        "tools_used": [],
        "mode": "agent"
    }

    # =========================================================================
    # STEP 1: INPUT GUARDRAILS (Mandatory - runs before Agent)
    # =========================================================================
    print("\n[Agent Mode - Step 1] Running input guardrails...")

    image_size = len(image_base64) if image_base64 else None

    guardrail_result = input_guardrails.validate_all(
        species=species,
        category=category,
        structured_fields=structured_fields,
        user_description=user_description,
        image_size=image_size,
        image_type=image_type
    )

    if not guardrail_result["passed"]:
        result["error"] = guardrail_result["error"]
        return result

    result["warnings"] = guardrail_result["warnings"]
    sanitized_description = guardrail_result["sanitized_text"]

    # =========================================================================
    # STEP 2: AGENT LOOP (Autonomous Decision Making)
    # =========================================================================
    print("[Agent Mode - Step 2] Starting Agent loop...")

    try:
        # Initialize the triage agent
        agent = PetTriageAgent(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            max_iterations=8,
            verbose=verbose
        )

        # Run triage through the agent
        agent_result = agent.triage(
            species=species,
            category=category,
            structured_fields=structured_fields,
            user_description=sanitized_description,
            pet_profile=pet_profile,
            image_base64=image_base64,
            image_path=image_path,
            latitude=latitude,
            longitude=longitude
        )

        result["model_used"] = agent.model
        result["tools_used"] = agent_result.get("tools_used", [])

        if not agent_result.get("success"):
            raise Exception(agent_result.get("error", "Agent execution failed"))

        # Get the triage response from agent
        agent_response = agent_result.get("triage_response", {})

        print(f"  Agent completed. Tools used: {len(result['tools_used'])}")
        for tool_info in result["tools_used"]:
            print(f"    - {tool_info['tool']}")

    except Exception as e:
        print(f"  [ERROR] Agent execution failed: {e}")
        result["success"] = True
        result["response"] = output_guardrails.get_fallback(str(e))
        result["model_used"] = "fallback"
        result["warnings"].append(f"Agent failed, using fallback: {str(e)}")
        return result

    # =========================================================================
    # STEP 3: OUTPUT GUARDRAILS (Mandatory - runs after Agent)
    # =========================================================================
    print("[Agent Mode - Step 3] Running output guardrails...")

    # Convert agent response to JSON string for guardrails
    if isinstance(agent_response, dict):
        response_str = json.dumps(agent_response, ensure_ascii=False)
    else:
        response_str = str(agent_response)

    success, processed_response = output_guardrails.validate_and_process(response_str)

    if not success:
        print("  [WARNING] Output validation failed, using fallback")
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
        print("  [EMERGENCY] Emergency detected - Returning ER template")
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
        print(f"  [ERROR] LLM call failed: {e}")
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
        print("  [WARNING] Output validation failed, using fallback")
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
# Demo Functions
# ============================================================================

def demo_pipeline():
    """
    Demo function showing PIPELINE MODE (original linear workflow)
    """
    print("="*60)
    print("PET TRIAGE SYSTEM DEMO - PIPELINE MODE")
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
        print(f"  Actions: {result1['response'].get('recommended_actions', result1['response'].get('next_steps_now', []))[:2]}...")

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

    print("\n" + "="*60)
    print("PIPELINE MODE DEMO COMPLETE")
    print("="*60)


def demo_agent():
    """
    Demo function showing AGENT MODE (autonomous tool selection)
    """
    print("="*60)
    print("PET TRIAGE SYSTEM DEMO - AGENT MODE")
    print("="*60)
    print("\nAgent Mode uses LangChain to autonomously select tools:")
    print("  - check_red_flags: Emergency detection")
    print("  - vector_search: Knowledge base search")
    print("  - analyze_image: Image analysis (GPT-4V)")
    print("  - find_nearby_vets: Vet finder")
    print("  - generate_triage_response: Format output")

    # Demo Case 1: Agent handling a moderate case
    print("\n" + "="*60)
    print("AGENT CASE 1: Dog with skin issues")
    print("="*60)

    result1 = run_triage_agent(
        species="dog",
        category="Itching & Skin Issues",
        structured_fields={
            "duration": "3 days",
            "scratching_frequency": "frequent",
            "visible_rash": "Yes"
        },
        user_description="My dog has been scratching a lot and has a red rash on his belly. It started 3 days ago after we went to the park.",
        pet_profile={
            "name": "Buddy",
            "age": "2 years",
            "breed": "Golden Retriever"
        },
        verbose=True
    )

    print("\nResult:")
    print(f"  Success: {result1['success']}")
    print(f"  Is ER: {result1['is_er']}")
    print(f"  Model used: {result1['model_used']}")
    print(f"  Mode: {result1.get('mode', 'agent')}")
    print(f"  Tools used: {[t['tool'] for t in result1.get('tools_used', [])]}")
    if result1['response']:
        print(f"  Risk Level: {result1['response'].get('risk_level')}")
        print(f"  Reasoning: {result1['response'].get('reasoning_summary', [])[:2]}")

    # Demo Case 2: Emergency via Agent
    print("\n" + "="*60)
    print("AGENT CASE 2: EMERGENCY - Bloat symptoms in large dog")
    print("="*60)

    result2 = run_triage_agent(
        species="dog",
        category="Stomach Upset",
        structured_fields={
            "abdomen_distended": "Yes",
            "unproductive_retching": "Yes",
            "restless": "Yes"
        },
        user_description="My Great Dane has a swollen belly and keeps trying to vomit but nothing comes out. He's very restless and won't lie down.",
        pet_profile={
            "name": "Duke",
            "age": "6 years",
            "breed": "Great Dane"
        },
        verbose=True
    )

    print("\nResult:")
    print(f"  Success: {result2['success']}")
    print(f"  Is ER: {result2['is_er']}")
    print(f"  Tools used: {[t['tool'] for t in result2.get('tools_used', [])]}")
    if result2['response']:
        print(f"  Risk Level: {result2['response'].get('risk_level')}")
        print(f"  Red Flags: {result2['response'].get('red_flags')}")
        print(f"  Actions: {result2['response'].get('recommended_actions', [])[:2]}")

    print("\n" + "="*60)
    print("AGENT MODE DEMO COMPLETE")
    print("="*60)


def demo():
    """
    Combined demo showing both Pipeline and Agent modes.
    """
    print("\n" + "="*70)
    print("          PET TRIAGE SYSTEM - ARCHITECTURE COMPARISON")
    print("="*70)
    print("\nThis demo shows two modes of operation:")
    print("  1. PIPELINE MODE: Fixed linear workflow (Input → LLM → Output)")
    print("  2. AGENT MODE: Autonomous tool selection via LangChain")
    print("="*70)

    # Run pipeline demo
    demo_pipeline()

    print("\n\n")

    # Run agent demo
    demo_agent()

    print("\n" + "="*70)
    print("                    ALL DEMOS COMPLETE")
    print("="*70)


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
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            test_all_tasks()
        elif command == "demo":
            demo()
        elif command == "demo-pipeline":
            demo_pipeline()
        elif command == "demo-agent":
            demo_agent()
        elif command == "agent":
            # Quick agent test
            print("Running quick agent test...")
            result = run_triage_agent(
                species="dog",
                category="Stomach Upset",
                structured_fields={"vomiting_frequency": "once"},
                user_description="My dog vomited once",
                verbose=True
            )
            print(f"\nResult: {json.dumps(result['response'], indent=2, ensure_ascii=False)}")
        else:
            print("Usage: python main.py [test|demo|demo-pipeline|demo-agent|agent]")
            print("")
            print("Commands:")
            print("  test          - Run all unit tests")
            print("  demo          - Run both pipeline and agent demos")
            print("  demo-pipeline - Run pipeline mode demo only")
            print("  demo-agent    - Run agent mode demo only")
            print("  agent         - Quick agent test with sample input")
    else:
        # Default: run full demo
        demo()
