"""
Clausely FastAPI Backend — API endpoints for the legal compilation engine.

Provides REST endpoints for:
- /api/v1/compile  → Full ADK multi-agent pipeline
- /api/v1/reward   → Log RL reward signals
- /api/v1/validate → SFE-only validation (fast)
- /api/v1/export   → PDF/DOCX export
- /health          → Health check
"""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
import os
import uuid
from typing import List, Optional

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

load_dotenv()

from agents.orchestrator import clausely_orchestrator, run_clausely
from tools.sfe import SymbolicFormattingEngine
from tools.reward_signal import log_signal, get_aggregate_stats

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from app.rag_service import RAGService
from app.strategist_swarm import run_swarm_simulation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clausely.api")

# JWT and OAuth2 Security Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret_clausely_production_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Mock User Store for authentication fallback
MOCK_USERS = {
    "advocate": {"username": "advocate", "password": "password123", "role": "associate"},
    "senior_partner": {"username": "senior_partner", "password": "password123", "role": "partner"},
}

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generate a JWT access token containing the sub (username) and user role."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate the incoming JWT token and return user identity."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "associate")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Clausely API",
    description=(
        "Legal Compilation Engine powered by Google ADK. "
        "Compiles legal intent into court-ready documents for Indian courts."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class IntakeRequest(BaseModel):
    jurisdiction: str = "MH-DISTRICT"
    document_type: str = "Affidavit"
    court_name: str = "Civil Judge Senior Division"
    cause_of_action: str = ""
    relief_sought: str = ""
    client_name: Optional[str] = None
    opposing_party: Optional[str] = None
    language: str = "en"
    prompt: Optional[str] = None
    run_strategy: bool = False
    payload_base64: Optional[str] = None
    signature_sha256: Optional[str] = None
    checksum: Optional[str] = None
    origin_certificate: Optional[str] = None
    timestamp_epoch: Optional[int] = None



class ClauselyResponse(BaseModel):
    matter_id: str
    document_text: str
    acceptance_score: float
    fatal_defects: List[str]
    curable_defects: List[str]
    registry_checks: dict = {}
    outcome_scenarios: Optional[List[dict]] = None
    objections: Optional[List[dict]] = None
    strategy_memo: Optional[str] = None
    case_base_id: str = ""
    similar_matters: Optional[List[dict]] = None


class RewardRequest(BaseModel):
    matter_id: str
    signal_type: str  # filed, accepted, rejected, edited_minor, edited_major
    details: str = ""


class ValidateRequest(BaseModel):
    document_text: str
    jurisdiction: str = "MH-DISTRICT"
    document_type: str = "affidavit"


class ExportRequest(BaseModel):
    document_text: str
    jurisdiction: str = "MH-DISTRICT"
    format: str = "pdf"  # "pdf" or "docx"
    metadata: dict = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate advocate credentials and issue a JWT bearer token."""
    # Check actual database first if available
    try:
        from database_schema import User as DBUser, SessionLocal as DBSessionLocal
        db = DBSessionLocal()
        try:
            db_user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
            if db_user and db_user.hashed_password == form_data.password:
                access_token = create_access_token(
                    data={"sub": db_user.username, "role": db_user.role}
                )
                return {"access_token": access_token, "token_type": "bearer"}
        finally:
            db.close()
    except Exception:
        # Fail silently and fallback to mock user dictionary
        pass

    # Fallback to Mock User Store
    user = MOCK_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/compile", response_model=ClauselyResponse)
async def compile_document(request: IntakeRequest, current_user: dict = Depends(get_current_user)):
    """
    Main endpoint: compile legal intent into a court-ready document.
    Runs the full ADK multi-agent pipeline. Requires valid JWT credentials.
    """
    try:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=clausely_orchestrator,
            app_name="clausely",
            session_service=session_service,
        )
        result = await run_clausely(
            runner,
            request.model_dump(),
            run_strategy=request.run_strategy,
        )
        return ClauselyResponse(**result)
    except Exception as e:
        logger.error(f"Compilation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reward")
async def log_reward(request: RewardRequest, current_user: dict = Depends(get_current_user)):
    """
    Log a reward signal for self-evolution.
    Call this when: document filed, accepted, rejected, edited. Requires valid JWT.
    """
    reward_values = {
        "filed": 0.5,
        "accepted": 3.0,
        "rejected": -3.0,
        "edited_minor": 0.5,
        "edited_major": 0.2,
        "client_approved": 1.0,
    }
    value = reward_values.get(request.signal_type, 0.0)
    result = log_signal(
        matter_id=request.matter_id,
        signal_type=request.signal_type,
        reward_value=value,
        details=request.details,
    )
    return result


@app.post("/api/v1/validate")
async def validate_document(request: ValidateRequest):
    """
    Quick validation — runs document through SFE only (no LLM calls).
    Fast endpoint for real-time validation feedback. Publicly accessible.
    """
    try:
        from agents.acceptor import simulate_registry_check
        result = simulate_registry_check(
            document_text=request.document_text,
            jurisdiction=request.jurisdiction,
            document_type=request.document_type,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/export")
async def export_document(request: ExportRequest):
    """
    Export document as PDF or DOCX.
    Uses the SFE to apply exact court formatting rules. Publicly accessible.
    """
    try:
        sfe = SymbolicFormattingEngine(request.jurisdiction)

        # Build document dict for SFE
        doc_dict = {
            "sections": {"content": request.document_text},
            "metadata": request.metadata,
            "formatting": {},
        }

        if request.format == "pdf":
            pdf_bytes = sfe.export_pdf(doc_dict)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=clausely_document.pdf"
                },
            )
        elif request.format == "docx":
            docx_bytes = sfe.export_docx(doc_dict)
            return Response(
                content=docx_bytes,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": "attachment; filename=clausely_document.docx"
                },
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get aggregate reward signal statistics. Requires valid JWT."""
    return get_aggregate_stats()


@app.get("/api/v1/jurisdictions")
async def list_jurisdictions():
    """List supported court jurisdictions."""
    return {
        "jurisdictions": SymbolicFormattingEngine.supported_jurisdictions(),
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "clausely-adk",
        "model": "gemini-3.5-flash",
    }


# ---------------------------------------------------------------------------
# Strategist Swarm MVP Route
# ---------------------------------------------------------------------------

class StrategySources(BaseModel):
    matter_context: bool = True
    documents: bool = True
    case_base: bool = True
    playbooks: bool = True
    research: bool = True

class UploadedFile(BaseModel):
    name: str
    content: str

class StrategyRequest(BaseModel):
    query: str
    sources: StrategySources
    api_key: Optional[str] = None
    uploaded_files: Optional[List[UploadedFile]] = None

class StrategyResponse(BaseModel):
    summary: str
    risks: List[str]
    opportunities: List[str]
    assumptions: List[str]
    missing_information: List[str]
    recommendation: str
    alternative_strategies: List[str]
    evidence: List[str]
    confidence: float

rag_service = RAGService()

@app.post("/api/strategy/run", response_model=StrategyResponse)
async def run_strategy_api(request: StrategyRequest):
    """
    Execute real RAG retrieval and 5-agent sequential swarm reasoning simulation using Gemini.
    """
    api_key = request.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Neither GEMINI_API_KEY nor GOOGLE_API_KEY is configured. Please configure it to use the Strategist Swarm."
        )
        
    try:
        # 1. Build index from selected sources
        selected_dict = {
            "matter_context": request.sources.matter_context,
            "documents": request.sources.documents,
            "case_base": request.sources.case_base,
            "playbooks": request.sources.playbooks,
            "research": request.sources.research
        }
        
        logger.info(f"Building RAG index for: {selected_dict}")
        uploaded_list = [f.model_dump() for f in request.uploaded_files] if request.uploaded_files else None
        num_chunks = rag_service.build_index(selected_dict, uploaded_list)
        logger.info(f"Indexed {num_chunks} chunks.")
        
        # 2. Retrieve relevant chunks
        logger.info(f"Retrieving top chunks for query: '{request.query}'")
        retrieved = rag_service.retrieve(request.query, k=5)
        logger.info(f"Retrieved {len(retrieved)} chunks.")
        
        # 3. Run multi-agent sequential swarm simulation
        logger.info("Running Multi-Agent Swarm Simulation...")
        result = run_swarm_simulation(request.query, retrieved, api_key)
        
        # Format response evidence
        evidence_sources = list(set([chunk["source"] for chunk in retrieved])) if retrieved else []
        if not evidence_sources:
            evidence_sources = ["General Precedents"]
            
        return StrategyResponse(
            summary=result.get("summary", ""),
            risks=result.get("risks", []),
            opportunities=result.get("opportunities", []),
            assumptions=result.get("assumptions", []),
            missing_information=result.get("missing_information", []),
            recommendation=result.get("recommendation", ""),
            alternative_strategies=result.get("alternative_strategies", []),
            evidence=evidence_sources,
            confidence=result.get("confidence", 0.8)
        )
    except Exception as e:
        logger.error(f"Error executing strategy run: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
