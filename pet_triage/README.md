# Pet Triage AI System

An AI-powered symptom triage tool for dogs and cats using OpenAI GPT models and LangChain Agents. Designed for mobile app integration with safety-first approach.

## Project Structure

```
pet_triage/
├── api.py                  # FastAPI entry point
├── auth.py                 # JWT authentication
├── database.py             # SQLite database operations
├── main.py                 # Main triage orchestration
├── llm_setup.py            # OpenAI client, ER rules, model selection
├── input_guardrails.py     # 5-layer input validation
├── output_guardrails.py    # 6-layer output validation
├── core/                   # AI Agent module
│   ├── agent.py            # LangChain Agent (PetTriageAgent)
│   ├── tools.py            # Agent tools (check_red_flags, etc.)
│   ├── rag_chain.py        # RAG chain for knowledge base
│   └── image_analyzer.py   # GPT-4V image analysis
├── shared/                 # Shared constants and utilities
│   ├── constants.py        # Single source of truth for constants
│   ├── prompts.py          # System prompts and templates
│   ├── schemas.py          # Response schemas
│   ├── red_flags.py        # Emergency detection rules
│   └── errors.py           # Error handling
└── tests/                  # Unit tests
```

## Architecture

```
User Input
    |
[INPUT GUARDRAILS - mandatory]
  - Safety checks, input sanitization
    |
[AGENT LOOP - autonomous decisions]
  LLM autonomously selects tools:
  ├─ check_red_flags: Emergency detect
  ├─ vector_search: RAG knowledge base
  ├─ analyze_image: GPT-4V image analysis
  ├─ find_nearby_vets: Vet finder
  ├─ get_er_template: ER response
  └─ generate_triage_response: Output
    |
[OUTPUT GUARDRAILS - mandatory]
  - Schema validation, risk calibration
    |
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

### Model Configuration

| Stage    | Model              | Purpose                              |
|----------|--------------------|--------------------------------------|
| Agent    | gpt-4-turbo-preview| Autonomous tool selection            |
| Fallback | gpt-4.1            | Complex/uncertain cases              |

## Input Guardrails (5 Layers)

| Layer | Name                    | Purpose                                    |
|-------|-------------------------|-------------------------------------------|
| A     | Scope Guardrails        | MVP boundaries (dogs/cats only)           |
| B     | Field Completeness      | Check required structured fields          |
| C     | ER Pre-check            | Hard-route emergencies (skip LLM)         |
| D     | Input Quality           | Sanitization, length limits               |
| E     | Safety Detection        | Prompt injection detection                |

## Output Guardrails (6 Layers)

| Layer | Name                    | Purpose                                    |
|-------|-------------------------|-------------------------------------------|
| A     | JSON Schema Validation  | Ensure valid JSON structure               |
| B     | Content Safety          | No diagnosis, no medication dosing        |
| C     | Risk Calibration        | Prevent under-triage                      |
| D     | Mandatory Disclaimer    | Always include medical disclaimer         |
| E     | UI Constraints          | List limits, character limits             |
| F     | Safe Fallback           | Never break the app                       |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-openai-key
PINECONE_API_KEY=your-pinecone-key
```

### 3. Run the API Server

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### 4. Run Tests

```bash
python tests/run_all_tests.py
```

## Supported Symptom Categories

1. Toxic Ingestion and Poisoning
2. Stomach Upset
3. Itching and Skin Issues
4. Injury and Bleeding
5. Concerning Behaviour Changes
6. Ears, Eyes, and Mouth
7. Breathing Issues
8. Urinary and Genital
9. Something Else
10. General Question

## Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **ER** | Emergency | Go to emergency vet NOW |
| **TODAY** | Urgent | Vet visit today |
| **SOON** | Non-urgent | Vet visit within 24-48 hours |
| **MONITOR** | Low-risk | Safe to monitor at home |

## Emergency Hard-Routing

The following conditions trigger immediate ER response WITHOUT calling the LLM:

- Cat open-mouth breathing
- Blue/purple gums
- Male cat urinary straining (12+ hours)
- Seizure > 5 minutes or 3+ in 24 hours
- Bloat symptoms (distended abdomen + unproductive retching)
- Heavy uncontrolled bleeding
- Eye proptosis (eye popped out)

## Output JSON Schema

```json
{
  "risk_level": "ER | TODAY | SOON | MONITOR",
  "category": "one of 10 categories",
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
3. **Conservative Escalation**: When uncertain, escalate to higher urgency
4. **Always Disclaimer**: Every response includes medical disclaimer
