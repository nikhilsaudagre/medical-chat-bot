from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models, schemas, crud, utils
import uuid

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sessions/", response_model=schemas.ChatSession)
def create_session(db: Session = Depends(get_db)):
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    return crud.create_chat_session(db, session_id=session_id)

@app.post("/messages/", response_model=schemas.ChatMessage)
def create_message(message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    # Check if session exists
    db_session = crud.get_chat_session(db, session_id=message.session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_message = models.ChatMessage(
        session_id=message.session_id,
        message=message.message,
        is_user=message.is_user
    )
    return crud.create_chat_message(db, db_message)

@app.get("/messages/{session_id}", response_model=list[schemas.ChatMessage])
def read_messages(session_id: str, db: Session = Depends(get_db)):
    return crud.get_chat_messages(db, session_id=session_id)



@app.post("/chat/", response_model=schemas.ChatResponse)
def chat_with_ai(chat_request: schemas.ChatRequest, db: Session = Depends(get_db)):

    # Check if session exists
    db_session = crud.get_chat_session(db, session_id=chat_request.session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Save user message to database
    user_message = schemas.ChatMessageCreate(
        session_id=chat_request.session_id,
        message=chat_request.message,
        is_user=1,  # 1 = user, 0 = assistant
        patient_id=chat_request.patient_id
    )
    crud.create_chat_message(db, user_message)
    
    # Generate AI response
    messages = [
        {"role": "system", "content": "You are a medical assistant..."},
        {"role": "user", "content": chat_request.message}
    ]
    ai_response = utils.get_ai_response(messages)
    
    # Save AI message to database
    ai_message = schemas.ChatMessageCreate(
        session_id=chat_request.session_id,
        message=ai_response,
        is_user=0,  # 0 = assistant
        patient_id=chat_request.patient_id
    )
    crud.create_chat_message(db, ai_message)

    return {"response": ai_response, "session_id": chat_request.session_id}



@app.post("/symptom-check/", response_model=schemas.SymptomReport)
def symptom_check(report: schemas.SymptomReportCreate, db: Session = Depends(get_db)):
    # Check if session exists
    db_session = crud.get_chat_session(db, session_id=report.session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get analysis from AI
    analysis = utils.analyze_symptoms(
        report.symptoms,
        report.severity,
        report.duration,
        report.additional_info
    )
    
    # Create report
    db_report = models.SymptomReport(
        session_id=report.session_id,
        symptoms=report.symptoms,
        severity=report.severity,
        duration=report.duration,
        additional_info=report.additional_info or "",
        analysis_result=analysis
    )
    
    return crud.create_symptom_report(db, db_report)

@app.post("/drug-info/", response_model=schemas.DrugInfoResponse)
def drug_info(request: schemas.DrugInfoRequest):
    return utils.get_drug_info(request.drug_name)

@app.get("/symptom-reports/{session_id}", response_model=list[schemas.SymptomReport])
def read_symptom_reports(session_id: str, db: Session = Depends(get_db)):
    return crud.get_symptom_reports(db, session_id=session_id)