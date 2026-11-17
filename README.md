# Project 20: Agentic Triage Assistant
**Developed by Team LOGIC LABS**  
*Department of Computer Science & Engineering, East Point College of Engineering & Technology*

## Overview
Project 20 is an automated campus grievance triage platform featuring:
- **FastAPI Backend & SQLite Storage**
- **JWT Authentication**
- **FAISS Vector Deduplication Engine** (Merging identical reports with 0.85 similarity threshold)
- **Zero-Latency Emergency Safety Bypass**

## Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch FastAPI App
python -m uvicorn app.main:app --reload

# 3. Access Web Application
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser
