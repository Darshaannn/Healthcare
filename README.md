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

### 6. FastAPI Backend System (Phase 6)
- **Integration**: `main.py` ties all engines into a cohesive HTTP API.
- **Persistence**: `database.py` adds PostgreSQL persistence for MPI mappings and Consents.
- **Endpoints**: `/ingest` (CSV to FHIR), `/consent/grant`, and `/patient/{id}/records`.

## 🚀 Getting Started

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend System**:
   ```bash
   python main.py
   ```

4. **API Interaction**:
   - Visit `http://localhost:8000/docs` for the interactive Swagger documentation.
   - Upload `simulated_hospital_data.csv` to `/ingest`.

## 🛠️ Next Steps
- [ ] Implement **Real JWT Authentication** (OAuth2 with password flow).
- [ ] Build a **Clinical Decision Support (CDS)** engine for Drug-Drug Interaction alerts.
- [ ] Implement the **React-based Patient Consent Dashboard**.
