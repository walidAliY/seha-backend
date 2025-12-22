from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Base class for SQLAlchemy models [cite: 13]
Base = declarative_base()

def get_db_engine(database_url):
    """
    Creates a database engine for the provided URL.
    Used by services to connect to their respective SQLite databases[cite: 28, 34, 38, 50].
    """
    return create_engine(
        database_url, 
        connect_args={"check_same_thread": False}
    )

def get_session_local(engine):
    """Creates a session factory linked to the provided engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)