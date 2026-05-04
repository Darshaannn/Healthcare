import pytest
from mpi_engine import MasterPatientIndex

@pytest.fixture
def mpi():
    return MasterPatientIndex()

def test_exact_match(mpi):
    """Test that two identical records yield a 100% match score."""
    patient_a = {
        "first_name": "Rahul", "last_name": "Sharma",
        "dob": "1985-03-12", "phone": "+919876543210", "national_id": "123456789012"
    }
    patient_b = patient_a.copy()
    
    score = mpi.calculate_match_score(patient_a, patient_b)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_fuzzy_name_match(mpi):
    """Test that reversed names (common in India) still match highly."""
    patient_a = {
        "first_name": "Rahul", "last_name": "Sharma",
        "dob": "1985-03-12", "phone": "+919876543210", "national_id": "123456789012"
    }
    patient_b = {
        "first_name": "Sharma", "last_name": "Rahul", # Reversed
        "dob": "1985-03-12", "phone": "+919876543210", "national_id": "123456789012"
    }
    
    score = mpi.calculate_match_score(patient_a, patient_b)
    # Thefuzz token_sort_ratio should handle this perfectly
    assert score > 0.95, f"Expected > 0.95, got {score}"

def test_missing_aadhaar_but_strong_match(mpi):
    """Test that missing national_id but matching phone/dob/name still links."""
    patient_a = {
        "first_name": "Priya", "last_name": "Patel",
        "dob": "1990-07-25", "phone": "+919123456789", "national_id": "987654321098"
    }
    patient_b = {
        "first_name": "Priya", "last_name": "Patel",
        "dob": "1990-07-25", "phone": "+919123456789", "national_id": None # Missing Aadhaar
    }
    
    score = mpi.calculate_match_score(patient_a, patient_b)
    # Score should be 0.25 (phone) + 0.15 (dob) + 0.10 (name) = 0.50
    assert score == 0.50, f"Expected 0.50, got {score}"

def test_link_patient_flow(mpi):
    """Test the end-to-end linking and Global ID assignment."""
    patient_a = {
        "first_name": "Amit", "last_name": "Singh",
        "dob": "1978-11-05", "phone": "+919988776655", "national_id": "456789012345"
    }
    patient_b = {
        "first_name": "Amit", "last_name": "S.",
        "dob": "1978-11-05", "phone": "+919988776655", "national_id": "456789012345"
    }
    
    global_id_1, _ = mpi.link_patient(patient_a)
    global_id_2, score = mpi.link_patient(patient_b)
    
    assert global_id_1 == global_id_2, "MPI failed to link records with strong Aadhaar match."
    assert global_id_1.startswith("ABHA-")
