import unittest
from fastapi import HTTPException
from backend.main import (
    app,
    DOC_STORE,
    get_health,
    handle_upload,
    extract_document,
    post_corrections,
    explain_report,
    get_questions,
    submit_feedback,
    ExtractRequest,
    CorrectionsRequest,
    ExplainRequest,
    QuestionsRequest,
    FeedbackRequest,
    MANDATORY_DISCLAIMER
)

class TestAPIContracts(unittest.TestCase):
    """
    13 API tests verifying:
    - Health endpoint contract
    - 10 MB payload limit enforcement (HTTP 413)
    - Empty file rejection (HTTP 400)
    - Unsupported file format rejection (HTTP 415)
    - Successful upload (HTTP 200)
    - Extract flow with missing document (HTTP 404)
    - Extract flow execution (HTTP 200)
    - User corrections non-empty validation (HTTP 422)
    - User corrections recalculation application (HTTP 200)
    - Explain endpoint schema & mandatory disclaimer presence
    - Explain endpoint deterministic red flag priority
    - Doctor questions count constraint (3 to 6 questions)
    - Feedback endpoint rating bounds validation (1 to 5)
    """

    def test_01_health_endpoint(self):
        res = get_health()
        self.assertEqual(res.status, "healthy")
        self.assertIn("ReportSaathi", res.service)

    def test_02_upload_empty_file_rejected_400(self):
        with self.assertRaises(HTTPException) as ctx:
            handle_upload("empty.pdf", b"")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("empty", str(ctx.exception.detail).lower())

    def test_03_upload_unsupported_format_rejected_415(self):
        with self.assertRaises(HTTPException) as ctx:
            handle_upload("malware.exe", b"binarydata")
        self.assertEqual(ctx.exception.status_code, 415)

    def test_04_upload_exceeding_10mb_rejected_413(self):
        oversized_bytes = b"0" * (10 * 1024 * 1024 + 100)
        with self.assertRaises(HTTPException) as ctx:
            handle_upload("huge.pdf", oversized_bytes)
        self.assertEqual(ctx.exception.status_code, 413)

    def test_05_upload_success_200(self):
        valid_pdf = b"%PDF-1.4 sample content"
        res = handle_upload("test_report.pdf", valid_pdf)
        self.assertTrue(bool(res.document_id))
        self.assertEqual(res.filename, "test_report.pdf")

    def test_06_extract_unknown_document_404(self):
        req = ExtractRequest(document_id="non-existent-doc-uuid")
        with self.assertRaises(HTTPException) as ctx:
            extract_document(req)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_07_extract_flow_success(self):
        doc_id = "test-doc-extract"
        DOC_STORE[doc_id] = {
            "document_id": doc_id,
            "filename": "sample.pdf",
            "file_path": "tests/fixtures/07-scanned-pdf.pdf",
            "raw_text": "",
            "biomarkers": []
        }
        req = ExtractRequest(document_id=doc_id)
        res = extract_document(req)
        self.assertEqual(res.document_id, doc_id)
        self.assertIsInstance(res.requires_verification, bool)

    def test_08_corrections_empty_text_422(self):
        with self.assertRaises(HTTPException) as ctx:
            post_corrections("doc-1", CorrectionsRequest(corrected_text="   "))
        self.assertEqual(ctx.exception.status_code, 422)

    def test_09_corrections_valid_application_200(self):
        doc_id = "test-doc-corr"
        req = CorrectionsRequest(corrected_text="Platelet Count 240000 /uL 150000 - 450000")
        res = post_corrections(doc_id, req)
        self.assertEqual(res.document_id, doc_id)
        self.assertEqual(len(res.biomarkers), 1)
        self.assertEqual(res.biomarkers[0].value, 240000)

    def test_10_explain_includes_mandatory_disclaimer_and_safety(self):
        doc_id = "test-doc-explain"
        DOC_STORE[doc_id] = {
            "document_id": doc_id,
            "biomarkers": [
                {
                    "name": "Hemoglobin",
                    "value": 14.0,
                    "unit": "g/dL",
                    "reference_low": 12.0,
                    "reference_high": 16.0,
                    "status": "normal"
                }
            ],
            "red_flags": []
        }
        req = ExplainRequest(document_id=doc_id, language="English", reading_level="Standard")
        res = explain_report(req)
        self.assertEqual(res.disclaimer, MANDATORY_DISCLAIMER)
        self.assertEqual(res.status, "ready")

    def test_11_explain_prioritizes_red_flags(self):
        doc_id = "test-doc-redflag"
        DOC_STORE[doc_id] = {
            "document_id": doc_id,
            "biomarkers": [
                {
                    "name": "Potassium",
                    "value": 6.8,
                    "unit": "mmol/L",
                    "reference_low": 3.5,
                    "reference_high": 5.0,
                    "status": "needs_attention"
                }
            ]
        }
        req = ExplainRequest(document_id=doc_id)
        res = explain_report(req)
        self.assertEqual(len(res.red_flags), 1)
        self.assertIn("emergency", res.summary.lower())

    def test_12_doctor_questions_range_between_3_and_6(self):
        doc_id = "test-doc-q"
        DOC_STORE[doc_id] = {
            "document_id": doc_id,
            "biomarkers": [
                {"name": "Hemoglobin", "value": 8.5, "unit": "g/dL", "status": "needs_attention"}
            ],
            "red_flags": []
        }
        req = QuestionsRequest(document_id=doc_id)
        res = get_questions(req)
        self.assertTrue(3 <= len(res.doctor_questions) <= 6)

    def test_13_feedback_validation_and_acceptance(self):
        # Invalid rating out of range
        with self.assertRaises(Exception):
            FeedbackRequest(rating=6, feedback="Too high")

        # Valid rating
        req = FeedbackRequest(rating=5, feedback="Very helpful!")
        res = submit_feedback(req)
        self.assertEqual(res.status, "success")

if __name__ == "__main__":
    unittest.main()
