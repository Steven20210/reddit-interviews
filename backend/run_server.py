#!/usr/bin/env python3
"""
Script to run the FastAPI server for InterviewsDB
"""

import uvicorn
from app import app

if __name__ == "__main__":
    print("Starting InterviewsDB FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation will be available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
