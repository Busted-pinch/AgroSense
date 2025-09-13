import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ==============================
# Absolute path setup
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to db folder's parent
DB_FOLDER = os.path.join(BASE_DIR, "../../db")        # adjust relative to app/db structure
os.makedirs(DB_FOLDER, exist_ok=True)                 # ensure folder exists

DATABASE_PATH = os.path.join(DB_FOLDER, "agrosense.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ==============================
# SQLAlchemy engine & session
# ==============================
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": True})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ==============================
# Example User table
# ==============================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
class Guidelines(Base):
    __tablename__ = "guidelines"
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True)
    disease_name = Column(String, index=True)
    instructions = Column(String)
# ==============================
# Create tables
# ==============================
Base.metadata.create_all(bind=engine)