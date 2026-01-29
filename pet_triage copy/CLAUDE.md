# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pet Triage AI System - an AI-powered symptom triage tool for dogs and cats using OpenAI GPT models. Designed for mobile app integration with safety-first approach. Educational project for ISBA2421 course.

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

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo (3 test cases)
python main.py demo

# Run all unit tests
python main.py test

# Run individual task tests
python tests/test_llm_setup.py
python tests/test_prompts.py
python tests/test_input_guardrails.py
python tests/test_output_guardrails.py
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

### Emergency Hard-Routing

Certain conditions return immediate ER response WITHOUT LLM call (zero API cost):
- Cat open-mouth breathing
- Blue/purple gums
- Male cat urinary straining (12+ hours)
- Seizure >5 minutes or 3+ in 24 hours
- Bloat symptoms (distended abdomen + unproductive retching)
- Heavy uncontrolled bleeding
- Eye proptosis

### Risk Levels

- **ER**: Go to emergency vet NOW
- **TODAY**: Vet visit today
- **SOON**: Vet visit within 24-48 hours
- **MONITOR**: Safe to monitor at home

## Safety Principles

1. **No Diagnosis**: Only triage guidance, never definitive diagnosis
2. **No Medication Dosing**: Never provide drug dosages
3. **Conservative Escalation**: When uncertain, escalate to higher urgency (under-triage is dangerous)
4. **Always Disclaimer**: Every response includes medical disclaimer

## Environment Setup

Create `.env` file with:
```
OPENAI_API_KEY=sk-your-api-key-here
```
