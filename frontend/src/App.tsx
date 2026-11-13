import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { LanguageSelector } from './components/LanguageSelector';
import { UploadView } from './components/UploadView';
import { CheckValuesView } from './components/CheckValuesView';
import { ResultsView } from './components/ResultsView';
import { DoctorQuestionsView } from './components/DoctorQuestionsView';
import { ShareView } from './components/ShareView';
import {
  checkBackendHealth,
  uploadDocument,
  extractDocument,
  submitCorrections,
  requestExplanation,
  HealthStatus,
} from './api';
import { SupportedLanguage, ReadingLevel, ReportResult, BiomarkerValue, RedFlagAlert } from './types';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus>({ online: false, service: 'ReportSaathi API' });
  const [language, setLanguage] = useState<SupportedLanguage>('English');
  const [readingLevel, setReadingLevel] = useState<ReadingLevel>('Standard');

  // Multi-step workflow state
  const [currentStep, setCurrentStep] = useState<'upload' | 'check' | 'results'>('upload');
  const [documentId, setDocumentId] = useState<string>('');
  const [rawText, setRawText] = useState<string>('');
  const [biomarkers, setBiomarkers] = useState<BiomarkerValue[]>([]);
  const [redFlags, setRedFlags] = useState<RedFlagAlert[]>([]);
  const [requiresVerification, setRequiresVerification] = useState<boolean>(false);

  // Results state
  const [reportResult, setReportResult] = useState<ReportResult | null>(null);

  // Loading & error handling
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const probe = async () => {
      const status = await checkBackendHealth();
      setHealth(status);
    };
    probe();
    const interval = setInterval(probe, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    try {
      const uploadRes = await uploadDocument(file);
      setDocumentId(uploadRes.document_id);

      // Trigger OCR extraction
      const extractRes = await extractDocument(uploadRes.document_id);
      setRawText(extractRes.raw_text);
      setBiomarkers(extractRes.biomarkers);
      setRedFlags(extractRes.red_flags);
      setRequiresVerification(extractRes.requires_verification);

      setCurrentStep('check');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed.';
      setUploadError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadSample = (sampleData: ReportResult) => {
    setReportResult(sampleData);
    setBiomarkers(sampleData.biomarkers);
    setRedFlags(sampleData.red_flags);
    setCurrentStep('results');
  };

  const handleApplyCorrections = async (correctedText: string) => {
    const res = await submitCorrections(documentId, correctedText);
    setRawText(correctedText);
    setBiomarkers(res.biomarkers);
    setRedFlags(res.red_flags);
    setRequiresVerification(res.requires_verification);
  };

  const handleProceedToExplanation = async () => {
    setIsProcessing(true);
    try {
      const result = await requestExplanation(documentId, language, readingLevel);
      setReportResult(result);
      setCurrentStep('results');
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error generating explanation.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setCurrentStep('upload');
    setDocumentId('');
    setRawText('');
    setBiomarkers([]);
    setRedFlags([]);
    setReportResult(null);
    setUploadError(null);
  };

  return (
    <div>
      <div className="container">
        <Header health={health} />

        <LanguageSelector
          language={language}
          readingLevel={readingLevel}
          onLanguageChange={setLanguage}
          onReadingLevelChange={setReadingLevel}
        />

        {currentStep === 'upload' && (
          <UploadView
            onUploadSuccess={(docId) => setDocumentId(docId)}
            onLoadSample={handleLoadSample}
            isUploading={isUploading}
            uploadError={uploadError}
            onUploadFile={handleUploadFile}
          />
        )}

        {currentStep === 'check' && (
          <CheckValuesView
            documentId={documentId}
            rawText={rawText}
            biomarkers={biomarkers}
            redFlags={redFlags}
            requiresVerification={requiresVerification}
            onProceedToExplanation={handleProceedToExplanation}
            onApplyCorrections={handleApplyCorrections}
            isProcessing={isProcessing}
          />
        )}

        {currentStep === 'results' && reportResult && (
          <>
            <div className="no-print" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'flex-start' }}>
              <button type="button" className="btn btn-secondary" onClick={handleReset}>
                ← Analyze Another Report
              </button>
            </div>

            <ResultsView report={reportResult} />
            <DoctorQuestionsView questions={reportResult.doctor_questions} />
            <ShareView summary={reportResult.summary} />
          </>
        )}
      </div>

      <Footer />
    </div>
  );
};

