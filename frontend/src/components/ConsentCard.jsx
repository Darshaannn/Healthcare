import React from 'react';
import { ShieldCheck, Clock, CheckCircle } from 'lucide-react';

const ConsentCard = ({ patient, status, details }) => {
  const isPending = status === 'Pending';
  return (
    <div className="patient-card">
      <div className="patient-info">
        <div style={{width: '48px', height: '48px', borderRadius: '50%', backgroundColor: isPending ? 'var(--bg-yellow-light)' : 'var(--bg-green-light)', color: isPending ? 'var(--accent-yellow)' : 'var(--accent-green)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <ShieldCheck size={24} />
        </div>
        <div className="patient-details">
          <h3 style={{color: 'white', margin: '0 0 6px 0', fontSize: '1.1rem'}}>{patient}</h3>
          <p style={{margin: 0, color: 'var(--text-secondary)', fontSize: '0.95rem'}}>{details}</p>
        </div>
      </div>
      <div>
        {isPending ? (
          <span className="badge warning"><Clock size={14} /> Consent pending</span>
        ) : (
          <span className="badge success"><CheckCircle size={14} /> Consent active</span>
        )}
      </div>
    </div>
  );
};

export default ConsentCard;
