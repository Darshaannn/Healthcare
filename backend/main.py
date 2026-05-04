from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import shutil
import os
import json
import datetime
import requests

# Import our custom engines
from parser_sdk import HospitalDataParser
from terminology_engine import TerminologyEngine, FhirTransformer
from mpi_engine import MasterPatientIndex
from consent_engine import ConsentEngine
from clinical_rules import DrugInteractionEngine
from database import SessionLocal, engine, init_db, get_db, PatientMapping, ConsentArtefact, User
from auth import create_access_token, get_password_hash, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
from api_gateway import SecureApiGateway

app = FastAPI(title="UHR Platform API")

# Mount Static Files for the Frontend UI
app.mount("/static", StaticFiles(directory="static"), name="static")

HAPI_FHIR_URL = os.getenv("HAPI_FHIR_URL", "http://localhost:8080/fhir")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

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
ddi_engine = DrugInteractionEngine()
api_gateway = SecureApiGateway(consent_manager)

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
            
            # 4. Terminology Transformation & FHIR Bundle Generation
            fhir_bundle = transformer.to_fhir_bundle([record])
            
            # 5. Push to the REAL HAPI FHIR Server running in Docker
            fhir_status = "Generated but not pushed"
            try:
                # Use application/fhir+json as required by HL7 FHIR servers
                response = requests.post(
                    HAPI_FHIR_URL, 
                    json=fhir_bundle, 
                    headers={"Content-Type": "application/fhir+json"}
                )
                if response.status_code in [200, 201]:
                    fhir_status = "Successfully committed to HAPI FHIR Server"
                else:
                    fhir_status = f"FHIR Server Error: {response.status_code} - {response.text}"
            except Exception as e:
                fhir_status = f"FHIR Server offline. Is docker-compose running? Error: {str(e)}"
            
            results.append({
                "local_id": record["patient"]["patient_id"],
                "global_id": best_global_id,
                "fhir_summary": f"{len(fhir_bundle['entry'])} resources generated",
                "fhir_server_status": fhir_status
            })
            
        db.commit()
        return {"status": "success", "processed_records": results}
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/consent/grant")
async def grant_consent(
    patient_abha_id: str,
    doctor_id: str,
    purpose: str = "Care Management",
    valid_hours: int = 24,
    data_types: str = "Condition,MedicationRequest",
    db: Session = Depends(get_db)
):
    """
    Wires the consent engine to generate a consent artefact.
    """
    types_list = [t.strip() for t in data_types.split(",")]
    artefact = consent_manager.generate_consent_artefact(
        patient_abha_id=patient_abha_id,
        doctor_id=doctor_id,
        purpose=purpose,
        valid_hours=valid_hours,
        data_types=types_list
    )
    
    new_consent = ConsentArtefact(
        id=artefact["consent_id"],
        patient_id=artefact["patient_abha_id"],
        doctor_id=artefact["granted_to_doctor_id"],
        data_types=artefact["allowed_data_types"],
        expires_at=datetime.datetime.strptime(artefact["expires_at"], "%Y-%m-%dT%H:%M:%S"),
        status=artefact["status"]
    )
    db.add(new_consent)
    db.commit()
    
    return artefact

@app.get("/patient/{abha_id}")
async def get_patient_data(
    abha_id: str,
    resource_type: str,
    consent_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Wires the API gateway to securely fetch patient data.
    """
    consent = db.query(ConsentArtefact).filter(ConsentArtefact.id == consent_token).first()
    if not consent:
        raise HTTPException(status_code=403, detail="Consent not found or unauthorized.")
        
    # Gateway proxy call
    response = api_gateway.handle_request(consent.doctor_id, abha_id, resource_type, consent_token)
    
    if response.get("status") == 403:
        raise HTTPException(status_code=403, detail=response.get("error"))
        
    return response

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
    
    # 3. Simulate fetching from FHIR Store
    # In a real app, this would query the HAPI FHIR server using the global_id
    return {
        "global_id": global_id,
        "authorized_by": consent_token,
        "records": [
            {"resourceType": "Condition", "code": "A90", "display": "Dengue Fever"},
            {"resourceType": "MedicationRequest", "medication": "Warfarin 5mg"}
        ]
    }

@app.post("/patient/{global_id}/prescribe")
async def prescribe_medication(
    global_id: str, 
    medication: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Checks for drug-drug interactions against the patient's unified history 
    before allowing a new prescription.
    """
    # 1. Fetch patient's medication history (Simulated)
    # In production, this pulls all 'MedicationRequest' resources from the FHIR Store
    history = ["Warfarin 5mg", "Metformin 500mg"] 
    
    # 2. Run Interaction Check
    alerts = ddi_engine.check_interactions(history, medication)
    
    if alerts:
        return {
            "status": "WARNING",
            "message": "Drug-Drug Interactions Detected",
            "alerts": alerts,
            "prescribed_by": current_user.full_name
        }
        
    return {
        "status": "SAFE",
        "message": "No clinical interactions detected.",
        "medication": medication,
        "prescribed_by": current_user.full_name
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
