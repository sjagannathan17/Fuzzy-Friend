"""
Pet Health AI - Configuration
============================

This module manages application configuration and environment variables.
It centralizes:
- API Keys (OpenAI, Pinecone, Google)
- Model configurations
- Path definitions

Usage:
    from config import OPENAI_API_KEY, LLM_MODEL
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = PROJECT_ROOT / "1. Original pet data"
PROCESSED_DIR = PROJECT_ROOT / "2. Processed pet data" / "processed"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# API Keys (from environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Pinecone Configuration
PINECONE_INDEX_NAME = "pet-health-ai"
PINECONE_DIMENSION = 1536  # text-embedding-3-small
PINECONE_METRIC = "cosine"

# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-3-small"

# Text Splitting Configuration
CHUNK_SIZE = 600  # tokens
CHUNK_OVERLAP = 100  # tokens

# Body System Mapping
CONDITION_TO_BODY_SYSTEM = {
    # Clinical notes conditions
    "Digestive Issues": "gi",
    "Mobility Problems": "mobility",
    "Parasites": "general",
    "Respiratory Issues": "respiratory",
    "Skin Conditions": "skin",
    "Eye Problems": "eye",
    "Urinary Issues": "urinary",
    "Behavioral Issues": "behavior",
    "Nutritional Issues": "nutrition",
    
    # Pain database
    "acute": "mobility",
    "chronic": "mobility",
    "post-operative": "mobility",
    
    # Default
    "general": "general",
}

# Credibility levels
CREDIBILITY_OFFICIAL = "official"        # FDA, OFA data
CREDIBILITY_PROFESSIONAL = "professional"  # Clinical notes, vet data
CREDIBILITY_COMMUNITY = "community"        # User reports

# Data source configurations
DATA_SOURCES = {
    "breed_health": {
        "files": [
            RAW_DATA_DIR / "ofa_data" / "breed_health_risks.csv",
            RAW_DATA_DIR / "ofa_data" / "breed_health_risks.json",
        ],
        "doc_type": "breed_health",
        "credibility": CREDIBILITY_OFFICIAL,
    },
    "clinical_notes": {
        "files": [RAW_DATA_DIR / "train-00000-of-00001.parquet"],
        "doc_type": "clinical_notes",
        "credibility": CREDIBILITY_PROFESSIONAL,
    },
    "pain_database": {
        "files": [RAW_DATA_DIR / "Dog pain database.xlsx"],
        "doc_type": "pain_assessment",
        "credibility": CREDIBILITY_PROFESSIONAL,
    },
    "adverse_events": {
        "files": [
            RAW_DATA_DIR / "openfda_data" / "cat_adverse_events_sample.json",
            RAW_DATA_DIR / "openfda_data" / "dog_adverse_events_sample.json",
        ],
        "doc_type": "adverse_event",
        "credibility": CREDIBILITY_OFFICIAL,
    },
    "genotype": {
        "files": [RAW_DATA_DIR / "Full_genotype_dataset.xlsx"],
        "doc_type": "genetic_risk",
        "credibility": CREDIBILITY_PROFESSIONAL,
    },
    "bloat_risk": {
        "files": [RAW_DATA_DIR / "ofa_data" / "bloat_risk_breeds.json"],
        "doc_type": "breed_health",
        "credibility": CREDIBILITY_OFFICIAL,
    },
    "brachycephalic": {
        "files": [RAW_DATA_DIR / "ofa_data" / "brachycephalic_breeds.json"],
        "doc_type": "breed_health", 
        "credibility": CREDIBILITY_OFFICIAL,
    },
}
