import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# The default falls back to SQLite if the .env variable isn't found
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Aakarsh@localhost:5432/landmark_db")

# 'echo=True' will log all SQL queries to your terminal—great for debugging
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Initializes tables in the PostgreSQL database."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for FastAPI to provide a DB session."""
    with Session(engine) as session:
        yield session
