import React, { useState, useEffect } from 'react';
import { searchPatients } from '../api/client';
import { Search, ChevronRight, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const mockPatients = [
  { id: 'ABHA-4829', name: 'Rahul Sharma', initials: 'RS', dob: '12/03/1985', hospitals: 'Apollo Delhi + Fortis Mumbai', status: 'DDI alert' },
  { id: 'ABHA-7721', name: 'Priya Patel', initials: 'PP', dob: '25/07/1990', hospitals: 'Fortis Mumbai', status: 'Consent active' },
  { id: 'ABHA-3310', name: 'Amit Kumar', initials: 'AK', dob: '08/11/1972', hospitals: 'Max Healthcare + AIIMS', status: 'Consent pending' },
  { id: 'ABHA-9102', name: 'Neha Verma', initials: 'NV', dob: '14/02/1998', hospitals: 'Apollo Delhi', status: 'No consent' },
];

const getStatusBadge = (status) => {
  switch(status) {
    case 'DDI alert': return <span className="badge danger"><AlertTriangle size={14} /> {status}</span>;
    case 'Consent active': return <span className="badge success"><CheckCircle size={14} /> {status}</span>;
    case 'Consent pending': return <span className="badge warning"><Clock size={14} /> {status}</span>;
    default: return <span className="badge neutral">{status}</span>;
  }
};

const PatientSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(mockPatients);

  useEffect(() => {
    if(query) {
      setResults(mockPatients.filter(p => p.name.toLowerCase().includes(query.toLowerCase())));
    } else {
      setResults(mockPatients);
    }
  }, [query]);

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div className="header-bar">
        <h1>Patient search</h1>
        <div className="doctor-profile">
          <div className="avatar">DS</div>
          <span>DOC-SHARMA-001</span>
        </div>
      </div>
      
      <div className="search-bar">
        <div className="search-icon-wrapper">
          <Search size={20} />
        </div>
        <input 
          type="text" 
          className="search-input" 
          placeholder="Search by name, ABHA ID, Aadhaar, or phone..." 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-primary">Search <ChevronRight size={16} /></button>
      </div>

      <div className="results-container">
        <div className="section-label">RESULTS</div>
        {results.map((patient, idx) => (
          <div className={`patient-card ${idx === 0 ? 'selected' : ''}`} key={patient.id}>
            <div className="patient-info">
              <div className="patient-avatar">{patient.initials}</div>
              <div className="patient-details">
                <h3>{patient.name}</h3>
                <p>{patient.id} &nbsp;·&nbsp; DOB {patient.dob} &nbsp;·&nbsp; {patient.hospitals}</p>
              </div>
            </div>
            <div>
              {getStatusBadge(patient.status)}
            </div>
          </div>
        ))}
        
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '32px', paddingBottom: '32px'}}>
          <span style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>Showing {results.length} of 127 patients</span>
          <div style={{display: 'flex', gap: '8px'}}>
            <button className="btn">Previous</button>
            <button className="btn" style={{backgroundColor: 'var(--bg-card-hover)', borderColor: 'var(--border-color)', color: 'white'}}>1</button>
            <button className="btn">2</button>
            <button className="btn">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientSearch;
