import json
import uuid
from thefuzz import process, fuzz

class TerminologyEngine:
    """
    Advanced Terminology Engine - Phase 7
    Uses fuzzy string matching (Levenshtein distance) and a clinical synonym dictionary
    to map messy hospital data to official ICD-10 codes.
    """
    
    def __init__(self):
        # Layer 1: The Gold Standard Dictionary (ICD-10 Mapping)
        # In a production system, this would be a lookup in a SNOMED CT / ICD-10 database.
        self.knowledge_base = [
            {"code": "A90", "display": "Dengue fever [classical dengue]", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["dengue", "dengue fever", "breakbone fever", "dandy fever", "DNG-001"]},
            
            {"code": "A01.0", "display": "Typhoid fever", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["typhoid", "enteric fever", "salmonella typhi", "TYP-101"]},
            
            {"code": "I10", "display": "Essential (primary) hypertension", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["hypertension", "high blood pressure", "htn", "high bp"]},
            
            {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["diabetes", "type 2 diabetes", "dm2", "t2dm", "sugar", "मधुमेह"]},
            
            {"code": "B20", "display": "Human immunodeficiency virus [HIV] disease", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["hiv", "aids", "hiv positive"]},
            
            {"code": "J18.9", "display": "Pneumonia, unspecified organism", "system": "http://hl7.org/fhir/sid/icd-10", 
             "synonyms": ["pneumonia", "lung infection", "chest congestion"]}
        ]

    def standardize_diagnosis(self, raw_code, raw_desc):
        """
        An advanced multi-layered matching strategy.
        Returns (standardized_diag_dict, confidence_score)
        """
        raw_text = str(raw_desc).lower().strip()
        raw_code = str(raw_code).upper().strip()

        # 1. Exact Code Match (Highest Confidence)
        for item in self.knowledge_base:
            if raw_code == item["code"] or raw_code in item["synonyms"]:
                return {
                    "code": item["code"],
                    "display": item["display"],
                    "system": item["system"]
                }, 100

        # 2. Advanced Fuzzy Match against Synonyms
        # We flatten the knowledge base into a list of synonyms for the 'process' tool
        choices = []
        synonym_to_item = {}
        for item in self.knowledge_base:
            for syn in item["synonyms"]:
                choices.append(syn)
                synonym_to_item[syn] = item
        
        # We use token_set_ratio which handles word re-ordering well (e.g. 'fever dengue' vs 'dengue fever')
        best_match_synonym, score = process.extractOne(raw_text, choices, scorer=fuzz.token_set_ratio)
        
        if score >= 85:
            matched_item = synonym_to_item[best_match_synonym]
            return {
                "code": matched_item["code"],
                "display": matched_item["display"],
                "system": matched_item["system"]
            }, score
            
        # 3. Layer 3: Dead Letter Queue / Manual Review (Low Confidence)
        return {
            "code": "UNKNOWN",
            "display": raw_desc,
            "system": "PENDING_MANUAL_REVIEW"
        }, score

class FhirTransformer:
    """Transforms our standardized internal model into official FHIR R4 JSON payloads."""
    def __init__(self, terminology_engine):
        self.terminology = terminology_engine
        
    def to_fhir_bundle(self, internal_records):
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
            
            # 2. Map to FHIR Condition with Confidence Scoring
            standardized_diag, confidence = self.terminology.standardize_diagnosis(
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
                        "text": encounter.get("raw_diagnosis_desc")
                    },
                    # We add a custom extension to track the NLP confidence score (useful for manual review queues)
                    "extension": [
                        {
                            "url": "http://uhr.gov.in/fhir/StructureDefinition/mapping-confidence",
                            "valueDecimal": confidence
                        }
                    ],
                    "subject": {"reference": f"urn:uuid:{patient_id}"},
                    "recordedDate": encounter.get("visit_date")
                },
                "request": {"method": "POST", "url": "Condition"}
            }
            
            bundle["entry"].extend([fhir_patient, fhir_condition])
            
        return bundle

if __name__ == "__main__":
    # Demo of the advanced NLP matching
    engine = TerminologyEngine()
    
    test_cases = [
        ("DNG-001", "Severe Dengue Fever"), # Code match
        ("", "high bp problem"),             # Fuzzy match (Hypertension)
        ("", "patient has sugar"),           # Fuzzy match (Diabetes)
        ("", "मधुमेह"),                      # Multilingual match (Hindi for Diabetes)
        ("", "broken leg")                   # No match (Unknown)
    ]
    
    print("--- Testing Advanced Terminology NLP ---")
    for code, desc in test_cases:
        diag, score = engine.standardize_diagnosis(code, desc)
        print(f"\nInput: '{desc}' (Code: {code})")
        print(f"Result: {diag['code']} - {diag['display']} (Confidence: {score}%)")
