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
from input_guardrails import ERPreCheckGuardrails


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


def main():
    print("=" * 60)
    print("Pet Triage AI - Interactive Mode")
    print("=" * 60)
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

            # Check for emergency keywords first
            is_er, er_response = check_for_emergency(user_input)

            if is_er and er_response:
                print("\n[EMERGENCY DETECTED]")
                print(f"Risk Level: {er_response.get('risk_level', 'ER')}")
                print(f"Category: {er_response.get('category', 'Unknown')}")
                print("\nRecommended Actions:")
                for action in er_response.get('recommended_actions', []):
                    print(f"  - {action}")
                print(f"\nDisclaimer: {er_response.get('disclaimer', '')}")
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
