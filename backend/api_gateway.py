import json
from consent_engine import ConsentEngine

class SecureApiGateway:
    """
    SMART on FHIR API Gateway - Phase 5
    Intercepts all incoming requests from doctors/hospitals and validates them
    against the Consent Engine before hitting the actual FHIR Server.
    """
    
    def __init__(self, consent_engine):
        self.consent_engine = consent_engine
        
        # Simulating the actual HAPI FHIR Database we built in Phase 1
        self.mock_fhir_database = {
            "ABHA-1234": [
                {"resourceType": "Condition", "code": "A90", "display": "Dengue Fever"},
                {"resourceType": "MedicationRequest", "medication": "Paracetamol 500mg"}
            ]
        }

    def handle_request(self, doctor_id, patient_abha_id, requested_resource, consent_token):
        """
        The main interceptor proxy function.
        """
        print(f"\n[API GATEWAY] Intercepted request from Doctor {doctor_id} for Patient {patient_abha_id} ({requested_resource})")
        
        # 1. Validation Layer
        is_authorized, message = self.consent_engine.verify_consent(consent_token, doctor_id, requested_resource)
        
        if not is_authorized:
            print(f"[API GATEWAY] ❌ ACCESS DENIED: {message}")
            return {"status": 403, "error": message}
            
        print("[API GATEWAY] ✅ Consent Verified. Forwarding request to FHIR Server...")
        
        # 2. Proxy Layer (Fetch from FHIR Server)
        patient_data = self.mock_fhir_database.get(patient_abha_id, [])
        
        # 3. Filter Layer (Ensure we only return exactly what was consented to)
        filtered_data = [res for res in patient_data if res["resourceType"] == requested_resource]
        
        print(f"[API GATEWAY] 📤 Returning {len(filtered_data)} {requested_resource} records to Dr. {doctor_id}.")
        return {"status": 200, "data": filtered_data}


if __name__ == "__main__":
    # --- SIMULATION WORKFLOW ---
    engine = ConsentEngine()
    gateway = SecureApiGateway(engine)
    
    PATIENT_ID = "ABHA-1234"
    DR_SMITH = "DOC-SMITH-001"
    DR_JONES = "DOC-JONES-002"
    
    print("--- 1. Patient Grants Consent ---")
    # Patient Rahul uses his app to grant Dr. Smith access to ONLY his Diagnoses for 24 hours.
    artefact = engine.generate_consent_artefact(
        patient_abha_id=PATIENT_ID,
        doctor_id=DR_SMITH,
        purpose="Care Management",
        valid_hours=24,
        data_types=["Condition"] # Only allowed to see 'Condition' (Diagnosis). NOT 'MedicationRequest'.
    )
    CONSENT_TOKEN = artefact["consent_id"]
    print(f"Patient generated Consent Token: {CONSENT_TOKEN}")
    print(f"Allowed Access: {artefact['allowed_data_types']}")
    
    print("\n--- 2. Valid Request ---")
    # Dr. Smith asks for Conditions using the correct token
    gateway.handle_request(DR_SMITH, PATIENT_ID, "Condition", CONSENT_TOKEN)
    
    print("\n--- 3. Invalid Data Type Request ---")
    # Dr. Smith tries to snoop on Medications, but Rahul didn't consent to that!
    gateway.handle_request(DR_SMITH, PATIENT_ID, "MedicationRequest", CONSENT_TOKEN)
    
    print("\n--- 4. Unauthorized Doctor Request ---")
    # Dr. Jones tries to steal and use Dr. Smith's token
    gateway.handle_request(DR_JONES, PATIENT_ID, "Condition", CONSENT_TOKEN)
