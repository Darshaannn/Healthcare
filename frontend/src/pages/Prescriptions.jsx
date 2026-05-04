import React, { useState, useEffect } from 'react';
import DDIAlert from '../components/DDIAlert';
import { Pill, Search, Plus } from 'lucide-react';
import { checkInteraction } from '../api/client';

const Prescriptions = () => {
  const [medication, setMedication] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [isChecking, setIsChecking] = useState(false);
  
  // Hardcoded patient meds for now as requested
  const activeMeds = ["Warfarin 5mg", "Metformin 500mg"];

  useEffect(() => {
    const checkDDI = async () => {
      if (!medication) {
        setAlerts([]);
        return;
      }
      setIsChecking(true);
      try {
        const res = await checkInteraction({
          active_medications: activeMeds,
          new_drug: medication
        });
        setAlerts(res.data.alerts || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsChecking(false);
      }
    };

    const timer = setTimeout(() => {
      checkDDI();
    }, 500);

    return () => clearTimeout(timer);
  }, [medication]);

  const hasCritical = alerts.some(a => a.severity === 'CRITICAL');

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
        
        {alerts.map((alert, idx) => (
          <DDIAlert 
            key={idx}
            message={`Interaction with ${alert.pair.join(' and ')}: ${alert.message}`} 
          />
        ))}
        
        <div style={{display: 'flex', justifyContent: 'flex-end'}}>
          <button className={`btn ${hasCritical ? 'btn' : 'btn-primary'}`} style={hasCritical ? {backgroundColor: 'var(--bg-red-light)', color: 'var(--text-red)', borderColor: 'rgba(239, 68, 68, 0.2)'} : {}}>
            {isChecking ? 'Checking...' : 'Prescribe Medication'}
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
