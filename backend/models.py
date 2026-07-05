# backend/models.py
# ---------------------------------------------------------
# Defines the SQLAlchemy ORM models representing the database schema.
# ---------------------------------------------------------

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# --- Table: Users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String) # Stores hashed password, never plain text
    age = Column(Integer)
    contact = Column(String)
    email = Column(String, unique=True, index=True)
    
    # 1-to-Many relationship with PredictionHistory
    predictions = relationship("PredictionHistory", back_populates="owner")


# --- Table: Prediction History ---
class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Foreign key linking to User
    symptoms = Column(String) 
    predicted_disease = Column(String)
    medicines = Column(String)
    diet = Column(String)
    workout = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) # Auto-timestamps the record

    # Many-to-1 relationship back to User
    owner = relationship("User", back_populates="predictions")
