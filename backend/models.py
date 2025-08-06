from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from .database import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(Text)
    role = Column(String)  # e.g., "user" or "assistant"
    created_at = Column(DateTime, default=datetime.utcnow)


class SymptomReport(Base):
    __tablename__ = "symptom_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    symptoms = Column(JSON)
    severity = Column(String(20))
    duration = Column(String(20))
    additional_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_result = Column(Text)