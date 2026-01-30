# Pet Triage AI System

An AI-powered symptom triage tool for dogs and cats using OpenAI GPT models and LangChain Agents. Designed for mobile app integration with safety-first approach.

## Project Structure

```
pet_triage/
├── main.py                # Main application (supports Pipeline & Agent modes)
├── config.py              # Constants and configuration
├── llm_setup.py           # OpenAI client, ER rules, model selection
├── prompts.py             # System prompts and message builders
├── input_guardrails.py    # 5-layer input validation
├── output_guardrails.py   # 6-layer output validation
├── RAG/                   # RAG & Agent module
│   ├── agent.py           # LangChain Agent (PetTriageAgent)
│   ├── tools.py           # Agent tools (check_red_flags, vector_search, etc.)
│   ├── rag_chain.py       # RAG chain for knowledge base queries
│   ├── image_analyzer.py  # GPT-4V image analysis
│   └── config.py          # RAG-specific configuration
├── shared/                # Shared constants and utilities
│   ├── constants.py       # Single source of truth for constants
│   ├── red_flags.py       # Emergency detection rules
│   └── schemas.py         # Response schemas
├── tests/
│   ├── test_llm_setup.py
│   ├── test_prompts.py
│   ├── test_input_guardrails.py
│   └── test_output_guardrails.py
├── .env                   # API keys (not committed)
└── requirements.txt
```

## Architecture

This system supports **TWO modes** of operation:

### Mode 1: Pipeline Mode (Original LLM-based)

```
User Input → Input Guardrails (5 layers)
    ↓ (if ER triggered → return ER template, skip LLM)
    ↓ (if not emergency)
Model Selection → Prompt Construction → Single LLM Call → Output Guardrails → Response
```

### Mode 2: Agent Mode (New - Autonomous Tool Selection)

```
User Input
    ↓
┌─────────────────────────────────────────┐
│  INPUT GUARDRAILS (mandatory)           │
│  - Safety checks, input sanitization    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  AGENT LOOP (autonomous decisions)      │
│  LLM autonomously selects tools:        │
│  ├─ check_red_flags: Emergency detect   │
│  ├─ vector_search: RAG knowledge base   │
│  ├─ analyze_image: GPT-4V image analysis│
│  ├─ find_nearby_vets: Vet finder        │
│  ├─ get_er_template: ER response        │
│  └─ generate_triage_response: Output    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  OUTPUT GUARDRAILS (mandatory)          │
│  - Schema validation, risk calibration  │
└─────────────────────────────────────────┘
    ↓
Final Response (TriageResponse)
```

### Agent Tools

| Tool | Type | Description |
|------|------|-------------|
| `check_red_flags` | Rule-based | Check for emergency red flags |
| `vector_search` | RAG | Search 18,909 pet health records |
| `analyze_image` | Vision | Analyze pet photos with GPT-4V |
| `find_nearby_vets` | API | Find nearby vet clinics (OpenStreetMap) |
| `get_er_template` | Template | Get pre-built ER response |
| `generate_triage_response` | Generator | Format final triage output |
| `request_followup` | Generator | Generate follow-up questions |

### Model Configuration

| Stage    | Model              | Purpose                              |
|----------|--------------------|--------------------------------------|
| Agent    | gpt-4-turbo-preview| Autonomous tool selection & reasoning|
| Triage   | gpt-4.1-mini       | Main triage engine (Pipeline mode)  |
| Fallback | gpt-4.1            | Complex/uncertain cases             |

### Module Responsibilities

- **main.py**: Orchestrates workflows via `run_triage()` (Pipeline) and `run_triage_agent()` (Agent)
- **RAG/agent.py**: `PetHealthAgent` and `PetTriageAgent` classes using LangGraph
- **RAG/tools.py**: All agent tools with emergency detection, RAG search, vet finder
- **llm_setup.py**: OpenAI client setup, ER templates, model selection
- **prompts.py**: System prompts, few-shot examples, message builders
- **input_guardrails.py**: 5-layer input validation
- **output_guardrails.py**: 6-layer output validation
- **shared/**: Single source of truth for constants, red flags, schemas
- **tests/**: Unit tests for all modules

## Features

### Input Guardrails (5 Layers)

| Layer | Name                    | Purpose                                    |
|-------|-------------------------|--------------------------------------------|
| A     | Scope Guardrails        | MVP boundaries (dogs/cats only)            |
| B     | Field Completeness      | Check required structured fields           |
| C     | ER Pre-check            | Hard-route emergencies (skip LLM)          |
| D     | Input Quality           | Sanitization, length limits                |
| E     | Safety Detection        | Prompt injection & unsafe request detection|

### Output Guardrails (6 Layers)

| Layer | Name                    | Purpose                                    |
|-------|-------------------------|--------------------------------------------|
| A     | JSON Schema Validation  | Ensure valid JSON structure                |
| B     | Content Safety          | No diagnosis, no medication dosing         |
| C     | Risk Calibration        | Prevent under-triage, escalate if needed   |
| D     | Mandatory Disclaimer    | Always include medical disclaimer          |
| E     | UI Constraints          | List limits, character limits              |
| F     | Safe Fallback           | Never break the app                        |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-openai-key
PINECONE_API_KEY=your-pinecone-key  # For RAG vector search
```

### 3. Run Demos

```bash
# Run both Pipeline and Agent demos
python main.py demo

# Run Pipeline mode demo only
python main.py demo-pipeline

# Run Agent mode demo only
python main.py demo-agent

# Quick Agent test
python main.py agent
```

### 4. Run All Unit Tests

```bash
python main.py test
```

### 5. Run Individual Task Tests

```bash
python tests/test_llm_setup.py
python tests/test_prompts.py
python tests/test_input_guardrails.py
python tests/test_output_guardrails.py
```

## Supported Symptom Categories

1. Toxic Ingestion & Poisoning
2. Stomach Upset
3. Itching & Skin Issues
4. Injury & Bleeding
5. Concerning Behaviour Changes
6. Ears, Eyes, and Mouth
7. Breathing Issues
8. Urinary & Genital
9. Something Else

## Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **ER** | Emergency | Go to emergency vet NOW |
| **TODAY** | Urgent | Vet visit today |
| **SOON** | Non-urgent | Vet visit within 24-48 hours |
| **MONITOR** | Low-risk | Safe to monitor at home |

## Emergency Hard-Routing

The following conditions trigger immediate ER response WITHOUT calling the LLM (zero API cost):

- Cat open-mouth breathing
- Blue/purple gums
- Male cat urinary straining (12+ hours without urination)
- Seizure > 5 minutes or 3+ in 24 hours
- Bloat symptoms (distended abdomen + unproductive retching)
- Heavy uncontrolled bleeding
- Eye proptosis (eye popped out)

## Usage Example

### Pipeline Mode (Original)

```python
from main import run_triage

result = run_triage(
    species="cat",
    category="Urinary & Genital",
    structured_fields={
        "sex": "male",
        "straining_no_urine": "Yes",
        "hours_since_urination": "12+"
    },
    user_description="My cat keeps going to the litter box but can't pee",
    pet_profile={"name": "Whiskers", "age": "5 years"}
)

print(f"Risk Level: {result['response']['risk_level']}")
print(f"Model Used: {result['model_used']}")
```

### Agent Mode (New - Autonomous Tool Selection)

```python
from main import run_triage_agent

result = run_triage_agent(
    species="dog",
    category="Stomach Upset",
    structured_fields={
        "abdomen_distended": "Yes",
        "unproductive_retching": "Yes"
    },
    user_description="My Great Dane has a swollen belly and keeps trying to vomit",
    pet_profile={"name": "Duke", "breed": "Great Dane"},
    verbose=True  # Print agent reasoning
)

print(f"Risk Level: {result['response']['risk_level']}")
print(f"Mode: {result['mode']}")  # 'agent'
print(f"Tools Used: {[t['tool'] for t in result['tools_used']]}")
# Example: ['check_red_flags', 'get_er_template']
```

## Output JSON Schema

All responses follow this structure:

```json
{
  "risk_level": "ER | TODAY | SOON | MONITOR",
  "category": "one of 9 categories",
  "red_flags": ["list of detected red flags"],
  "reasoning_summary": ["1-3 short reasons"],
  "recommended_actions": ["3-6 short actions"],
  "what_to_monitor": ["2-5 monitoring signals"],
  "follow_up_questions": ["0-2 questions if needed"],
  "disclaimer": "safety disclaimer"
}
```

## Safety Principles

1. **No Diagnosis**: Only triage guidance, never definitive diagnosis
2. **No Medication Dosing**: Never provide drug dosages
3. **Conservative Escalation**: When uncertain, escalate to higher urgency (under-triage is dangerous)
4. **Always Disclaimer**: Every response includes medical disclaimer

