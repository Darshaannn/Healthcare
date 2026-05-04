import React from 'react';
import { AlertOctagon } from 'lucide-react';

const DDIAlert = ({ message }) => {
  return (
    <div style={{
      backgroundColor: 'var(--bg-red-light)',
      color: 'var(--text-red)',
      padding: '16px 20px',
      borderRadius: 'var(--radius-md)',
      border: '1px solid rgba(239, 68, 68, 0.2)',
      borderLeft: '4px solid var(--accent-red)',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px'
    }}>
      <AlertOctagon size={24} style={{flexShrink: 0, marginTop: '2px'}} />
      <div>
        <strong style={{display: 'block', fontSize: '1rem', marginBottom: '4px'}}>Severe Drug Interaction Detected</strong>
        <p style={{margin: '0', fontSize: '0.95rem', lineHeight: '1.5', color: '#fca5a5'}}>{message}</p>
      </div>
    </div>
  );
};

export default DDIAlert;
