from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import shutil
import os
import json
import datetime

# Import our custom engines
from parser_sdk import HospitalDataParser
from terminology_engine import TerminologyEngine, FhirTransformer
from mpi_engine import MasterPatientIndex
from consent_engine import ConsentEngine
from database import SessionLocal, engine, init_db, get_db, PatientMapping, ConsentArtefact, User
from auth import create_access_token, get_password_hash, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password

app = FastAPI(title="UHR Platform API")

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}. Ensure Postgres is running.")

# --- ENGINES INITIALIZATION ---
terminology = TerminologyEngine()
transformer = FhirTransformer(terminology)
mpi = MasterPatientIndex()
consent_manager = ConsentEngine()

# --- AUTH ENDPOINTS ---

@app.post("/register")
def register_doctor(username: str, password: str, full_name: str, db: Session = Depends(get_db)):
    """Registers a new doctor in the system."""
    hashed_pw = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_pw, full_name=full_name)
    db.add(new_user)
    db.commit()
    return {"message": "Doctor registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates a user and returns a JWT access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- DATA ENDPOINTS ---

@app.post("/ingest")
async def ingest_data(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingests a hospital CSV, runs normalization, terminology mapping, 
    MPI linking, and prepares FHIR payloads.
    """
    # 1. Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Run Parser
        parser = HospitalDataParser(temp_path)
        records = parser.parse()
        
        results = []
        for record in records:
            # 3. Run MPI (Link to Global ID)
            # In Phase 6, we check the DB first
            existing_mappings = db.query(PatientMapping).all()
            # Simple simulation of MPI check against DB
            best_global_id = None
            for mapping in existing_mappings:
                score = mpi.calculate_match_score(record["patient"], mapping.patient_data)
                if score >= 0.85:
                    best_global_id = mapping.global_id
                    break
            
            if not best_global_id:
                best_global_id, _ = mpi.link_patient(record["patient"])
            
            # Save Mapping to DB
            new_mapping = PatientMapping(
                global_id=best_global_id,
                local_id=record["patient"]["patient_id"],
                hospital_name=record["patient"]["source_hospital"],
                patient_data=record["patient"]
            )
            db.add(new_mapping)
            
            # 4. Terminology Transformation
            fhir_bundle = transformer.to_fhir_bundle([record])
            
            results.append({
                "local_id": record["patient"]["patient_id"],
                "global_id": best_global_id,
                "fhir_summary": f"{len(fhir_bundle['entry'])} resources generated"
            })
            
        db.commit()
        return {"status": "success", "processed_records": results}
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/patient/{global_id}/records")
async def get_patient_records(
    global_id: str, 
    consent_token: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Secure access to patient records via API Gateway logic.
    Only allows access if the current logged-in doctor matches the consent doctor_id.
    """
    # 1. Check Consent in DB
    consent = db.query(ConsentArtefact).filter(ConsentArtefact.id == consent_token).first()
    
    if not consent:
        raise HTTPException(status_code=403, detail="Consent not found or unauthorized.")
    
    # 2. Security Check: Does the logged-in doctor match the consent?
    if consent.doctor_id != str(current_user.id) and consent.doctor_id != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized: This consent was granted to a different doctor.")
    
    # 2. Check Expiry
    if consent.expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=403, detail="Consent has expired.")
        
    # 3. Simulate fetching from FHIR Store
    # In a real app, this would query the HAPI FHIR server using the global_id
    return {
        "global_id": global_id,
        "authorized_by": consent_token,
        "records": [
            {"resourceType": "Condition", "code": "A90", "display": "Dengue Fever"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
