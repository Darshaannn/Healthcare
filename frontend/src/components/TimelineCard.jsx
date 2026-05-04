import React from 'react';
import { Calendar, FileText, Pill, FlaskConical } from 'lucide-react';

const getIconForTitle = (title) => {
  if (title.includes('Diagnosis')) return <FileText size={16} color="var(--accent-blue)" />;
  if (title.includes('Prescription')) return <Pill size={16} color="var(--accent-green)" />;
  if (title.includes('Lab Result')) return <FlaskConical size={16} color="var(--accent-yellow)" />;
  return <FileText size={16} color="var(--accent-blue)" />;
};

const TimelineCard = ({ date, title, description }) => {
  return (
    <div style={{
      borderLeft: '2px solid var(--border-color)',
      paddingLeft: '32px',
      position: 'relative',
      marginBottom: '32px'
    }}>
      <div style={{
        position: 'absolute',
        left: '-16px',
        top: '0',
        width: '30px',
        height: '30px',
        borderRadius: '50%',
        backgroundColor: 'var(--bg-sidebar)',
        border: '2px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1
      }}>
        {getIconForTitle(title)}
      </div>
      <div style={{display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '500', marginBottom: '8px'}}>
        <Calendar size={14} /> {date}
      </div>
      <div className="card-container" style={{margin: 0, padding: '20px'}}>
        <h4 style={{margin: '0 0 8px 0', color: 'var(--text-primary)', fontSize: '1.05rem'}}>{title}</h4>
        <p style={{margin: '0', color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5'}}>{description}</p>
      </div>
    </div>
  );
};

export default TimelineCard;
