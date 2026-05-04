import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mpi_engine import MasterPatientIndex
from terminology_engine import TerminologyEngine
from consent_engine import ConsentEngine

def test_mpi_same_aadhaar_links():
    mpi = MasterPatientIndex()
    # Our MPI links by returning deterministic global ID based on match logic
    id1, _ = mpi.link_patient({"patient_id": "P001", "name": "Rahul Sharma", "phone": "9876543210"})
    id2, _ = mpi.link_patient({"patient_id": "P001", "name": "Rahul Sharma", "phone": "9876543210"})
    assert id1 == id2

def test_terminology_maps_dng001():
    engine = TerminologyEngine()
    result = engine.map_code("DNG-001", "Dengue Fever")
    assert result["icd10_code"] == "A90"

def test_consent_expired_rejected():
    engine = ConsentEngine()
    artefact = engine.generate_consent_artefact("ABHA-1", "DOC-1", "Care", -1, ["Condition"])
    valid, msg = engine.verify_consent(artefact["consent_id"], "DOC-1", "Condition")
    assert valid == False
