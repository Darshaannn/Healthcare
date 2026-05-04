import React from 'react';
import ConsentCard from '../components/ConsentCard';
import { Plus } from 'lucide-react';

const ConsentHub = () => {
  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div className="header-bar">
        <h1>Consent hub</h1>
      </div>
      <p style={{color: 'var(--text-secondary)', marginBottom: '32px', fontSize: '1.05rem'}}>Manage data access requests directly through the ABDM Gateway.</p>
      
      <div style={{marginBottom: '40px'}}>
        <button className="btn btn-primary"><Plus size={18} /> Request New Consent</button>
      </div>

      <div className="section-label">ACTIVE & PENDING REQUESTS</div>
      <ConsentCard 
        patient="Rahul Sharma (ABHA-4829)" 
        status="Active" 
        details="Granted access to Conditions and Medications until May 05, 2026."
      />
      <ConsentCard 
        patient="Amit Kumar (ABHA-3310)" 
        status="Pending" 
        details="Requested access for upcoming surgery consultation."
      />
    </div>
  );
};

export default ConsentHub;
