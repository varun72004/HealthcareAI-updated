# backend/database.py
# ---------------------------------------------------------
# Configures the PostgreSQL connection and SQLAlchemy ORM.
# ---------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Core interface to the database
engine = create_engine(DATABASE_URL)

# Factory for generating temporary database sessions for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base template that all ORM models will inherit from
Base = declarative_base()

# Generator function to safely yield a DB session and ensure it closes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()