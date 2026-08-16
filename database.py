import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL database URL (loaded from .env)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a local database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()