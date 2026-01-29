# Pet Triage AI System

An AI-powered symptom triage tool for dogs and cats using OpenAI GPT models. Designed for mobile app integration with safety-first approach. Educational project for ISBA2421 course.

## Project Structure

```
pet_triage/
├── config.py              # Constants and configuration
├── llm_setup.py           # OpenAI client, ER rules, model selection
├── prompts.py             # System prompts and message builders
├── input_guardrails.py    # 5-layer input validation
├── output_guardrails.py   # 6-layer output validation
├── main.py                # Main application entry point
├── tests/
│   ├── test_llm_setup.py
│   ├── test_prompts.py
│   ├── test_input_guardrails.py
│   └── test_output_guardrails.py
├── .env                   # API key (not committed)
└── requirements.txt
```

## Architecture

### Triage Flow

```
User Input → Input Guardrails (5 layers, includes ER Check at Layer C)
    ↓ (if ER triggered → return ER template, skip LLM)
    ↓ (if not emergency)
Model Selection → Prompt Construction → LLM Call → Output Guardrails (6 layers) → Response
```

### Model Configuration

| Stage    | Model         | Purpose                              |
|----------|---------------|--------------------------------------|
| Intake   | gpt-4o-mini   | Low-cost initial classification      |
| Triage   | gpt-4.1-mini  | Main triage engine                   |
| Fallback | gpt-4.1       | Complex/uncertain cases              |

### Module Responsibilities

- **main.py**: Orchestrates the complete workflow via `run_triage()` function
- **llm_setup.py**: OpenAI client setup, ER hard-routing rules, model selection
- **prompts.py**: System prompts, few-shot examples, message builders for intake/triage/fallback stages
- **input_guardrails.py**: 5-layer input validation
- **output_guardrails.py**: 6-layer output validation
- **config.py**: Constants for species, categories, risk levels, model config, limits
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

### 2. Set Up API Key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run Demo (3 test cases)

```bash
python main.py demo
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
    pet_profile={
        "name": "Whiskers",
        "age": "5 years"
    }
)

print(f"Risk Level: {result['response']['risk_level']}")
print(f"Next Steps: {result['response']['next_steps_now']}")
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

## License

This project is for educational purposes as part of ISBA2421 course.
