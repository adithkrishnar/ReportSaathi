# ReportSaathi (रिपोर्ट साथी)

> **Plain-Language Medical Report & Prescription Explainer**  
> *"This explains your report. It does not replace your doctor."*

ReportSaathi is an educational, non-clinical web application designed for patients and caregivers in India. It translates printed medical laboratory reports and printed prescriptions into clear, plain-language explanations in **English, Hindi, and Kannada** across three reading levels (**Simple, Standard, and Detailed**), bounded strictly by printed report reference ranges.

---

## Architecture Overview

```
ReportSaathi/
├── .github/workflows/      # Automated CI/CD (40 Python Tests + Frontend Build)
│   └── ci.yml
├── backend/
│   ├── main.py             # FastAPI App, CORS, Endpoints & Health Check
│   ├── safety/
│   │   ├── rules.py        # 5 Deterministic Red Flags & 5% Borderline Evaluator
│   │   ├── banned_phrases.py # Diagnosis & Dosage Modification Regex Filters
│   │   └── privacy.py      # PHI/PII Log Redactor & Ephemeral Storage Manager
│   └── integrations/
│       └── ocr.py          # Tesseract OCR wrapper & Clarity Noise Assessor
├── shared/
│   ├── types.ts            # Shared TypeScript Contracts & Domain Models
│   └── sample-report.json  # Complete Blood Count (CBC) Gold-Standard Fixture
├── frontend/
│   ├── src/
│   │   ├── components/     # Header, Footer, LanguageSelector, UploadView,
│   │   │                   # CheckValuesView, ResultsView, DoctorQuestionsView, ShareView
│   │   ├── api.ts          # Backend API Client with Health Status Probe
│   │   ├── App.tsx         # Responsive Multi-Step User Journey
│   │   └── index.css       # Clean Medical Healthcare Design System
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_safety.py      # 13 Safety Tests (Red flags, missing ranges, banned phrases)
│   ├── test_ocr.py         # 5 OCR Tests (Noise, Indian comma format, corrections)
│   ├── test_api_contract.py# 13 Contract Tests (10MB limit, 413, 400, 415, 422, disclaimers)
│   ├── test_privacy.py     # 9 Privacy Tests (Aadhaar/phone/drug scrubbing, traversal blocks)
│   └── fixtures/           # 10 Anonymized Gold-Standard Test Fixtures
└── README.md
```

---

## Critical Safety & Regulatory Non-Negotiables

1. **Zero Diagnosis**: Never diagnoses illnesses, predicts diseases, or claims a patient is disease-free.
2. **Zero Medication Modification**: Never advises starting, stopping, increasing, or decreasing prescription medicine dosages.
3. **Strict Report Reference Ranges**: Lab values are compared **ONLY** against ranges printed on the user's specific report. If missing, assigned `no_range_on_report`. Standard population ranges are never assumed.
4. **Deterministic Red Flags Before AI**: Critical thresholds (Potassium, Platelets, Hemoglobin, Glucose, Creatinine) execute programmatically in pure Python **BEFORE** any explanation text is generated.
5. **Mandatory Disclaimer**: Every screen, PDF, and API payload displays:  
   `"This explains your report. It does not replace your doctor."`
6. **Ephemeral Processing & 10 MB Limit**: No permanent storage of patient medical data in the MVP. Uploads are strictly capped at 10 MB and cleaned up on-demand or via TTL.

---

## 40-Test QA Suite Execution

Run the complete 40-test automated test suite:

```bash
python -m unittest discover tests -v
```

### Test Breakdown (100% Pass Rate):
- **Safety Engine (`test_safety.py`)**: 13 Tests
- **OCR Engine (`test_ocr.py`)**: 5 Tests
- **API Contracts (`test_api_contract.py`)**: 13 Tests
- **Privacy & Storage (`test_privacy.py`)**: 9 Tests

---

## Running the Application Locally

### 1. Start the Backend API (FastAPI)
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health: `http://127.0.0.1:8000/api/health`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (React + Vite)
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:3000`.

