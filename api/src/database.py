import os
from sqlalchemy import Column, Integer, Float, String, Text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Resolve database storage path dynamically (aligned with project structure)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
if not os.path.exists(UPLOAD_DIR) and not UPLOAD_DIR.startswith("/app"):
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
if os.name == 'nt' and UPLOAD_DIR == "/app/uploads":
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))

os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_PATH = os.path.join(UPLOAD_DIR, "hazard_events.db")

# Format database URL properly for async SQLite (aiosqlite)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
if os.name == 'nt':
    clean_path = DB_PATH.replace("\\", "/")
    DATABASE_URL = f"sqlite+aiosqlite:///{clean_path}"

print(f"[Database] Initializing persistent database at: {DATABASE_URL}")

# Setup engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class HazardEventModel(Base):
    __tablename__ = "hazard_events"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(String(50), index=True, nullable=False)
    timestamp_ms = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), index=True, nullable=False)
    detections = Column(Text, nullable=False)  # JSON-encoded array of Detection schema
    thumbnail_b64 = Column(Text, nullable=True)

# Database Session Dependency for FastAPI routes
async def get_db():
    async with async_session() as session:
        yield session
