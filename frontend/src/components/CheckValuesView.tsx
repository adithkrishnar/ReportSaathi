import React, { useState } from 'react';
import { AlertTriangle, Edit3, ArrowRight, RefreshCw } from 'lucide-react';
import { BiomarkerValue, RedFlagAlert } from '../types';

interface CheckValuesViewProps {
  documentId: string;
  rawText: string;
  biomarkers: BiomarkerValue[];
  redFlags: RedFlagAlert[];
  requiresVerification: boolean;
  onProceedToExplanation: () => void;
  onApplyCorrections: (correctedText: string) => Promise<void>;
  isProcessing: boolean;
}

export const CheckValuesView: React.FC<CheckValuesViewProps> = ({
  rawText,
  biomarkers,
  redFlags,
  requiresVerification,
  onProceedToExplanation,
  onApplyCorrections,
  isProcessing,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(rawText);
  const [savingCorrections, setSavingCorrections] = useState(false);

  const handleSave = async () => {
    setSavingCorrections(true);
    try {
      await onApplyCorrections(editedText);
      setIsEditing(false);
    } finally {
      setSavingCorrections(false);
    }
  };

  const hasZeroValues = biomarkers.length === 0;

  return (
    <div className="card no-print">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>
            Step 2: Review Extracted Laboratory Information
          </h2>
          <p style={{ fontSize: '13px', color: '#64748b' }}>
            Verify the test values extracted from your report before generating the plain-language explanation.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => {
            setIsEditing(!isEditing);
            setEditedText(rawText);
          }}
        >
          <Edit3 size={16} />
          {isEditing ? 'Cancel Editing' : 'Edit / Correct Text'}
        </button>
      </div>

      {requiresVerification && (
        <div
          style={{
            marginBottom: '16px',
            padding: '12px 16px',
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: '8px',
            color: '#b45309',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '14px',
          }}
        >
          <AlertTriangle size={20} />
          <span>
            <strong>Verification Recommended:</strong> Some characters in your report scan were unclear or slightly blurry. Please review the values carefully.
          </span>
        </div>
      )}

      {hasZeroValues && (
        <div
          style={{
            marginBottom: '20px',
            padding: '16px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            color: '#991b1b',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <AlertTriangle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontWeight: 600, fontSize: '15px' }}>No Laboratory Values Detected</h4>
            <p style={{ fontSize: '13px', marginTop: '4px' }}>
              The system could not identify any standard medical test names and numerical values from the uploaded image. Please ensure your image is a clear medical laboratory report, or click <strong>Edit / Correct Text</strong> to enter your test names and numbers manually.
            </p>
          </div>
        </div>
      )}

      {isEditing ? (
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
            Raw Report Text (Edit to correct any misread numbers or names):
          </label>
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={8}
            style={{
              width: '100%',
              padding: '12px',
              fontFamily: 'monospace',
              fontSize: '13px',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              outline: 'none',
              resize: 'vertical',
            }}
          />
          <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSave}
              disabled={savingCorrections || !editedText.trim()}
            >
              {savingCorrections ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  Updating...
                </>
              ) : (
                'Save & Re-evaluate'
              )}
            </button>
          </div>
        </div>
      ) : (
        !hasZeroValues && (
          <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: '#475569' }}>Test Name</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: '#475569' }}>Result</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: '#475569' }}>Printed Reference Range</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: '#475569' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {biomarkers.map((b, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 500, color: '#0f172a' }}>{b.name}</td>
                    <td style={{ padding: '12px 16px', fontWeight: 600 }}>{b.value} {b.unit}</td>
                    <td style={{ padding: '12px 16px', color: '#64748b' }}>
                      {b.reference_low !== null && b.reference_low !== undefined && b.reference_high !== null && b.reference_high !== undefined
                        ? `${b.reference_low} - ${b.reference_high} ${b.unit}`
                        : 'No range printed on report'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span className={`badge badge-${b.status.replace(/_/g, '-')}`}>
                        {b.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {redFlags.length > 0 && (
        <div style={{ marginBottom: '20px', padding: '14px', backgroundColor: '#fef2f2', border: '1px solid #f87171', borderRadius: '8px' }}>
          <p style={{ color: '#991b1b', fontWeight: 600, fontSize: '14px' }}>
            ⚠️ {redFlags.length} Critical Alert(s) Detected in this report.
          </p>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button
          type="button"
          className="btn btn-primary"
          onClick={onProceedToExplanation}
          disabled={isProcessing || hasZeroValues}
          style={{ minWidth: '180px' }}
        >
          {isProcessing ? 'Generating Explanation...' : 'Explain My Report'}
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
};

