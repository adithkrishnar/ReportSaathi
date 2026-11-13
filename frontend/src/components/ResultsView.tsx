import React from 'react';
import { AlertOctagon, Info, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';
import { ReportResult, BiomarkerValue, RedFlagAlert } from '../types';

interface ResultsViewProps {
  report: ReportResult;
}

export const ResultsView: React.FC<ResultsViewProps> = ({ report }) => {
  return (
    <div>
      {/* 1. CRITICAL RED-FLAG ALERT BANNER (If Any) */}
      {report.red_flags && report.red_flags.length > 0 && (
        <div className="emergency-banner" role="alert">
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
            <AlertOctagon size={28} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '0.02em', textTransform: 'uppercase' }}>
                URGENT EMERGENCY ALERT
              </h3>
              <p style={{ fontSize: '14px', marginTop: '4px', opacity: 0.95 }}>
                One or more critical lab measurements require immediate emergency medical evaluation:
              </p>
              <ul style={{ marginTop: '10px', marginLeft: '20px', fontSize: '14px' }}>
                {report.red_flags.map((rf: RedFlagAlert, idx: number) => (
                  <li key={idx} style={{ marginBottom: '6px' }}>
                    <strong>{rf.biomarker} ({rf.value} {rf.unit}):</strong> {rf.message}
                  </li>
                ))}
              </ul>
              <div style={{ marginTop: '12px', padding: '10px 14px', backgroundColor: 'rgba(0, 0, 0, 0.25)', borderRadius: '6px', fontSize: '13px', fontWeight: 600 }}>
                Please proceed directly to the nearest hospital emergency room or contact your emergency doctor immediately.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. SUMMARY CARD */}
      <div className="card">
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
          Report Explanation Summary
        </h2>
        <p style={{ fontSize: '15px', color: '#334155', lineHeight: '1.6' }}>
          {report.summary}
        </p>
      </div>

      {/* 3. BIOMARKER DETAILS GRID */}
      <div className="card">
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', marginBottom: '16px' }}>
          Laboratory Parameters & Understandable Explanations
        </h3>
        <div style={{ display: 'grid', gap: '16px' }}>
          {report.biomarkers.map((b: BiomarkerValue, idx: number) => {
            let statusIcon = <CheckCircle2 size={18} style={{ color: '#16a34a' }} />;
            if (b.status === 'needs_attention') {
              statusIcon = <AlertTriangle size={18} style={{ color: '#dc2626' }} />;
            } else if (b.status === 'borderline') {
              statusIcon = <AlertTriangle size={18} style={{ color: '#d97706' }} />;
            } else if (b.status === 'no_range_on_report') {
              statusIcon = <HelpCircle size={18} style={{ color: '#64748b' }} />;
            }

            return (
              <div
                key={idx}
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '16px',
                  backgroundColor: '#ffffff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {statusIcon}
                    <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>{b.name}</h4>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                      {b.value} {b.unit}
                    </span>
                    <span className={`badge badge-${b.status.replace(/_/g, '-')}`}>
                      {b.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>

                <div style={{ marginTop: '10px', fontSize: '13px', color: '#64748b' }}>
                  <strong>Report Reference Range: </strong>
                  {b.reference_low !== null && b.reference_low !== undefined && b.reference_high !== null && b.reference_high !== undefined
                    ? `${b.reference_low} - ${b.reference_high} ${b.unit}`
                    : 'None printed on report (Doctor consultation required)'}
                </div>

                {b.explanation && (
                  <div style={{ marginTop: '10px', fontSize: '14px', color: '#334155', backgroundColor: '#f8fafc', padding: '10px 14px', borderRadius: '6px' }}>
                    <Info size={16} style={{ display: 'inline', verticalAlign: '-3px', marginRight: '6px', color: '#2563eb' }} />
                    {b.explanation}
                  </div>
                )}

                {b.interpretation && (
                  <p style={{ marginTop: '8px', fontSize: '13px', color: '#475569', fontStyle: 'italic' }}>
                    {b.interpretation}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

