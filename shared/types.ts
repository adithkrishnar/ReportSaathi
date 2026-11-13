export type ClinicalStatus = 'normal' | 'borderline' | 'needs_attention' | 'no_range_on_report';

export type ReadingLevel = 'Simple' | 'Standard' | 'Detailed';
export type SupportedLanguage = 'English' | 'Hindi' | 'Kannada';

export interface BiomarkerValue {
  name: string;
  value: number;
  unit: string;
  reference_low?: number | null;
  reference_high?: number | null;
  status: ClinicalStatus;
  explanation?: string;
  interpretation?: string;
}

export interface RedFlagAlert {
  biomarker: string;
  value: number;
  unit: string;
  threshold_rule: string;
  message: string;
  urgency: 'EMERGENCY' | 'URGENT';
}

export interface MedicineInstruction {
  name: string;
  dosage: string;
  frequency: string;
  instructions: string;
}

export interface ReportResult {
  document_id: string;
  language: SupportedLanguage;
  reading_level: ReadingLevel;
  disclaimer: string;
  requires_verification: boolean;
  biomarkers: BiomarkerValue[];
  red_flags: RedFlagAlert[];
  doctor_questions: string[];
  prescriptions?: MedicineInstruction[];
  summary: string;
  status: 'ready' | 'unclear' | 'error';
}

export interface UserCorrectionPayload {
  document_id: string;
  raw_text: string;
  biomarkers?: BiomarkerValue[];
}

export interface FeedbackPayload {
  rating: number; // 1-5
  feedback?: string;
}

