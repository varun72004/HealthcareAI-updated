# backend/schemas.py
# ---------------------------------------------------------
# Pydantic models for data validation and API serialization.
# ---------------------------------------------------------

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---

class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    age: int
    contact: str
    email: EmailStr

class UserOut(BaseModel):
    id: int
    name: str
    username: str
    email: str
    age: int
    contact: str
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    contact: Optional[str] = None

# --- Auth Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- AI Prediction Schemas ---

class PredictionRequest(BaseModel):
    symptoms: List[str]

class PredictionResponse(BaseModel):
    predicted_disease: str
    medicines: str
    diet: str
    workout: str
    
class SaveRecordRequest(BaseModel):
    symptoms: List[str]
    predicted_disease: str
    medicines: str
    diet: str
    workout: str

class PredictionHistoryOut(BaseModel):
    id: int
    symptoms: str
    predicted_disease: str
    medicines: str
    diet: str
    workout: str
    created_at: datetime
    
    class Config:
        from_attributes = True