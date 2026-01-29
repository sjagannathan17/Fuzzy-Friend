# Agentic AI Pet Health Assistant
> **Branch:** `RAG-and-VectorDB`  
> **Last Updated:** January 28, 2026  
> **Contributor:** Rachel

## Overview

This project is an **Agentic AI Pet Health Assistant** that goes beyond simple RAG-based Q&A. It is an autonomous agent capable of **Perception, Decision Making, and Action**.

It combines:
1.  **RAG Knowledge Base**: 18,909 curated records (Pinecone)
2.  **Visual Perception**: Image analysis via GPT-4 Vision
3.  **Autonomous Decision Making**: LangChain-based reasoning
4.  **Real-world Action**: Geolocation-based vet finding (OpenStreetMap)
5.  **Real-time Information**: Google Search grounding (Gemini)

---

## Architecture

The system uses a hub-and-spoke agentic architecture where `agent.py` acts as the central brain.

```mermaid
graph TD
    User[User Input] --> Agent[agent.py (Central Brain)]
    
    subgraph Perception
        Agent --> |Analysis| Image[image_analyzer.py]
        Agent --> |Triage| RedFlags[check_red_flags]
    end
    
    subgraph Knowledge
        Agent --> |Search| RAG[rag_chain.py / Pinecone]
        Agent --> |Search| Web[web_search / Gemini]
    end
    
    subgraph Action
        Agent --> |Find| Vets[find_nearby_vets / OpenStreetMap]
    end
    
    Image --> Agent
    RedFlags --> Agent
    RAG --> Agent
    Web --> Agent
    Vets --> Agent
    
    Agent --> Final[Context-Aware Response]
```

---

## Key Features

### 1. Autonomous Agent (`agent.py`)
- **Reasoning**: Decides *which* tools to use and *when*.
- **Chain of Thought**: "I see a wound in the image -> I should check infection signs -> I will search for wound care."
- **Context Aware**: Understands pet profile (breed, age) and previous conversation history.

### 2. Multi-Modal Analysis
- **Image Analysis**: Agent can "see" pet photos to assess rashes, wounds, or behavioral cues.
- **Location Awareness**: Uses user coordinates to find emergency care.

### 3. RAG Knowledge Base
- **Source**: 18,909 curated records (OpenFDA, Vet Notes, Breed Standards).
- **Engine**: Pinecone Vector DB + OpenAI Embeddings.

### 4. Safety & Ethics
- **Red Flag Detection**: Rule-based (non-LLM) system to instantly catch emergencies.
- **Symptom Categories**: 9 distinct categories to focus clinical analysis.

---

## Symptom Categories (Context Injection)

The agent supports 9 specific symptom categories injected from the frontend:

- **Toxic Ingestion & Poisoning**
- **Stomach Upset**
- **Itching & Skin Issues**
- **Injury & Bleeding**
- **Concerning Behaviour Changes**
- **Ears, Eyes, and Mouth**
- **Breathing Issues**
- **Urinary & Genital**
- **Something Else**

---

## Tech Stack & Project Structure

**Core Technologies:** `LangChain`, `OpenAI (GPT-4 Turbo)`, `Pinecone`, `Google Gemini`, `OpenStreetMap`

```text
genai_group_project/
├── agent.py                     MAIN ENTRY POINT (The Agent)
├── tools.py                     Tool definitions (Red flags, Vet finder)
├── rag_chain.py                 RAG Knowledge Base connection
├── image_analyzer.py            Visual analysis module
├── config.py                    Configuration & Keys
└── requirements.txt             Dependencies
```

---

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API Keys in .env
# OPENAI_API_KEY=sk-...
# PINECONE_API_KEY=...
# GOOGLE_API_KEY=...
```

### 2. Run the Agent (Interactive Mode)
```bash
python agent.py
```

---

## Backend Integration Guide

The Agent expects **Context Injection** from the backend. Do not query the database *inside* the agent; pass data *to* the agent.

### Python Backend Example

```python
from agent import PetHealthAgent

# 1. Initialize Agent
agent = PetHealthAgent()

# 2. Prepare Context (Fetch from your DB)
context = {
    # User Selection
    "symptom_category": "Itching & Skin Issues",
    "image_path": "/path/to/upload/rash.jpg",
    "location": "37.7749,-122.4194",
    
    # Injected Pet Profile (from DB)
    "pet_info": {
        "name": "Max",
        "breed": "Golden Retriever",
        "age": "5 years",
        "conditions": ["Hip Dysplasia"]
    }
}

# 3. Call Agent
result = agent.chat("What is this red spot on his belly?", context=context)

# 4. Return Output
print(result["output"])
```

---

## Contact
**Module Owner:** Rachel  
**Branch:** RAG-and-VectorDB  

For questions about the Agent architecture, RAG pipeline, or vector database, contact Rachel.