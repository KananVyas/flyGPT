import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, APIRouter
from src.main import FlightAgent
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
api_router = APIRouter(prefix="/api/v1")
flight_agent = FlightAgent()
class QueryModel(BaseModel):
    user_query: str

@api_router.get("/")
def read_root():
    return {"FlyGPT": "World"}

@api_router.post("/searchFlights/{search_id}")
def initiate_flight_search(search_id: int, query: QueryModel):
    best_flight_result = flight_agent.search_flights(query.user_query)
    response_json = {
        'search_id': search_id,
        'result': best_flight_result
    }
    # print(response_json)
    return JSONResponse(content=response_json, status_code=200)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3001)