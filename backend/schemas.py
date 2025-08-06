from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatSessionCreate(BaseModel):
    session_id: str

class ChatSession(BaseModel):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode

class ChatMessageCreate(BaseModel):
    session_id: str
    message: str
    is_user: int
    patient_id: Optional[str] = None

class ChatMessage(BaseModel):
    id: int
    session_id: str
    message: str
    is_user: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode

class SymptomReportCreate(BaseModel):
    session_id: str
    symptoms: List[str]
    severity: str
    duration: str
    additional_info: Optional[str] = None

class SymptomReport(BaseModel):
    id: int
    session_id: str
    symptoms: List[str]
    severity: str
    duration: str
    additional_info: Optional[str] = None
    analysis_result: str
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode

class DrugInfoRequest(BaseModel):
    drug_name: str

class DrugInfoResponse(BaseModel):
    name: str
    description: str
    usage: str
    side_effects: List[str]
    interactions: List[str]

class ChatRequest(BaseModel):
    session_id: str
    message: str
    patient_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str