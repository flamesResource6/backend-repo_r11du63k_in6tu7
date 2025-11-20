import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from database import create_document, get_documents
from schemas import Booking

app = FastAPI(
    title="Libya Car Rental API",
    description="API for booking requests and content for the Libya car rental landing page",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Libya Car Rental API is running"}

# Public content endpoints for the landing page
class Vehicle(BaseModel):
    id: str
    name_ar: str
    category_ar: str
    seats: int
    price_per_day: int
    thumbnail: str  # URL to small image or 3D thumb

# For demo purposes: static fleet list (content, not bookings)
FLEET: List[Vehicle] = [
    Vehicle(id="sport-01", name_ar="سيارة رياضية فاخرة", category_ar="رياضية",
            seats=2, price_per_day=650, thumbnail="/cars/sport-01.jpg"),
    Vehicle(id="sedan-01", name_ar="سيدان مريحة", category_ar="سيدان",
            seats=5, price_per_day=280, thumbnail="/cars/sedan-01.jpg"),
    Vehicle(id="suv-01", name_ar="دفع رباعي عائلي", category_ar="دفع رباعي",
            seats=7, price_per_day=420, thumbnail="/cars/suv-01.jpg"),
]

@app.get("/api/fleet", response_model=List[Vehicle])
def get_fleet():
    return FLEET

# Booking request endpoint (uses MongoDB)
@app.post("/api/book")
def create_booking(payload: Booking):
    try:
        # Validate dates
        if payload.return_date <= payload.pickup_date:
            raise HTTPException(status_code=400, detail="Return date must be after pickup date")
        booking_id = create_document("booking", payload)
        return {"status": "ok", "booking_id": booking_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        docs = get_documents("booking", {}, limit=1)
        response["database"] = "✅ Connected"
        response["sample"] = len(docs)
    except Exception as e:
        response["database"] = f"⚠️ {str(e)[:80]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
