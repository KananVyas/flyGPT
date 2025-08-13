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
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("FLIGHTS_API_HOST", "0.0.0.0")
PORT = int(os.getenv("FLIGHTS_API_PORT", "3001"))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Thread pool executor for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

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
async def read_root():
    return {
        "service": "FlyGPT API",
        "version": "1.0.0",
        "description": "AI Agent for Smart Flight Search",
        "docs": f"{BASE_URL}:{PORT}/docs",
        "health": f"{BASE_URL}:{PORT}/health"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FlyGPT API",
        "timestamp": "2025-01-27T00:00:00Z"
    }

async def run_flight_search_in_executor(user_query: str):
    """
    Run the flight search in a thread pool executor to avoid blocking the event loop
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, 
        flight_agent.search_flights, 
        user_query
    )

@api_router.post("/searchFlights/{search_id}")
async def initiate_flight_search(search_id: int, query: QueryModel):
    try:
        # Run the CPU-intensive flight search in a thread pool
        best_flight_result = await run_flight_search_in_executor(query.user_query)
        
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

@api_router.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown
    """
    executor.shutdown(wait=True)

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
    print(f"🧵 Thread Pool Workers: 1")
    print("-" * 50)
    
    uvicorn.run(
        "app:app", 
        host=HOST, 
        port=PORT, 
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )