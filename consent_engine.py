import uuid
from datetime import datetime, timedelta

class ConsentEngine:
    """
    Consent Engine - Phase 5
    Generates and manages ABDM-compliant Consent Artefacts.
    Patients use this to grant time-limited, purpose-specific access to their data.
    """
    
    def __init__(self):
        self.active_consents = {}

    def generate_consent_artefact(self, patient_abha_id, doctor_id, purpose, valid_hours, data_types):
        """
        Creates a secure cryptographic token/artefact granting access.
        """
        consent_id = f"CONSENT-{str(uuid.uuid4())[:8].upper()}"
        
        expiry_time = datetime.now() + timedelta(hours=valid_hours)
        
        artefact = {
            "consent_id": consent_id,
            "patient_abha_id": patient_abha_id,
            "granted_to_doctor_id": doctor_id,
            "purpose_of_request": purpose, # e.g., "Care Management", "Emergency"
            "allowed_data_types": data_types, # e.g., ["Condition", "Observation", "MedicationRequest"]
            "status": "GRANTED",
            "expires_at": expiry_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        # Store in our database
        self.active_consents[consent_id] = artefact
        return artefact

    def verify_consent(self, consent_id, doctor_id, requested_data_type):
        """
        Validates if a request is authorized by an active consent artefact.
        """
        if consent_id not in self.active_consents:
            return False, "Consent Artefact not found or revoked."
            
        artefact = self.active_consents[consent_id]
        
        # 1. Check Expiry Time
        if datetime.now() > datetime.strptime(artefact["expires_at"], "%Y-%m-%dT%H:%M:%S"):
            artefact["status"] = "EXPIRED"
            return False, "Consent has expired."
            
        # 2. Check Doctor Identity
        if artefact["granted_to_doctor_id"] != doctor_id:
            return False, "Unauthorized: Doctor ID does not match the consent token."
            
        # 3. Check Data Type Authorization
        if requested_data_type not in artefact["allowed_data_types"] and "*" not in artefact["allowed_data_types"]:
            return False, f"Unauthorized: Patient did not grant access to '{requested_data_type}' data."
            
        return True, "Authorized"
