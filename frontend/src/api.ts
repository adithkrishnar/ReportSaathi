import { ReportResult, BiomarkerValue, RedFlagAlert } from './types';

const API_BASE = '/api';

export interface HealthStatus {
  online: boolean;
  service: string;
}

export async function checkBackendHealth(): Promise<HealthStatus> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      return { online: true, service: data.service || 'ReportSaathi API' };
    }
    return { online: false, service: 'ReportSaathi API' };
  } catch {
    return { online: false, service: 'ReportSaathi API' };
  }
}

export async function uploadDocument(file: File): Promise<{ document_id: string; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let errMsg = `Upload failed with status ${res.status}`;
    try {
      const errData = await res.json();
      if (errData.detail) errMsg = errData.detail;
    } catch {}
    throw new Error(errMsg);
  }

  return res.json();
}

export async function extractDocument(document_id: string): Promise<{
  raw_text: string;
  requires_verification: boolean;
  noise_ratio: number;
  biomarkers: BiomarkerValue[];
  red_flags: RedFlagAlert[];
}> {
  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id }),
  });

  if (!res.ok) {
    throw new Error('Extraction failed. Please verify the document or backend connection.');
  }

  return res.json();
}

export async function submitCorrections(document_id: string, corrected_text: string) {
  const res = await fetch(`${API_BASE}/extract/${document_id}/corrections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ corrected_text }),
  });

  if (!res.ok) {
    throw new Error('Failed to apply corrections.');
  }

  return res.json();
}

export async function requestExplanation(
  document_id: string,
  language: string,
  reading_level: string
): Promise<ReportResult> {
  const res = await fetch(`${API_BASE}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id, language, reading_level }),
  });

  if (!res.ok) {
    throw new Error('Failed to generate report explanation.');
  }

  return res.json();
}

export async function submitFeedback(rating: number, feedback?: string) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, feedback }),
  });
  return res.json();
}
