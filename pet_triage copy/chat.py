#!/usr/bin/env python3
"""
Interactive Chat Mode for Pet Triage AI
Run: python chat.py
"""

import sys
import os

# Add both root and RAG directories to path
root_dir = os.path.dirname(os.path.abspath(__file__))
rag_dir = os.path.join(root_dir, 'RAG')
sys.path.insert(0, root_dir)
sys.path.insert(0, rag_dir)

from RAG.agent import PetHealthAgent
from RAG.tools import find_nearby_vets
from input_guardrails import ERPreCheckGuardrails, ScopeGuardrails, SafetyGuardrails


# List of non-supported animals to detect
NON_SUPPORTED_ANIMALS = [
    "bird", "parrot", "parakeet", "cockatiel", "canary", "finch",
    "rabbit", "bunny", "hamster", "guinea pig", "gerbil", "mouse", "rat",
    "fish", "goldfish", "betta", "tropical fish",
    "reptile", "snake", "lizard", "gecko", "turtle", "tortoise", "iguana",
    "ferret", "chinchilla", "hedgehog",
    "horse", "pony", "donkey",
    "chicken", "duck", "goose", "turkey",
    "pig", "goat", "sheep", "cow",
    "frog", "toad", "salamander", "newt",
    "spider", "tarantula", "scorpion",
    "hermit crab", "crab", "lobster",
    "monkey", "primate",
    "exotic", "wild animal"
]


def detect_species_from_text(text: str) -> tuple:
    """
    Detect species mentioned in text.
    Returns: (detected_species, is_supported)
    - detected_species: 'dog', 'cat', or the unsupported animal name
    - is_supported: True if dog/cat, False otherwise
    """
    text_lower = text.lower()
    
    # Check for supported species first
    dog_keywords = ["dog", "puppy", "pup", "canine"]
    cat_keywords = ["cat", "kitten", "kitty", "feline"]
    
    for keyword in dog_keywords:
        if keyword in text_lower:
            return "dog", True
    
    for keyword in cat_keywords:
        if keyword in text_lower:
            return "cat", True
    
    # Check for non-supported animals
    for animal in NON_SUPPORTED_ANIMALS:
        if animal in text_lower:
            return animal, False
    
    # No animal detected - could be general question
    return None, None


def check_for_emergency(text: str) -> tuple:
    """
    Check if user input contains emergency keywords.
    Returns: (is_emergency, er_response)
    """
    is_er, er_response = ERPreCheckGuardrails.run_er_precheck(
        structured_fields={},
        user_text=text
    )
    return is_er, er_response


def get_user_location() -> tuple:
    """
    Ask user for their location to find nearby vets.
    Returns: (latitude, longitude) or (None, None) if skipped
    """
    print("\n[FINDING NEARBY EMERGENCY VETS]")
    print("Enter your location to find nearby emergency veterinary clinics.")
    print("(Type 'skip' to skip this step)")
    
    location_input = input("Enter latitude,longitude (e.g., 37.7749,-122.4194): ").strip()
    
    if location_input.lower() == 'skip':
        return None, None
    
    try:
        parts = location_input.split(',')
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon
    except ValueError:
        pass
    
    print("Invalid format. Skipping vet search.")
    return None, None


def display_nearby_vets(latitude: float, longitude: float):
    """
    Find and display nearby emergency vets.
    """
    print("\nSearching for nearby emergency veterinary clinics...")
    
    try:
        result = find_nearby_vets(
            latitude=latitude,
            longitude=longitude,
            emergency_only=True,
            max_results=5
        )
        
        vets = result.get("vets", [])
        
        if vets:
            print(f"\n[NEARBY EMERGENCY VETS] Found {len(vets)} clinics:\n")
            for i, vet in enumerate(vets, 1):
                print(f"  {i}. {vet.get('name', 'Unknown')}")
                if vet.get('address'):
                    print(f"     Address: {vet['address']}")
                if vet.get('distance_km'):
                    print(f"     Distance: {vet['distance_km']} km")
                if vet.get('phone'):
                    print(f"     Phone: {vet['phone']}")
                if vet.get('opening_hours'):
                    print(f"     Hours: {vet['opening_hours']}")
                print()
        else:
            print("\nNo emergency veterinary clinics found nearby.")
            print("Please search online for '24 hour emergency vet near me'")
    except Exception as e:
        print(f"\nCould not search for nearby vets: {e}")
        print("Please search online for '24 hour emergency vet near me'")


def main():
    print("=" * 60)
    print("Pet Triage AI - Interactive Mode")
    print("=" * 60)
    print("🐕 🐈 This system only supports DOGS and CATS.")
    print("Type your question about your pet's health.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 60)
    print()

    agent = PetHealthAgent()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            # ===== INPUT GUARDRAIL: Species Check =====
            detected_species, is_supported = detect_species_from_text(user_input)
            
            if is_supported == False and detected_species:
                # User mentioned an unsupported animal
                print(f"\n❌ Sorry, we currently only support DOGS and CATS.")
                print(f"   '{detected_species}' is not supported by this system.")
                print("   Please consult a veterinarian specializing in exotic pets.")
                print()
                continue

            # Check for emergency keywords first
            is_er, er_response = check_for_emergency(user_input)

            if is_er and er_response:
                print("\n" + "=" * 60)
                print("⚠️  [EMERGENCY DETECTED] ⚠️")
                print("=" * 60)
                print(f"Risk Level: {er_response.get('risk_level', 'ER')}")
                print(f"Category: {er_response.get('category', 'Unknown')}")
                
                if er_response.get('red_flags'):
                    print("\nRed Flags:")
                    for flag in er_response.get('red_flags', []):
                        print(f"  🚨 {flag}")
                
                print("\nRecommended Actions:")
                for action in er_response.get('recommended_actions', []):
                    print(f"  ➡️  {action}")
                
                if er_response.get('what_to_monitor'):
                    print("\nWhat to Monitor:")
                    for item in er_response.get('what_to_monitor', []):
                        print(f"  👁️  {item}")
                
                print(f"\n⚕️  Disclaimer: {er_response.get('disclaimer', '')}")
                
                # Ask for location and find nearby emergency vets
                lat, lon = get_user_location()
                if lat is not None and lon is not None:
                    display_nearby_vets(lat, lon)
                
                print("=" * 60)
                print()
                continue

            print("\nAgent is thinking...\n")

            result = agent.chat(user_input)

            print(f"Agent: {result.get('output', 'No response')}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()

if __name__ == "__main__":
    main()
