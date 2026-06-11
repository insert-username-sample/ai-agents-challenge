"""
Clausely Database Schema — SQLAlchemy 2.0 Declarative Models.

Defines the persistence layer for:
- User & Advocate Registry (with RBAC roles)
- Matter & Case Filing Drafts (Legal AST state tracking)
- Audit Logs & Evidence Ledger Transactions (Cryptographic anchors)
- Precedent Citations (Case law reference mappings)
"""

from __future__ import annotations

import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Boolean,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


class User(Base):
    """
    Law Firm User / Advocate table.
    Enforces Role-Based Access Control (RBAC) via the role field.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="associate", nullable=False)  # admin, partner, associate, client
    advocate_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    bar_council_enrollment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    # Relationship to matters compiled by this user
    matters: Mapped[List[Matter]] = relationship(back_populates="creator", cascade="all, delete-orphan")


class Matter(Base):
    """
    Matter / Legal Case table.
    Stores case context, Legal AST states, and current formatting progress.
    """
    __tablename__ = "matters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    creator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(50), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    court_name: Mapped[str] = mapped_column(String(150), nullable=False)
    client_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    opposing_party: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    cause_of_action: Mapped[str] = mapped_column(Text, nullable=False)
    relief_sought: Mapped[str] = mapped_column(Text, nullable=False)
    document_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acceptance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # draft, compiled, filed, rejected
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    creator: Mapped[Optional[User]] = relationship(back_populates="matters")
    audit_logs: Mapped[List[AuditLog]] = relationship(back_populates="matter", cascade="all, delete-orphan")
    precedents: Mapped[List[Precedent]] = relationship(back_populates="matter", cascade="all, delete-orphan")


class AuditLog(Base):
    """
    Evidence Ledger & Simulation Audit Trail table.
    Logs every state mutation, MCTS step, and ZK proof attestation.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(String(50), ForeignKey("matters.matter_id"), nullable=False, index=True)
    node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # mutation, verification, compilation
    details: Mapped[str] = mapped_column(Text, nullable=False)
    hash_value: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 hash
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    matter: Mapped[Matter] = relationship(back_populates="audit_logs")


class Precedent(Base):
    """
    Precedents and Citations used in a Case.
    Links verified case citation patterns with their status.
    """
    __tablename__ = "precedents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(String(50), ForeignKey("matters.matter_id"), nullable=False, index=True)
    citation: Mapped[str] = mapped_column(String(255), nullable=False)
    case_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_overruled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    matter: Mapped[Matter] = relationship(back_populates="precedents")


# SQLite In-memory engine helper for quick tests
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Helper to initialize SQLite in-memory database schema for verification."""
    Base.metadata.create_all(bind=engine)
