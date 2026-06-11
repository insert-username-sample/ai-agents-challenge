import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy.orm import Session
from database_schema import Base, User, Matter, AuditLog, Precedent, engine, init_db, SessionLocal

def test_database_initialization():
    # Initialize DB (create tables in-memory sqlite)
    init_db()
    
    # Open session
    db: Session = SessionLocal()
    try:
        # Create a mock user
        user = User(
            username="senior_partner",
            hashed_password="hashed_secure_password_123",
            role="partner",
            advocate_name="Karan Singh",
            bar_council_enrollment="MH/123/2026",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.username == "senior_partner"
        assert user.role == "partner"

        # Create a mock matter linked to user
        matter = Matter(
            matter_id="CLY-ABC12345",
            creator_id=user.id,
            jurisdiction="MH-HC",
            document_type="Affidavit",
            court_name="Bombay High Court",
            cause_of_action="Arbitrary service termination.",
            relief_sought="Reinstatement with backwages.",
            acceptance_score=95.0,
            status="compiled",
        )
        db.add(matter)
        db.commit()
        db.refresh(matter)
        
        assert matter.id is not None
        assert len(user.matters) == 1
        assert user.matters[0].matter_id == "CLY-ABC12345"

        # Create a mock precedent citation
        precedent = Precedent(
            matter_id=matter.matter_id,
            citation="(2014) 9 SCC 129",
            case_name="Dashrath Rupsingh Rathod v. State of Maharashtra",
            relevance_score=0.95,
            is_overruled=False,
        )
        db.add(precedent)
        
        # Create a mock audit log
        audit = AuditLog(
            matter_id=matter.matter_id,
            action="compilation",
            details="AST successfully compiled via Drafter Agent",
            hash_value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        db.add(audit)
        db.commit()
        
        db.refresh(matter)
        assert len(matter.precedents) == 1
        assert matter.precedents[0].citation == "(2014) 9 SCC 129"
        assert len(matter.audit_logs) == 1
        assert matter.audit_logs[0].action == "compilation"

    finally:
        db.close()
        # Clean up tables
        Base.metadata.drop_all(bind=engine)
