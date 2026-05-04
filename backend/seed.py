import os
import requests
import json

from generate_simulated_data import generate_hospital_data
from parser_sdk import HospitalDataParser
from terminology_engine import TerminologyEngine, FhirTransformer
from mpi_engine import MasterPatientIndex

def seed_database():
    print("🚀 Starting Database Seed Process...")

    # 1. Generate Data
    csv_path = "simulated_hospital_data.csv"
    if not os.path.exists(csv_path):
        print(f"Generating simulated data to {csv_path}...")
        generate_hospital_data(10, csv_path)
    
    # 2. Parse Data
    print("Parsing CSV data...")
    parser = HospitalDataParser(csv_path)
    records = parser.parse()
    
    # 3. Terminology & FHIR Transformation
    print("Mapping terminology and transforming to FHIR...")
    terminology = TerminologyEngine()
    transformer = FhirTransformer(terminology)
    mpi = MasterPatientIndex()
    
    hapi_url = os.getenv("HAPI_FHIR_URL", "http://localhost:8080/fhir")
    
    success_count = 0
    for record in records:
        # Generate global ID
        global_id, _ = mpi.link_patient(record["patient"])
        
        # Transform to FHIR Bundle
        fhir_bundle = transformer.to_fhir_bundle([record])
        
        # 4. Post to HAPI FHIR
        try:
            res = requests.post(
                hapi_url, 
                json=fhir_bundle, 
                headers={"Content-Type": "application/fhir+json"}
            )
            if res.status_code in [200, 201]:
                success_count += 1
                print(f"✅ Successfully posted patient {global_id} to FHIR server.")
            else:
                print(f"❌ Failed to post {global_id}: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"⚠️ Could not connect to HAPI FHIR server at {hapi_url}. Is Docker running?")
            break
            
    print(f"🏁 Seeding complete! {success_count} records processed.")

if __name__ == "__main__":
    seed_database()
