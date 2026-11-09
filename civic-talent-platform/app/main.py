import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.models import Application, Base, Candidate, Vacancy

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./civic_talent.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
API_KEY = os.getenv("API_KEY", "local-development-only")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("civic_talent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenient for the demo. Production environments should use reviewed migrations.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Civic Talent Platform", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def request_log(request: Request, call_next):
    start = time.monotonic()
    request_id = str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(json.dumps({"event": "unhandled_request", "request_id": request_id}))
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"event": "request", "request_id": request_id, "method": request.method, "path": request.url.path, "status": response.status_code, "duration_ms": round((time.monotonic() - start) * 1000, 2)}))
    return response


def db_session():
    with SessionLocal() as db:
        yield db


def require_key(x_api_key: str | None = Header(default=None)):
    import secrets
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    skills: list[str] = Field(default_factory=list, max_length=30)


class CandidateOut(CandidateCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class VacancyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    department: str = Field(min_length=1, max_length=120)


class VacancyOut(VacancyCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ApplicationCreate(BaseModel):
    candidate_id: int = Field(gt=0)
    vacancy_id: int = Field(gt=0)


class ApplicationOut(ApplicationCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)


class StatusChange(BaseModel):
    status: Literal["reviewing", "interview", "offered", "rejected", "withdrawn"]


TRANSITIONS = {
    "submitted": {"reviewing", "withdrawn"},
    "reviewing": {"interview", "rejected", "withdrawn"},
    "interview": {"offered", "rejected", "withdrawn"},
    "offered": {"withdrawn"},
    "rejected": set(),
    "withdrawn": set(),
}


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready(db: Session = Depends(db_session)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready"}


@app.post("/v1/candidates", response_model=CandidateOut, status_code=201, dependencies=[Depends(require_key)])
def create_candidate(body: CandidateCreate, db: Session = Depends(db_session)):
    candidate = Candidate(**body.model_dump())
    db.add(candidate)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Candidate email already registered")
    db.refresh(candidate)
    return candidate


@app.get("/v1/candidates", response_model=list[CandidateOut], dependencies=[Depends(require_key)])
def candidates(db: Session = Depends(db_session), limit: int = 20, offset: int = 0):
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(422, "Invalid pagination")
    return db.scalars(select(Candidate).order_by(Candidate.id).limit(limit).offset(offset)).all()


@app.post("/v1/vacancies", response_model=VacancyOut, status_code=201, dependencies=[Depends(require_key)])
def create_vacancy(body: VacancyCreate, db: Session = Depends(db_session)):
    vacancy = Vacancy(**body.model_dump())
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy


@app.get("/v1/vacancies", response_model=list[VacancyOut], dependencies=[Depends(require_key)])
def vacancies(db: Session = Depends(db_session)):
    return db.scalars(select(Vacancy).order_by(Vacancy.id).limit(100)).all()


@app.post("/v1/applications", response_model=ApplicationOut, status_code=201, dependencies=[Depends(require_key)])
def create_application(body: ApplicationCreate, db: Session = Depends(db_session)):
    if not db.get(Candidate, body.candidate_id) or not db.get(Vacancy, body.vacancy_id):
        raise HTTPException(404, "Candidate or vacancy does not exist")
    record = Application(**body.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Application already exists")
    db.refresh(record)
    return record


@app.patch("/v1/applications/{application_id}/status", response_model=ApplicationOut, dependencies=[Depends(require_key)])
def change_status(application_id: int, body: StatusChange, db: Session = Depends(db_session)):
    record = db.get(Application, application_id)
    if not record:
        raise HTTPException(404, "Application not found")
    if body.status not in TRANSITIONS[record.status]:
        raise HTTPException(409, f"Transition from {record.status} to {body.status} not permitted")
    record.status = body.status
    db.commit()
    db.refresh(record)
    return record
