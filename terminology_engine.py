import json
import uuid

class TerminologyEngine:
    """
    Terminology Engine - Phase 3
    Maps internal hospital codes and free-text to global clinical standards (ICD-10/SNOMED CT).
    """
    def __init__(self):
        # Layer 1: Pre-built Exact Mapping Table
        self.icd10_mapping = {
            # Proprietary Codes
            "DNG-001": {"code": "A90", "display": "Dengue fever [classical dengue]", "system": "http://hl7.org/fhir/sid/icd-10"},
            "TYP-101": {"code": "A01.0", "display": "Typhoid fever", "system": "http://hl7.org/fhir/sid/icd-10"},
            "DM2": {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications", "system": "http://hl7.org/fhir/sid/icd-10"},
            
            # Exact existing ICD-10 codes (Pass-through)
            "A90": {"code": "A90", "display": "Dengue fever [classical dengue]", "system": "http://hl7.org/fhir/sid/icd-10"},
            "A01.0": {"code": "A01.0", "display": "Typhoid fever", "system": "http://hl7.org/fhir/sid/icd-10"},
            "I10": {"code": "I10", "display": "Essential (primary) hypertension", "system": "http://hl7.org/fhir/sid/icd-10"},
            "E11.9": {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications", "system": "http://hl7.org/fhir/sid/icd-10"}
        }

    def fuzzy_match(self, raw_text):
        """
        Layer 2: Fuzzy Matching via NLP
        (Simulated string matching for MVP. In production, this runs BioBERT.)
        """
        raw = str(raw_text).lower()
        if "dengue" in raw:
            return {"code": "A90", "display": "Dengue fever [classical dengue]", "system": "http://hl7.org/fhir/sid/icd-10"}
        if "hypertension" in raw:
            return {"code": "I10", "display": "Essential (primary) hypertension", "system": "http://hl7.org/fhir/sid/icd-10"}
        
        # Layer 3: Dead Letter Queue (Needs clinical informaticist review)
        return {"code": "UNKNOWN", "display": raw_text, "system": "LOCAL_HOSPITAL_CODE"}

    def standardize_diagnosis(self, raw_code, raw_desc):
        """Attempts Layer 1 match, then falls back to Layer 2."""
        if raw_code in self.icd10_mapping:
            return self.icd10_mapping[raw_code]
        return self.fuzzy_match(raw_desc)


class FhirTransformer:
    """Transforms our clean internal model into official FHIR R4 JSON payloads."""
    def __init__(self, terminology_engine):
        self.terminology = terminology_engine
        
    def to_fhir_bundle(self, internal_records):
        """Wraps everything into a FHIR Transaction Bundle for bulk upload."""
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }
        
        for record in internal_records:
            patient = record["patient"]
            encounter = record["encounter"]
            patient_id = str(uuid.uuid4())
            
            # 1. Map to FHIR Patient Resource
            fhir_patient = {
                "fullUrl": f"urn:uuid:{patient_id}",
                "resource": {
                    "resourceType": "Patient",
                    "identifier": [
                        {"system": "https://abdm.gov.in/aadhaar", "value": patient.get("national_id")},
                        {"system": f"https://{patient.get('source_hospital').replace(' ', '').lower()}.com/patient", "value": patient.get("patient_id")}
                    ],
                    "name": [{"family": patient.get("last_name"), "given": [patient.get("first_name")]}],
                    "gender": "male" if patient.get("gender") == "M" else "female",
                    "birthDate": patient.get("dob")
                },
                "request": {"method": "POST", "url": "Patient"}
            }
            
            # 2. Map to FHIR Condition (Diagnosis) Resource
            standardized_diag = self.terminology.standardize_diagnosis(
                encounter.get("raw_diagnosis_code"), 
                encounter.get("raw_diagnosis_desc")
            )
            
            fhir_condition = {
                "fullUrl": f"urn:uuid:{str(uuid.uuid4())}",
                "resource": {
                    "resourceType": "Condition",
                    "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
                    "code": {
                        "coding": [standardized_diag],
                        "text": encounter.get("raw_diagnosis_desc") # Preserve original text for audit trails
                    },
                    "subject": {"reference": f"urn:uuid:{patient_id}"},
                    "recordedDate": encounter.get("visit_date")
                },
                "request": {"method": "POST", "url": "Condition"}
            }
            
            bundle["entry"].extend([fhir_patient, fhir_condition])
            
        return bundle

if __name__ == "__main__":
    with open('internal_normalized_model.json', 'r') as f:
        records = json.load(f)
        
    engine = TerminologyEngine()
    transformer = FhirTransformer(engine)
    fhir_bundle = transformer.to_fhir_bundle(records)
    
    with open('fhir_r4_payload.json', 'w') as f:
        json.dump(fhir_bundle, f, indent=4)
        
    print(f"Successfully transformed data to FHIR R4 Bundle!")
