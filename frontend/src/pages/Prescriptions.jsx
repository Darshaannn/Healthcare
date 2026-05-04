import React, { useState } from 'react';
import DDIAlert from '../components/DDIAlert';
import { Pill, Search, Plus } from 'lucide-react';

const Prescriptions = () => {
  const [medication, setMedication] = useState('');
  
  const isAspirinOrIbuprofen = medication.toLowerCase().includes('aspirin') || medication.toLowerCase().includes('ibuprofen');

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div className="header-bar">
        <h1>Prescriptions</h1>
      </div>
      
      <div className="card-container">
        <h3 style={{margin: '0 0 20px 0', color: 'white', display: 'flex', alignItems: 'center', gap: '8px'}}>
          <Plus size={20} color="var(--accent-blue)" /> New Prescription
        </h3>
        
        <div className="search-bar" style={{marginBottom: '20px'}}>
          <div className="search-icon-wrapper">
            <Search size={18} />
          </div>
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search medication database (e.g., aspirin)" 
            value={medication}
            onChange={(e) => setMedication(e.target.value)}
          />
        </div>
        
        {isAspirinOrIbuprofen && (
          <DDIAlert 
            message={`${medication} interacts with patient's existing Warfarin. High risk of major bleeding complications.`} 
          />
        )}
        
        <div style={{display: 'flex', justifyContent: 'flex-end'}}>
          <button className={`btn ${isAspirinOrIbuprofen ? 'btn' : 'btn-primary'}`} style={isAspirinOrIbuprofen ? {backgroundColor: 'var(--bg-red-light)', color: 'var(--text-red)', borderColor: 'rgba(239, 68, 68, 0.2)'} : {}}>
            Prescribe Medication
          </button>
        </div>
      </div>
      
      <div style={{marginTop: '40px'}}>
        <div className="section-label">ACTIVE MEDICATIONS</div>
        
        <div className="patient-card" style={{cursor: 'default', flexDirection: 'column', alignItems: 'flex-start', padding: '20px'}}>
          <div style={{display: 'flex', alignItems: 'flex-start', gap: '16px', width: '100%'}}>
            <div style={{width: '40px', height: '40px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-blue-light)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <Pill size={20} />
            </div>
            <div style={{flexGrow: 1}}>
              <h4 style={{margin: '0 0 6px 0', color: 'white', fontSize: '1.1rem'}}>Warfarin 5mg</h4>
              <p style={{margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem'}}>Prescribed Jan 10, 2024 &nbsp;·&nbsp; Fortis Mumbai</p>
            </div>
            <div className="badge neutral">Active</div>
          </div>
        </div>

        <div className="patient-card" style={{cursor: 'default', flexDirection: 'column', alignItems: 'flex-start', padding: '20px'}}>
          <div style={{display: 'flex', alignItems: 'flex-start', gap: '16px', width: '100%'}}>
            <div style={{width: '40px', height: '40px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-blue-light)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <Pill size={20} />
            </div>
            <div style={{flexGrow: 1}}>
              <h4 style={{margin: '0 0 6px 0', color: 'white', fontSize: '1.1rem'}}>Metformin 500mg</h4>
              <p style={{margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem'}}>Prescribed Nov 06, 2023 &nbsp;·&nbsp; Apollo Delhi</p>
            </div>
            <div className="badge neutral">Active</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prescriptions;
