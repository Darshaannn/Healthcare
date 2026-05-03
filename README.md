# Unified Health Records (UHR) Platform

A comprehensive system architecture for a Unified Health Records platform built on FHIR R4 and ABDM (Ayushman Bharat Digital Mission) principles.

## 🏗️ Project Architecture

This project implements a multi-layered health data interoperability stack:

### 1. Infrastructure (Phase 1)
- **HAPI FHIR Server**: Open-source FHIR store.
- **PostgreSQL**: Reliable backend for the FHIR server.
- Configured via `docker-compose.yml`.

### 2. Hospital Connector SDK (Phase 2)
- **Parser**: Converts messy hospital EHR exports (CSV/HL7) into a normalized internal "Lingua Franca" model.
- Includes `parser_sdk.py` and sample `simulated_hospital_data.csv`.

### 3. Terminology Engine (Phase 3)
- **Standardization**: Maps proprietary hospital codes (e.g., `DNG-001`) and free-text to official **ICD-10 / SNOMED CT** codes.
- **FHIR Transformer**: Generates valid FHIR R4 JSON bundles.

### 4. Master Patient Index - MPI (Phase 4)
- **Deduplication**: Uses probabilistic matching (Aadhaar, Phone, DOB, Name) to link records from different hospitals to a single Global ABHA ID.

### 5. Consent Engine & API Gateway (Phase 5)
- **Trust Layer**: Enforces patient-owned data access.
- **API Gateway**: Intercepts FHIR requests and validates time-limited, purpose-specific consent tokens before releasing data.

## 🚀 Getting Started

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d
   ```

2. **Generate Sample Data**:
   ```bash
   python generate_simulated_data.py
   ```

3. **Run the Adapter Pipeline**:
   ```bash
   python parser_sdk.py
   python terminology_engine.py
   ```

4. **Test Security**:
   ```bash
   python api_gateway.py
   ```

## 🛠️ Next Steps
- [ ] Implement a React-based Patient Consent Dashboard.
- [ ] Build a Clinical Decision Support (CDS) engine for Drug-Drug Interaction alerts.
- [ ] Integrate with official ABDM Sandbox APIs.
