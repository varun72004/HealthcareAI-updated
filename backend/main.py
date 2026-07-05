# backend/main.py
# ---------------------------------------------------------
# FastAPI entry point. Handles routing, authentication, 
# and connects incoming frontend requests to ML logic.
# ---------------------------------------------------------

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List
from pathlib import Path
import sys

from .database import engine, Base, get_db
from . import models
from . import schemas
import os
from dotenv import load_dotenv

from .logic import predict_disease_and_recommend, features_list, valid_symptoms

# Load environment variables from .env file
load_dotenv()

# Ensure database schema is created
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Healthcare AI API")

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security & Authentication (JWT) ---
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_if_env_missing") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to validate token and return the current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# --- API Routes ---

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        username=user.username,
        password_hash=hashed_password,
        age=user.age,
        contact=user.contact,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.UserOut)
def update_users_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.age is not None:
        current_user.age = user_update.age
    if user_update.contact is not None:
        current_user.contact = user_update.contact
        
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/symptoms", response_model=List[str])
def get_symptoms():
    return valid_symptoms

@app.post("/predict", response_model=schemas.PredictionResponse)
def predict_symptoms(request: schemas.PredictionRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = predict_disease_and_recommend(request.symptoms)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@app.post("/save_record")
def save_prediction_record(request: schemas.SaveRecordRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    history_entry = models.PredictionHistory(
        user_id=current_user.id,
        symptoms=", ".join(request.symptoms),
        predicted_disease=request.predicted_disease,
        medicines=request.medicines,
        diet=request.diet,
        workout=request.workout
    )
    db.add(history_entry)
    db.commit()
    return {"message": "Record saved successfully"}

@app.get("/history", response_model=List[schemas.PredictionHistoryOut])
def get_user_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = db.query(models.PredictionHistory).filter(models.PredictionHistory.user_id == current_user.id).order_by(models.PredictionHistory.created_at.desc()).all()
    return history
