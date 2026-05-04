import csv
import json
from datetime import datetime

class HospitalDataParser:
    """
    Hospital Connector SDK - Phase 2
    This reads dirty hospital exports (CSV) and transforms them into our standard
    internal 'Lingua Franca' object model, preparing it for FHIR mapping.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.normalized_records = []

    def clean_aadhaar(self, raw_aadhaar):
        """Removes spaces and validates length of Aadhaar."""
        if not raw_aadhaar:
            return None
        clean = str(raw_aadhaar).replace(" ", "").strip()
        return clean if len(clean) == 12 else None
        
    def normalize_date(self, date_str, is_dob=False):
        """Converts DD-MM-YYYY or ISO formats to standard ISO 8601 (FHIR format)."""
        try:
            if is_dob:
                return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
            else:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+05:30")
        except Exception as e:
            return None

    def parse(self):
        """Reads the dirty CSV and creates a clean internal object model."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # 1. Demographics Model
                patient_model = {
                    "patient_id": row["PatientID"].strip(),
                    "source_hospital": row["Hospital_Name"].strip(),
                    "first_name": row["FirstName"].strip(),
                    "last_name": row["LastName"].strip(),
                    "dob": self.normalize_date(row["DOB"], is_dob=True),
                    "gender": row["Gender"].strip().upper(),
                    "phone": row["Phone"].strip(),
                    "national_id": self.clean_aadhaar(row["Aadhaar"])
                }
                
                # 2. Clinical Encounter Model
                encounter_model = {
                    "visit_date": self.normalize_date(row["VisitDate"]),
                    "raw_diagnosis_code": row["DiagCode"].strip(),
                    "raw_diagnosis_desc": row["DiagDesc"].strip(),
                    "medication_prescribed": row["Medication"].strip()
                }
                
                # Combine into our "Lingua Franca" Object
                self.normalized_records.append({
                    "patient": patient_model,
                    "encounter": encounter_model
                })
                
        return self.normalized_records

    def export_json(self, output_path):
        with open(output_path, 'w') as f:
            json.dump(self.normalized_records, f, indent=4)

if __name__ == "__main__":
    print("Starting Hospital Data Parsing...")
    parser = HospitalDataParser('simulated_hospital_data.csv')
    records = parser.parse()
    
    print(f"Successfully parsed and normalized {len(records)} records.")
    
    # Save output to see the internal model
    parser.export_json('internal_normalized_model.json')
    print("Exported standard format to internal_normalized_model.json")
