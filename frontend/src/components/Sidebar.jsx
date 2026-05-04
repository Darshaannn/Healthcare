import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, Activity, Pill, ShieldCheck, User } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>UHR Platform</h2>
        <p>Unified Health Records</p>
      </div>
      <div className="nav-links">
        <NavLink to="/search" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
          <Search size={18} /> Patient search
        </NavLink>
        <NavLink to="/timeline" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
          <Activity size={18} /> Health timeline
        </NavLink>
        <NavLink to="/prescriptions" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
          <Pill size={18} /> Prescriptions
        </NavLink>
        <NavLink to="/consents" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
          <ShieldCheck size={18} /> Consent hub
        </NavLink>
      </div>
      <div className="sidebar-footer">
        <div className="avatar" style={{width: '36px', height: '36px'}}>
          <User size={18} />
        </div>
        <div>
          <div style={{fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Logged in as</div>
          <strong style={{color: 'white', display: 'block', margin: '2px 0'}}>Dr. Sharma</strong>
          <span style={{fontSize: '0.8rem'}}>Apollo Mumbai</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
