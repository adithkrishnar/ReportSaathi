import unittest
import tempfile
import time
from pathlib import Path
from backend.safety.privacy import (
    sanitize_log_message,
    PrivacyPreservingLogFilter,
    EphemeralStorageManager
)

class TestPrivacyAndStorage(unittest.TestCase):
    """
    9 tests verifying:
    - Phone number scrubbing from log messages
    - Email address scrubbing from log messages
    - Aadhaar number scrubbing from log messages
    - Numerical lab results scrubbing from log messages
    - Prescription drug names scrubbing from log messages
    - EphemeralStorageManager directory traversal block
    - EphemeralStorageManager null-byte injection block
    - EphemeralStorageManager on-demand document cleanup (TC-26)
    - EphemeralStorageManager TTL-based expiration purge
    """

    def test_01_scrub_phone_numbers(self):
        log = "Patient phone is +91 9876543210 for follow up."
        clean = sanitize_log_message(log)
        self.assertNotIn("9876543210", clean)
        self.assertIn("[PHONE_REDACTED]", clean)

    def test_02_scrub_emails(self):
        log = "Sent report to patient.user@example.com."
        clean = sanitize_log_message(log)
        self.assertNotIn("patient.user@example.com", clean)
        self.assertIn("[EMAIL_REDACTED]", clean)

    def test_03_scrub_aadhaar(self):
        log = "ID verified: 1234 5678 9012 valid."
        clean = sanitize_log_message(log)
        self.assertNotIn("1234 5678 9012", clean)
        self.assertIn("[AADHAAR_REDACTED]", clean)

    def test_04_scrub_numerical_lab_values(self):
        log = "Extracted Hemoglobin value: 13.5 g/dL and Glucose 140 mg/dL"
        clean = sanitize_log_message(log)
        self.assertNotIn("13.5 g/dL", clean)
        self.assertNotIn("140 mg/dL", clean)
        self.assertIn("[LAB_VALUE_REDACTED]", clean)

    def test_05_scrub_prescription_drugs(self):
        log = "Prescribed Metformin 500mg and Paracetamol for fever."
        clean = sanitize_log_message(log)
        self.assertNotIn("Metformin", clean)
        self.assertNotIn("Paracetamol", clean)
        self.assertIn("[MEDICATION_REDACTED]", clean)

    def test_06_storage_blocks_directory_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = EphemeralStorageManager(base_dir=tmpdir)
            with self.assertRaises(ValueError):
                mgr.validate_path("../../windows/system32")

    def test_07_storage_blocks_null_byte_injection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = EphemeralStorageManager(base_dir=tmpdir)
            with self.assertRaises(ValueError):
                mgr.validate_path("doc123\0injected")

    def test_08_storage_cleanup_document_on_demand(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = EphemeralStorageManager(base_dir=tmpdir)
            doc_id = "doc-to-clean"
            path = mgr.save_upload(doc_id, "test.pdf", b"test-data")
            self.assertTrue(path.exists())
            
            cleaned = mgr.cleanup_document(doc_id)
            self.assertTrue(cleaned)
            self.assertFalse(path.exists())

    def test_09_storage_cleanup_expired_ttl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = EphemeralStorageManager(base_dir=tmpdir, default_ttl_seconds=1)
            doc_id = "expired-doc"
            path = mgr.save_upload(doc_id, "old.pdf", b"old-data")
            self.assertTrue(path.exists())

            # Wait 1.1s for TTL to expire
            time.sleep(1.1)
            purged = mgr.cleanup_expired(max_age_seconds=1)
            self.assertEqual(purged, 1)
            self.assertFalse(path.exists())

if __name__ == "__main__":
    unittest.main()

