"""
Pet Health AI - Agent Implementation
==============================

This module implements the autonomous agent using LangChain.
It orchestrates tool usage based on user input and context.

Key Features:
- Autonomous tool selection based on reasoning
- Multi-step execution (e.g., triage -> search -> recommendation)
- Context-aware processing (symptom categories, pet profiles)

Usage:
    from agent import PetHealthAgent
    
    agent = PetHealthAgent()
    result = agent.chat("My dog is vomiting", context={"pet_info": ...})
    print(result["output"])
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage

# Import existing tools (NO modifications to original files!)
from rag_chain import ask_simple, ask_with_image, get_chain
from tools import (
    check_red_flags,
    find_nearby_vets,
    triage_and_recommend,
    web_search
)
from image_analyzer import analyze_pet_image
from config import load_config

# Load configuration
config = load_config()


# ============================================================
# Agent System Prompt
# ============================================================

AGENT_SYSTEM_PROMPT = """You are a Pet Health AI Assistant with access to specialized tools.

## Role
You help pet owners understand their pet's health concerns by:
1. Analyzing symptoms and questions
2. Searching medical knowledge databases
3. Detecting emergencies
4. Finding veterinary care when needed
5. Providing evidence-based guidance

## Symptom Category Information
Users may select a symptom category from the interface before describing their concern.
When a category is provided, use it to focus your analysis:
- Toxic Ingestion & Poisoning: Ate toxic substances, poisoning symptoms, toxic plants
- Stomach Upset: Vomiting, diarrhea, appetite changes, abdominal issues
- Itching & Skin Issues: Rashes, itching, hair loss, wounds, lumps, skin abnormalities
- Injury & Bleeding: Physical injuries, cuts, wounds, bleeding, trauma
- Concerning Behaviour Changes: Lethargy, aggression, anxiety, sleep changes, unusual behavior
- Ears, Eyes, and Mouth: Eye discharge, ear infections, dental issues, vision/hearing problems
- Breathing Issues: Coughing, breathing difficulty, respiratory distress, nasal discharge
- Urinary & Genital: Urination changes, accidents, straining, genital issues
- Something Else: General health questions or symptoms not covered above

Use the category to prioritize relevant search terms and tailor your response.


## Available Tools

### Knowledge & Search
- vector_search: Search the pet health knowledge database (18,909 records)
  - Use for: medical questions, conditions, treatments, breed info
  - This is your PRIMARY knowledge source

- web_search: Search the web for latest information
  - Use ONLY when: Need recent research, new treatments, current news
  - Always prefer vector_search first

### Emergency & Safety
- check_red_flags: Check symptoms for emergency indicators (rule-based)
  - Use for: ANY symptom description
  - ALWAYS use this FIRST when symptoms are mentioned
  - Returns severity: CRITICAL/URGENT/MODERATE/NORMAL

- find_nearby_vets: Find veterinary clinics near user location
  - Use when: CRITICAL/URGENT severity, or user asks for vet recommendations
  - Requires: latitude and longitude

- emergency_triage: Combined check + vet finder
  - Use when: User provides symptoms AND location
  - More efficient than calling tools separately

### Pet Information
- Pet Context: Pet profile (breed, age, conditions) is provided in the context directly.

### Image Analysis
- analyze_image: Analyze pet photos with GPT-4 Vision
  - Use when: User provides an image path or URL
  - Input: path or URL to the image
  - Returns: visual observations, severity assessment, recommendations
  - ALWAYS use this when an image is provided

## Decision Making Strategy

### Step 1: Assess the Situation
- Is there an IMAGE? -> Use analyze_image FIRST
- Are there SYMPTOMS? -> Use check_red_flags FIRST
- Is there a SYMPTOM CATEGORY? -> Use it to refine your searches
- Is it a MEDICAL QUESTION? -> Use vector_search
- Need LATEST INFO? -> Use web_search (after vector_search)

### Step 2: Check Severity
- If CRITICAL -> find_nearby_vets immediately
- If URGENT -> recommend vet visit + provide info
- If MODERATE/NORMAL -> provide information and guidance

### Step 3: Provide Complete Answer
- Combine information from multiple tools if needed
- Reference the symptom category if provided
- Always cite sources
- Be clear about when to see a vet

## Important Rules

1. Safety First: ALWAYS check_red_flags for symptoms before giving advice
2. Use Images: ALWAYS analyze_image when image is provided
3. Prefer Database: Use vector_search before web_search
4. Leverage Category: Use symptom category to focus analysis
5. Be Direct: For emergencies, immediately find vets
6. Cite Sources: Mention which tool provided information
7. Know Limits: You're not a veterinarian - recommend professional care when appropriate

## Response Style
- Acknowledge the symptom category if provided
- Empathetic and clear
- Evidence-based
- Action-oriented for emergencies
- Educational for general questions

Remember: You can use multiple tools in sequence. Think step-by-step and choose the best tools for each situation.
"""


# ============================================================
# Tool Wrapper Functions
# ============================================================
# These wrap existing functions into LangChain Tool format

def _vector_search_wrapper(query: str) -> str:
    """Search the pet health knowledge database."""
    try:
        answer = ask_simple(query)
        return f"Knowledge Database Result:\n{answer}"
    except Exception as e:
        return f"Error searching database: {str(e)}"


def _check_red_flags_wrapper(symptoms: str) -> str:
    """Check symptoms for emergency red flags."""
    try:
        result = check_red_flags(symptoms)
        severity = result.get("severity", "UNKNOWN")
        flags = result.get("red_flags", [])
        recommendation = result.get("recommendation", "")
        
        output = f"SEVERITY: {severity}\n"
        if flags:
            output += f"\nRed Flags Detected:\n"
            for flag in flags:
                output += f"- {flag}\n"
        output += f"\nRecommendation: {recommendation}"
        
        return output
    except Exception as e:
        return f"Error checking symptoms: {str(e)}"


def _find_vets_wrapper(location_query: str) -> str:
    """
    Find nearby veterinary clinics.
    Input format: "latitude,longitude" or "latitude,longitude,emergency"
    Example: "37.7749,-122.4194" or "37.7749,-122.4194,emergency"
    """
    try:
        parts = location_query.split(",")
        if len(parts) < 2:
            return "Error: Please provide location as 'latitude,longitude'"
        
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        emergency = "emergency" in location_query.lower()
        
        results = find_nearby_vets(
            latitude=lat,
            longitude=lon,
            emergency_only=emergency,
            max_results=5
        )
        
        if not results.get("vets"):
            return "No veterinary clinics found nearby."
        
        output = f"Found {len(results['vets'])} veterinary clinics:\n\n"
        for i, vet in enumerate(results["vets"], 1):
            output += f"{i}. {vet['name']}\n"
            output += f"   Address: {vet.get('address', 'N/A')}\n"
            output += f"   Distance: {vet.get('distance_km', 'N/A')} km\n"
            if vet.get('phone'):
                output += f"   Phone: {vet['phone']}\n"
            output += "\n"
        
        return output
    except Exception as e:
        return f"Error finding vets: {str(e)}"


def _web_search_wrapper(query: str) -> str:
    """Search the web for latest pet health information."""
    try:
        result = web_search(query)
        return f"Web Search Results:\n{result.get('answer', 'No results found.')}"
    except Exception as e:
        return f"Error in web search: {str(e)}"





def _emergency_triage_wrapper(input_str: str) -> str:
    """
    Combined emergency triage and vet finding.
    Input format: "symptoms | latitude,longitude"
    Example: "vomiting and lethargy | 37.7749,-122.4194"
    """
    try:
        if "|" not in input_str:
            return "Error: Please provide input as 'symptoms | latitude,longitude'"
        
        symptoms, location = input_str.split("|", 1)
        symptoms = symptoms.strip()
        lat, lon = location.strip().split(",")
        lat, lon = float(lat), float(lon)
        
        result = triage_and_recommend(
            symptoms=symptoms,
            user_latitude=lat,
            user_longitude=lon
        )
        
        output = f"TRIAGE RESULT\n"
        output += f"Severity: {result['severity']}\n\n"
        
        if result.get('red_flags'):
            output += "Red Flags:\n"
            for flag in result['red_flags']:
                output += f"- {flag}\n"
            output += "\n"
        
        output += f"Recommendation: {result['recommendation']}\n\n"
        
        if result.get('nearby_vets'):
            output += "NEARBY VETERINARY CLINICS:\n"
            for i, vet in enumerate(result['nearby_vets'], 1):
                output += f"{i}. {vet['name']} - {vet.get('distance_km', 'N/A')} km\n"
        
        return output
    except Exception as e:
        return f"Error in triage: {str(e)}"


def _analyze_image_wrapper(image_path: str) -> str:
    """
    Analyze a pet image using GPT-4 Vision.
    Input: path or URL to the pet image
    """
    try:
        result = analyze_pet_image(image_path)
        
        output = f"IMAGE ANALYSIS RESULTS\n\n"
        output += f"Visual Observations:\n{result.get('description', 'N/A')}\n\n"
        
        if result.get('severity'):
            output += f"Assessed Severity: {result['severity']}\n\n"
        
        if result.get('recommendations'):
            output += f"Recommendations:\n"
            for rec in result['recommendations']:
                output += f"- {rec}\n"
        
        if result.get('concerns'):
            output += f"\nConcerns Identified:\n"
            for concern in result['concerns']:
                output += f"- {concern}\n"
        
        return output
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


# ============================================================
# Create LangChain Tools
# ============================================================

TOOLS = [
    Tool(
        name="vector_search",
        func=_vector_search_wrapper,
        description=(
            "Search the pet health knowledge database with 18,909 curated records. "
            "Use this for medical questions, conditions, treatments, breed information. "
            "Input: a clear question or search query about pet health. "
            "This should be your PRIMARY source for pet health information."
        )
    ),
    Tool(
        name="check_red_flags",
        func=_check_red_flags_wrapper,
        description=(
            "Check symptoms for emergency red flags using rule-based detection. "
            "ALWAYS use this FIRST when user describes any symptoms. "
            "Input: description of pet's symptoms. "
            "Output: severity level (CRITICAL/URGENT/MODERATE/NORMAL) and recommendations."
        )
    ),
    Tool(
        name="find_nearby_vets",
        func=_find_vets_wrapper,
        description=(
            "Find veterinary clinics near a location. "
            "Use when severity is CRITICAL/URGENT or user asks for vet recommendations. "
            "Input: 'latitude,longitude' or 'latitude,longitude,emergency' for emergency-only clinics. "
            "Example: '37.7749,-122.4194' or '37.7749,-122.4194,emergency'"
        )
    ),
    Tool(
        name="emergency_triage",
        func=_emergency_triage_wrapper,
        description=(
            "Combined emergency check and vet finder - more efficient than calling separately. "
            "Use when user provides both symptoms AND location. "
            "Input: 'symptoms | latitude,longitude' "
            "Example: 'vomiting and lethargy | 37.7749,-122.4194'"
        )
    ),

    Tool(
        name="web_search",
        func=_web_search_wrapper,
        description=(
            "Search the web for latest pet health information using Gemini + Google Search. "
            "Use ONLY when you need recent research, new treatments, or current news. "
            "ALWAYS try vector_search first before using web search. "
            "Input: a specific search query about recent pet health topics."
        )
    ),
    Tool(
        name="analyze_image",
        func=_analyze_image_wrapper,
        description=(
            "Analyze a pet photo using GPT-4 Vision to identify visible symptoms and concerns. "
            "ALWAYS use this when user provides an image. "
            "Input: file path or URL to the pet image. "
            "Output: visual observations, severity assessment, and recommendations. "
            "Useful for: skin conditions, wounds, physical abnormalities, posture issues."
        )
    ),
]


# ============================================================
# Agent Class
# ============================================================

class PetHealthAgent:
    """
    Autonomous AI Agent for Pet Health assistance.
    
    Unlike the regular RAG chain, this agent can:
    - Decide which tools to use based on context
    - Chain multiple tools together
    - Adapt strategy based on intermediate results
    
    Example:
        agent = PetHealthAgent()
        result = agent.chat("My dog is vomiting, should I be worried?")
        print(result["output"])
    """
    
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        """
        Initialize the Pet Health Agent.
        
        Args:
            model: OpenAI model to use
            temperature: LLM temperature (0-1)
            max_iterations: Maximum tool calling iterations
            verbose: Print agent reasoning steps
        """
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=config.get("openai_api_key")
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=TOOLS,
            prompt=self.prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=TOOLS,
            verbose=verbose,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        # Memory for conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def chat(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chat with the agent.
        
        Args:
            user_input: User's question or message
            context: Optional context (pet_info, location, etc.)
        
        Returns:
            Dictionary with:
                - output: Agent's response
                - intermediate_steps: List of tool calls made
                - chat_history: Conversation history
        """
        # Add context to input if provided
        full_input = user_input
        if context:
            context_str = "\n\nContext:\n"
            if "symptom_category" in context:
                context_str += f"Symptom Category: {context['symptom_category']}\n"
            if "pet_info" in context:
                context_str += f"Pet: {context['pet_info']}\n"
            if "location" in context:
                context_str += f"Location: {context['location']}\n"
            if "image_path" in context:
                context_str += f"Image: {context['image_path']}\n"
            full_input = user_input + context_str
        
        # Run agent
        result = self.agent_executor.invoke({
            "input": full_input,
            "chat_history": self.memory.chat_memory.messages
        })
        
        # Update memory
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(result["output"])
        
        return {
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "chat_history": self.memory.chat_memory.messages
        }
    
    def reset_memory(self):
        """Clear conversation history."""
        self.memory.clear()
    
    def get_tool_usage_summary(self, result: Dict[str, Any]) -> str:
        """
        Get a summary of which tools were used.
        
        Args:
            result: Result from chat() method
        
        Returns:
            Human-readable summary of tool usage
        """
        steps = result.get("intermediate_steps", [])
        if not steps:
            return "No tools were used."
        
        summary = "Tools used:\n"
        for i, (action, observation) in enumerate(steps, 1):
            tool_name = action.tool
            tool_input = action.tool_input
            summary += f"{i}. {tool_name}({tool_input})\n"
        
        return summary


# ============================================================
# Convenience Functions
# ============================================================

def quick_ask(question: str, verbose: bool = False) -> str:
    """
    Quick one-off question (no conversation memory).
    
    Args:
        question: User's question
        verbose: Print agent reasoning
    
    Returns:
        Agent's answer
    """
    agent = PetHealthAgent(verbose=verbose)
    result = agent.chat(question)
    return result["output"]


def emergency_check(symptoms: str, location: tuple = None, verbose: bool = False) -> str:
    """
    Quick emergency check with optional vet finding.
    
    Args:
        symptoms: Description of symptoms
        location: (latitude, longitude) tuple
        verbose: Print agent reasoning
    
    Returns:
        Emergency assessment and recommendations
    """
    agent = PetHealthAgent(verbose=verbose)
    
    question = f"Emergency check: {symptoms}"
    context = {}
    if location:
        context["location"] = f"Latitude: {location[0]}, Longitude: {location[1]}"
    
    result = agent.chat(question, context=context)
    return result["output"]


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Pet Health AI - Agent Version")
    print("=" * 60)
    print()
    
    # Examples for local testing
    
    # Example 1: Simple medical question
    print("Example 1: Simple Question")
    print("-" * 60)
    result = quick_ask(
        "What are the signs of diabetes in dogs?",
        verbose=True
    )
    print(f"\nAnswer: {result}")
    print()
    
    # Example 2: Emergency scenario with symptom category
    print("\n" + "=" * 60)
    print("Example 2: Emergency with Symptom Category")
    print("-" * 60)
    agent = PetHealthAgent(verbose=True)
    
    # User selects "Stomach Upset" category and describes symptoms
    result = agent.chat(
        "My dog has been vomiting for 3 hours and won't drink water",
        context={"symptom_category": "Stomach Upset"}
    )
    print(f"\nAgent: {result['output']}")
    print(f"\n{agent.get_tool_usage_summary(result)}")
    
    # Example 3: Image analysis placeholder
    print("\n" + "=" * 60)
    print("Example 3: Image Analysis (Placeholder)")
    print("-" * 60)
    print("Uncomment code in main block to test with actual image path.")
    
    # Example 4: Multi-turn conversation
    print("\n" + "=" * 60)
    print("Example 4: Multi-turn with Category")
    print("-" * 60)
    agent2 = PetHealthAgent(verbose=True)
    
    # Turn 1: User describes breathing symptoms
    result1 = agent2.chat(
        "My cat is coughing and seems to have trouble breathing",
        context={"symptom_category": "Breathing Issues"}
    )
    print(f"\nAgent: {result1['output'][:200]}...")
    
    # Turn 2: User provides location for vet finder
    result2 = agent2.chat(
        "Can you find nearby vets?",
        context={"location": "37.7749,-122.4194"}
    )
    print(f"\nAgent: {result2['output'][:200]}...")

    
    print("\n" + "=" * 60)
    print("Usage Example for Frontend Integration:")
    print("-" * 60)
    print("""
    # Frontend sends:
    {
        "query": "My dog is limping",
        "symptom_category": "Musculoskeletal",  # From dropdown
        "image_path": "https://...",  # Optional
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    # Backend processes:
    agent = PetHealthAgent()
    result = agent.chat(
        query,
        context={
            "symptom_category": symptom_category,
            "image_path": image_path,
            "location": f"{lat},{lon}"
        }
    )
    """)
    
    print("\n" + "=" * 60)
    print("Agent examples completed!")
    print("=" * 60)

