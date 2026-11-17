import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_URL = "sqlite:///./project20.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student") # 'student' or 'admin'

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String, unique=True, index=True)
    student_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    status = Column(String, default="Open") # Open, Merged, Resolved
    is_emergency = Column(Boolean, default=False)
    merged_count = Column(Integer, default=1)
    master_ticket_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
