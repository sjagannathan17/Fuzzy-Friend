"""
Pet Triage API Server
=====================

FastAPI server that exposes the pet triage functionality as HTTP endpoints.
This enables the Next.js frontend to communicate with the Python AI backend.

Usage:
    uvicorn api:app --reload --port 8000

Endpoints:
    POST /api/triage     - Main triage assessment
    POST /api/chat       - Conversational follow-up
    GET  /api/health     - Health check
    GET  /api/categories - Get supported symptom categories
"""

import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from our modules
from main import run_triage, run_triage_agent
from shared.constants import SUPPORTED_CATEGORIES, SUPPORTED_SPECIES
from shared.schemas import TriageResponse, get_fallback_response

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title="Fuzzy Friend - Pet Triage API",
    description="AI-powered pet symptom assessment and triage guidance",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev server
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        # Add production domains here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class PetProfile(BaseModel):
    """Pet profile information."""
    name: Optional[str] = None
    species: str = Field(..., description="Pet species: 'dog' or 'cat'")
    breed: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None
    sex: Optional[str] = None
    known_conditions: Optional[List[str]] = None


class TriageRequest(BaseModel):
    """Request payload for triage assessment."""
    species: str = Field(..., description="Pet species: 'dog' or 'cat'")
    category: str = Field(..., description="Symptom category")
    structured_fields: Dict[str, Any] = Field(default_factory=dict, description="UI form fields")
    user_description: str = Field(default="", max_length=1500, description="Free text symptom description")
    pet_profile: Optional[PetProfile] = None
    
    # Optional image (base64 encoded)
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded pet image")
    image_type: Optional[str] = Field(default=None, description="Image MIME type (image/jpeg, image/png)")
    
    # Optional location for vet finder
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class ChatMessage(BaseModel):
    """Chat message for conversational follow-up."""
    message: str = Field(..., max_length=1000)
    session_id: Optional[str] = None
    pet_context: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Unified API response wrapper."""
    success: bool
    trace_id: str
    timestamp: str
    processing_time_ms: int
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    is_er: bool = False


# =============================================================================
# Health Check Endpoint
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pet-triage-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# =============================================================================
# Categories Endpoint
# =============================================================================

@app.get("/api/categories")
async def get_categories():
    """Get supported symptom categories."""
    return {
        "categories": SUPPORTED_CATEGORIES,
        "species": SUPPORTED_SPECIES
    }


# =============================================================================
# Main Triage Endpoint
# =============================================================================

@app.post("/api/triage", response_model=APIResponse)
async def triage_assessment(request: TriageRequest):
    """
    Main triage assessment endpoint.
    
    Accepts symptom information and returns urgency assessment with recommendations.
    """
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        # Validate species
        if request.species.lower() not in ["dog", "cat"]:
            return APIResponse(
                success=False,
                trace_id=trace_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_code="INVALID_SPECIES",
                error_message="Only dogs and cats are supported"
            )
        
        # Validate category
        if request.category not in SUPPORTED_CATEGORIES:
            return APIResponse(
                success=False,
                trace_id=trace_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_code="INVALID_CATEGORY",
                error_message=f"Invalid category. Supported: {SUPPORTED_CATEGORIES}"
            )
        
        # Build pet profile dict
        pet_profile = None
        if request.pet_profile:
            pet_profile = {
                "name": request.pet_profile.name,
                "species": request.pet_profile.species,
                "breed": request.pet_profile.breed,
                "age": request.pet_profile.age,
                "weight": request.pet_profile.weight,
                "sex": request.pet_profile.sex,
            }
        
        # Run triage
        result = run_triage(
            species=request.species.lower(),
            category=request.category,
            structured_fields=request.structured_fields,
            user_description=request.user_description,
            pet_profile=pet_profile,
            image_base64=request.image_base64,
            image_type=request.image_type,
            latitude=request.latitude,
            longitude=request.longitude,
            verbose=False  # Disable verbose logging for API
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        if result.get("success"):
            return APIResponse(
                success=True,
                trace_id=trace_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=processing_time,
                data=result.get("response"),
                warnings=result.get("warnings", []),
                is_er=result.get("is_er", False)
            )
        else:
            # Triage failed, return fallback
            fallback = get_fallback_response(result.get("error"))
            return APIResponse(
                success=True,  # Still return success with fallback
                trace_id=trace_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=processing_time,
                data=fallback.model_dump(),
                warnings=["Using fallback response: " + str(result.get("error", "Unknown error"))],
                is_er=False
            )
    
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        
        # Return safe fallback on any error
        fallback = get_fallback_response(str(e))
        return APIResponse(
            success=True,  # Return success with fallback to not break app
            trace_id=trace_id,
            timestamp=datetime.utcnow().isoformat(),
            processing_time_ms=processing_time,
            data=fallback.model_dump(),
            warnings=[f"Error occurred, using fallback: {str(e)}"],
            is_er=False
        )


# =============================================================================
# Chat Endpoint (Conversational Follow-up)
# =============================================================================

@app.post("/api/chat")
async def chat_followup(request: ChatMessage):
    """
    Conversational follow-up endpoint for general pet health questions.
    
    This uses the PetHealthAgent for open-ended Q&A (not structured triage).
    """
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        # Import agent here to avoid circular imports
        from RAG.agent import PetHealthAgent
        
        # Create agent instance
        agent = PetHealthAgent(
            model="gpt-4-turbo-preview",
            temperature=0.5,
            verbose=False
        )
        
        # Build context from pet info
        context = request.pet_context or {}
        
        # Run chat
        result = agent.chat(request.message, context=context)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": processing_time,
            "response": result.get("output", ""),
            "tools_used": [
                tc.get("name", "unknown") if isinstance(tc, dict) else str(tc)
                for tc in result.get("intermediate_steps", [])
            ]
        }
    
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": processing_time,
            "error": str(e),
            "response": "I apologize, but I encountered an error. Please try again or consult your veterinarian if you have urgent concerns."
        }


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure API never crashes."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "error_message": "An internal error occurred. Please try again.",
            "trace_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# =============================================================================
# Run Server (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Pet Triage API server...")
    print("Docs available at: http://localhost:8000/api/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
