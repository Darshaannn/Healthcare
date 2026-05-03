from sqlalchemy import create_engine, Column, String, JSON, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# PostgreSQL connection string (matches docker-compose.yml)
SQLALCHEMY_DATABASE_URL = "postgresql://hapi_user:hapi_password@localhost:5432/hapi_fhir"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PatientMapping(Base):
    """Stores the link between Local Hospital IDs and the Global ABHA ID"""
    __tablename__ = "patient_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, index=True) # ABHA ID
    local_id = Column(String, index=True)  # Hospital ID (e.g. APO-123)
    hospital_name = Column(String)
    patient_data = Column(JSON) # Snapshot of demographics
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ConsentArtefact(Base):
    """Stores active consents granted by patients"""
    __tablename__ = "consents"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    doctor_id = Column(String)
    data_types = Column(JSON)
    expires_at = Column(DateTime)
    status = Column(String, default="GRANTED")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
