import React, { useRef, useState } from 'react';
import { Upload, FileText, AlertCircle, Play } from 'lucide-react';
import sampleReportData from '../../../shared/sample-report.json';
import { ReportResult } from '../types';

interface UploadViewProps {
  onUploadSuccess: (docId: string, filename: string) => void;
  onLoadSample: (sampleData: ReportResult) => void;
  isUploading: boolean;
  uploadError: string | null;
  onUploadFile: (file: File) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({
  onLoadSample,
  isUploading,
  uploadError,
  onUploadFile,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleValidateAndUpload = (file: File) => {
    setValidationError(null);
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
    const hasValidExt = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExt) {
      setValidationError('Unsupported format. Please upload a PDF, JPG, JPEG, or PNG document.');
      return;
    }

    if (file.size === 0) {
      setValidationError('Uploaded file is empty (0 bytes).');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setValidationError('File size exceeds the 10 MB limit.');
      return;
    }

    onUploadFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleValidateAndUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="card no-print">
      <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px', color: '#0f172a' }}>
        Step 1: Upload Your Medical Report or Prescription
      </h2>
      <p style={{ fontSize: '14px', color: '#64748b', marginBottom: '20px' }}>
        Upload a clear photo or PDF (up to 10 MB). Your personal identifiers are redacted, and files are processed ephemerally.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragOver ? '#2563eb' : '#cbd5e1'}`,
          borderRadius: '12px',
          padding: '40px 20px',
          textAlign: 'center',
          backgroundColor: dragOver ? '#eff6ff' : '#f8fafc',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          style={{ display: 'none' }}
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleValidateAndUpload(e.target.files[0]);
            }
          }}
        />

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: '#e0e7ff', color: '#4338ca', padding: '12px', borderRadius: '50%' }}>
            <Upload size={28} />
          </div>
          <div>
            <p style={{ fontSize: '15px', fontWeight: 600, color: '#1e293b' }}>
              Click to select or drag and drop your report
            </p>
            <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              PDF, JPG, JPEG, or PNG (Max 10 MB)
            </p>
          </div>
          {isUploading && (
            <p style={{ fontSize: '14px', color: '#2563eb', fontWeight: 500 }}>
              Uploading and analyzing document...
            </p>
          )}
        </div>
      </div>

      {(validationError || uploadError) && (
        <div
          style={{
            marginTop: '16px',
            padding: '12px 16px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fca5a5',
            borderRadius: '8px',
            color: '#991b1b',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
          }}
        >
          <AlertCircle size={18} />
          <span>{validationError || uploadError}</span>
        </div>
      )}

      <div
        style={{
          marginTop: '24px',
          paddingTop: '20px',
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#475569', fontSize: '14px' }}>
          <FileText size={18} />
          <span>Want to try it instantly without a file?</span>
        </div>
        <button
          type="button"
          className="btn btn-outline"
          onClick={() => onLoadSample(sampleReportData as unknown as ReportResult)}
        >
          <Play size={16} />
          Load Standard CBC Sample Report
        </button>
      </div>
    </div>
  );
};

