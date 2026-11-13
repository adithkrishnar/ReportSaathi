import React from 'react';
import { FileText } from 'lucide-react';
import { HealthStatus } from '../api';

interface HeaderProps {
  health: HealthStatus;
}

export const Header: React.FC<HeaderProps> = ({ health }) => {
  return (
    <header className="card no-print" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ background: '#2563eb', padding: '10px', borderRadius: '10px', color: 'white', display: 'flex' }}>
          <FileText size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>ReportSaathi</h1>
          <p style={{ fontSize: '13px', color: '#64748b' }}>Plain-language medical report and prescription explainer</p>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
        <span
          style={{
            display: 'inline-block',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: health.online ? '#16a34a' : '#dc2626',
          }}
        />
        <span style={{ color: health.online ? '#166534' : '#991b1b', fontWeight: 500 }}>
          {health.online ? 'Backend Connected' : 'Backend Offline'}
        </span>
      </div>
    </header>
  );
};

