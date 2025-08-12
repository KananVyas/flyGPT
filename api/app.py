import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, APIRouter
from src.main import FlightAgent
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("FLIGHTS_API_HOST", "0.0.0.0")
PORT = int(os.getenv("FLIGHTS_API_PORT", "3001"))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# FastAPI app configuration
app = FastAPI(
    title="FlyGPT API",
    description="AI Agent for Smart Flight Search - Multi-agent system for finding best flight deals across multiple dates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# API Router
api_router = APIRouter(prefix="/api/v1")
flight_agent = FlightAgent()

class QueryModel(BaseModel):
    user_query: str

@api_router.get("/")
def read_root():
    return {
        "service": "FlyGPT API",
        "version": "1.0.0",
        "description": "AI Agent for Smart Flight Search",
        "docs": f"{BASE_URL}:{PORT}/docs",
        "health": f"{BASE_URL}:{PORT}/health"
    }

@api_router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FlyGPT API",
        "timestamp": "2025-01-27T00:00:00Z"
    }

@api_router.post("/searchFlights/{search_id}")
def initiate_flight_search(search_id: int, query: QueryModel):
    try:
        best_flight_result = flight_agent.search_flights(query.user_query)
        response_json = {
            'search_id': search_id,
            'result': best_flight_result
        }
        return JSONResponse(content=response_json, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flight search failed: {str(e)}"
        )

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    print(f"🚀 Starting FlyGPT API Server...")
    print(f"📍 Host: {HOST}")
    print(f"🔌 Port: {PORT}")
    print(f"🌐 Base URL: {BASE_URL}:{PORT}")
    print(f"📚 API Documentation: {BASE_URL}:{PORT}/docs")
    print(f"🔍 Health Check: {BASE_URL}:{PORT}/health")
    print(f"🔧 Debug Mode: {DEBUG}")
    print("-" * 50)
    
    uvicorn.run(
        "app:app", 
        host=HOST, 
        port=PORT, 
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )