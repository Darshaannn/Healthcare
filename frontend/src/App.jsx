import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import PatientSearch from './pages/PatientSearch';
import HealthTimeline from './pages/HealthTimeline';
import Prescriptions from './pages/Prescriptions';
import ConsentHub from './pages/ConsentHub';

import './index.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/search" element={<PatientSearch />} />
            <Route path="/timeline" element={<HealthTimeline />} />
            <Route path="/prescriptions" element={<Prescriptions />} />
            <Route path="/consents" element={<ConsentHub />} />
            <Route path="*" element={<Navigate to="/search" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
