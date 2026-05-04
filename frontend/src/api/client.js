import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Mocked doctor for frontend testing
const doctor_id = 'DOC-SHARMA-001';

// The exact API calls specified by the user
export const searchPatients = (q) => api.get(`/patients?q=${q}`);
export const getHealthTimeline = (abha_id) => api.get(`/fhir/Patient/${abha_id}/everything`);
export const getActiveMedications = (abha_id) => api.get(`/fhir/MedicationRequest?patient=${abha_id}`);
export const submitPrescription = (abha_id, payload) => api.post(`/fhir/MedicationRequest`, payload);

export const getConsents = () => api.get(`/consent?doctor_id=${doctor_id}`);
export const grantConsent = (payload) => api.post(`/consent/grant`, payload);
export const revokeConsent = (consent_id) => api.delete(`/consent/${consent_id}`);

export default api;
