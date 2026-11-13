import React from 'react';
import { MessageSquare } from 'lucide-react';

interface DoctorQuestionsViewProps {
  questions: string[];
}

export const DoctorQuestionsView: React.FC<DoctorQuestionsViewProps> = ({ questions }) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{ background: '#ecfdf5', color: '#059669', padding: '8px', borderRadius: '8px' }}>
          <MessageSquare size={20} />
        </div>
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
            Recommended Questions for Your Doctor
          </h3>
          <p style={{ fontSize: '13px', color: '#64748b' }}>
            Take this list to your next consultation or pharmacist visit to get clear answers.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {questions.map((q, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              padding: '12px 14px',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
            }}
          >
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '24px',
                height: '24px',
                backgroundColor: '#2563eb',
                color: 'white',
                fontSize: '12px',
                fontWeight: 600,
                borderRadius: '50%',
                flexShrink: 0,
              }}
            >
              {idx + 1}
            </span>
            <span style={{ fontSize: '14px', color: '#1e293b', fontWeight: 500, lineHeight: '1.5' }}>
              {q}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

