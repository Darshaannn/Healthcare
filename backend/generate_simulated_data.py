import csv
import random
from datetime import datetime, timedelta

def generate_indian_data(num_records=100):
    first_names = ["Rahul", "Priya", "Amit", "Neha", "Rohan", "Sneha", "Vikram", "Anjali", "Suresh", "Kavita", "Aditya", "Riya"]
    last_names = ["Sharma", "Patel", "Singh", "Gupta", "Kumar", "Desai", "Joshi", "Verma", "Reddy", "Iyer", "Nair", "Das"]
    
    # We want some 'dirty' terminology mappings as described in your prompt
    # Mix of ICD-10, SNOMED, free-text, and internal hospital codes to train our adapter later
    diagnoses = [
        ("DNG-001", "Dengue Fever"), # Proprietary internal code
        ("A90", "Dengue fever [classical dengue]"), # Official ICD-10
        ("dengue", "dengue"), # Unstructured free text
        ("TYP-101", "Typhoid"), 
        ("A01.0", "Typhoid fever"),
        ("hypertension", "hypertension"),
        ("I10", "Essential (primary) hypertension"),
        ("DM2", "Type 2 Diabetes Mellitus"),
        ("E11.9", "Type 2 diabetes mellitus without complications")
    ]
    
    hospitals = ["Apollo Delhi", "Fortis Mumbai", "Max Healthcare", "AIIMS"]
    
    # Simulating a messy CSV export from a legacy hospital EHR
    with open('simulated_hospital_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "PatientID", "Hospital_Name", "FirstName", "LastName", "DOB", "Gender", 
            "Phone", "Aadhaar", "VisitDate", "DiagCode", "DiagDesc", "Medication"
        ])
        
        for _ in range(num_records):
            hospital = random.choice(hospitals)
            pid = f"{hospital[:3].upper()}-{random.randint(10000, 99999)}"
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            
            # Random DOB
            dob = (datetime(1950, 1, 1) + timedelta(days=random.randint(0, 25000))).strftime("%d-%m-%Y")
            gender = random.choice(["M", "F"])
            phone = f"+91{random.randint(9000000000, 9999999999)}"
            aadhaar = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
            
            # Random recent visit date
            visit = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%dT%H:%M:%S")
            
            diag = random.choice(diagnoses)
            meds = random.choice(["Paracetamol 500mg", "Amoxicillin 250mg", "Metformin 500mg", "Amlodipine 5mg", "None"])
            
            writer.writerow([pid, hospital, fname, lname, dob, gender, phone, aadhaar, visit, diag[0], diag[1], meds])

if __name__ == "__main__":
    generate_indian_data(100)
    print("Successfully generated simulated_hospital_data.csv with 100 messy hospital records!")
