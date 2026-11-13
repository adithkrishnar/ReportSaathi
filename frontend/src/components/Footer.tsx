import React from 'react';
import { Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="disclaimer-bar">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
        <Shield size={16} style={{ color: '#60a5fa' }} />
        <span>This explains your report. It does not replace your doctor.</span>
      </div>
    </footer>
  );
};

