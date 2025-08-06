from sqlalchemy.orm import Session
from . import models, schemas

def create_chat_session(db: Session, session_id: str):
    existing = db.query(models.ChatSession).filter_by(session_id=session_id).first()
    if existing:
        return existing  # Reuse existing session
    db_session = models.ChatSession(session_id=session_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: str):
    return db.query(models.ChatSession).filter(models.ChatSession.session_id == session_id).first()

def create_chat_message(db: Session, message: schemas.ChatMessageCreate):
    db_message = models.ChatMessage(
        session_id=message.session_id,

        content=message.message,
         role="user" if message.is_user else "assistant",  # or message.role if you're passing this
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, session_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).offset(skip).limit(limit).all()

def create_symptom_report(db: Session, report: models.SymptomReport):
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_symptom_reports(db: Session, session_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.SymptomReport).filter(models.SymptomReport.session_id == session_id).offset(skip).limit(limit).all()