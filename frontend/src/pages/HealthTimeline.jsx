import React from 'react';
import TimelineCard from '../components/TimelineCard';

const HealthTimeline = () => {
  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div className="header-bar">
        <h1>Health timeline</h1>
      </div>
      <p style={{color: 'var(--text-secondary)', marginBottom: '40px', fontSize: '1.05rem'}}>Longitudinal view of the patient's unified record.</p>
      
      <div style={{marginLeft: '10px'}}>
        <TimelineCard 
          date="August 12, 2025" 
          title="Diagnosis: Dengue Fever" 
          description="Recorded at Apollo Delhi. Patient presented with high fever and joint pain."
        />
        <TimelineCard 
          date="January 10, 2024" 
          title="Prescription: Warfarin 5mg" 
          description="Prescribed by Dr. Patel at Fortis Mumbai for atrial fibrillation."
        />
        <TimelineCard 
          date="November 05, 2023" 
          title="Lab Result: HbA1c 6.2%" 
          description="Routine blood work. Borderline pre-diabetic."
        />
      </div>
    </div>
  );
};

export default HealthTimeline;
