import json
import uuid
from thefuzz import fuzz

class MasterPatientIndex:
    """
    Master Patient Index (MPI) - Phase 4
    Deduplicates and links patient records across multiple hospitals using 
    probabilistic matching algorithms to create a single longitudinal health record.
    """
    
    def __init__(self):
        # In a real system, this is a highly optimized database table mapping Global ID -> Local IDs
        self.global_registry = []

    def calculate_match_score(self, new_patient, existing_patient):
        """
        Calculates a probabilistic match score between 0.0 and 1.0.
        """
        score = 0.0
        weights = {
            "aadhaar": 0.50, # National ID is a very strong indicator
            "phone": 0.25,
            "dob": 0.15,
            "name": 0.10
        }
        
        # 1. Aadhaar Match (Highest confidence)
        if new_patient.get("national_id") and existing_patient.get("national_id"):
            if str(new_patient["national_id"]) == str(existing_patient["national_id"]):
                score += weights["aadhaar"]
                
        # 2. Phone Match
        if new_patient.get("phone") and existing_patient.get("phone"):
            if str(new_patient["phone"]) == str(existing_patient["phone"]):
                score += weights["phone"]
                
        # 3. DOB Match
        if new_patient.get("dob") and existing_patient.get("dob"):
            if new_patient["dob"] == existing_patient["dob"]:
                score += weights["dob"]
                
        # 4. Name Match (Fuzzy logic using token_sort_ratio)
        # This handles reordering, e.g., "Rahul Sharma" vs "Sharma, Rahul"
        new_full_name = f"{new_patient.get('first_name', '')} {new_patient.get('last_name', '')}".lower()
        existing_full_name = f"{existing_patient.get('first_name', '')} {existing_patient.get('last_name', '')}".lower()
        
        name_match_percent = fuzz.token_sort_ratio(new_full_name, existing_full_name)
        score += weights["name"] * (name_match_percent / 100.0)
            
        return score

    def link_patient(self, new_patient_record):
        """
        Takes a new patient record and decides whether to link it to an existing
        Global ID (e.g., ABHA ID) or create a new one.
        """
        THRESHOLD = 0.85 # Needs high confidence to automatically link without human review
        
        best_match_id = None
        highest_score = 0.0
        
        # Scan existing registry for matches
        for global_id, existing_record in self.global_registry:
            score = self.calculate_match_score(new_patient_record, existing_record)
            if score > highest_score:
                highest_score = score
                best_match_id = global_id
                
        # If score exceeds threshold, link them together!
        if highest_score >= THRESHOLD:
            return best_match_id, highest_score
        else:
            # Create a new Global ID (simulating the generation of a new ABHA address)
            new_global_id = f"ABHA-{str(uuid.uuid4())[:8].upper()}"
            self.global_registry.append((new_global_id, new_patient_record))
            return new_global_id, highest_score

if __name__ == "__main__":
    # Let's simulate receiving records from two different hospitals for the same person
    
    # 1. Rahul visits Apollo Hospital
    record_hospital_a = {
        "patient_id": "APO-100",
        "first_name": "Rahul",
        "last_name": "Sharma",
        "dob": "1985-03-12",
        "phone": "+919876543210",
        "national_id": "123456789012"
    }
    
    # 2. A month later, he visits Fortis. Notice his name is recorded differently!
    record_hospital_b = {
        "patient_id": "FOR-999",
        "first_name": "R.", # Slight name variation
        "last_name": "Sharma",
        "dob": "1985-03-12",
        "phone": "+919876543210",
        "national_id": "123456789012"
    }
    
    mpi = MasterPatientIndex()
    
    print("--- Running Master Patient Index (MPI) Deduplication ---")
    
    # Process first record
    global_id_1, score_1 = mpi.link_patient(record_hospital_a)
    print(f"\n[Hospital A] Received record for 'Rahul Sharma' (ID: APO-100).")
    print(f"-> Assigned Global ID: {global_id_1}")
    
    # Process second record (should confidently link to the first one)
    global_id_2, score_2 = mpi.link_patient(record_hospital_b)
    print(f"\n[Hospital B] Received record for 'R. Sharma' (ID: FOR-999).")
    print(f"-> Match Score calculated: {score_2:.2f}/1.0")
    print(f"-> Linked to existing Global ID: {global_id_2}")
    
    if global_id_1 == global_id_2:
        print("\n✅ SUCCESS: MPI correctly linked records from two different siloed hospitals to the same longitudinal patient record!")
