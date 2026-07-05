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
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Extract query parameters to avoid duplicate 'sslmode' errors
connect_args = {}
if DATABASE_URL.startswith("postgresql://") and "neon.tech" in DATABASE_URL:
    # Ensure SSL is required for Neon
    if "sslmode" not in DATABASE_URL:
        connect_args["sslmode"] = "require"

# Core interface to the database with connection pooling handled correctly
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Checks connection validity before using it (fixes dropped connections)
    pool_recycle=300,    # Recycles connections every 5 minutes (good for serverless DBs)
    connect_args=connect_args
)
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