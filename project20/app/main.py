import random
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import init_db, get_db, User, Ticket
from app.auth import hash_password, verify_password, create_access_token, decode_token
from app.triage_agent import triage_complaint
from app.deduplicator import deduplicator

app = FastAPI(title="Project 20: Agentic Triage Assistant")

# Initialize database tables on startup
init_db()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

# Pydantic Schemas
class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "student"

class LoginSchema(BaseModel):
    username: str
    password: str

class TicketSubmitSchema(BaseModel):
    student_name: str
    content: str

# API Routes
@app.post("/api/auth/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(data.password)
    user = User(username=data.username, email=data.email, hashed_password=hashed, role=data.role)
    db.add(user)
    db.commit()
    return {"message": "User registered successfully!"}

@app.post("/api/auth/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "role": user.role, "username": user.username}

@app.post("/api/tickets/submit")
def submit_ticket(data: TicketSubmitSchema, db: Session = Depends(get_db)):
    triage = triage_complaint(data.content)
    ticket_code = f"TICK-{random.randint(1000, 9999)}"

    # Check emergency bypass
    if triage["is_emergency"]:
        ticket = Ticket(
            ticket_code=ticket_code,
            student_name=data.student_name,
            content=data.content,
            category=triage["category"],
            urgency=triage["urgency"],
            is_emergency=True,
            status="CRITICAL BYPASS"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return {
            "status": "EMERGENCY_BYPASS",
            "message": "Zero-Latency Emergency Bypass Triggered!",
            "ticket": {
                "ticket_code": ticket.ticket_code,
                "category": ticket.category,
                "urgency": ticket.urgency,
                "is_emergency": True
            }
        }

    # Check FAISS Deduplication
    # Generate temporary ID for check
    temp_id = random.randint(100000, 999999)
    dedup_res = deduplicator.check_and_add(temp_id, data.content)

    if dedup_res["is_duplicate"]:
        # Find master ticket in DB if available or create merged
        master = db.query(Ticket).filter(Ticket.id == dedup_res["matched_ticket_id"]).first()
        if master:
            master.merged_count += 1
            db.commit()
            return {
                "status": "MERGED",
                "message": f"Merged into Master Work Order #{master.ticket_code} ({dedup_res['similarity']}% similarity)",
                "master_ticket_code": master.ticket_code,
                "similarity": dedup_res["similarity"]
            }

    # Create new master ticket
    ticket = Ticket(
        ticket_code=ticket_code,
        student_name=data.student_name,
        content=data.content,
        category=triage["category"],
        urgency=triage["urgency"],
        is_emergency=False,
        status="Open"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "status": "CREATED",
        "message": "New Master Work Order created successfully.",
        "ticket": {
            "ticket_code": ticket.ticket_code,
            "category": ticket.category,
            "urgency": ticket.urgency,
            "status": ticket.status
        }
    }

@app.get("/api/tickets/all")
def get_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return tickets
