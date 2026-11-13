import os
import re
import time
import shutil
import logging
from pathlib import Path
from typing import Optional, Set

# PII & Sensitive Clinical scrubbing regex patterns
PHONE_PATTERN = re.compile(r"(\+?91[\-\s]?)?[6-9]\d{9}")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")
NUMERICAL_LAB_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg/dL|g/dL|mmol/L|/uL|/cumm|mEq/L|%|fl|pg)\b", re.IGNORECASE)

KNOWN_DRUGS = [
    "paracetamol", "amoxicillin", "metformin", "atorvastatin", "amlodipine",
    "pantoprazole", "azithromycin", "ferrous sulphate", "insulin", "omeprazole"
]
DRUG_PATTERNS = [re.compile(rf"\b{re.escape(drug)}\b", re.IGNORECASE) for drug in KNOWN_DRUGS]

def sanitize_log_message(msg: str) -> str:
    """
    Scrubs patient PII, drug names, and exact clinical numerical values from log outputs (TC-25).
    """
    clean = PHONE_PATTERN.sub("[PHONE_REDACTED]", msg)
    clean = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", clean)
    clean = AADHAAR_PATTERN.sub("[AADHAAR_REDACTED]", clean)
    clean = NUMERICAL_LAB_PATTERN.sub("[LAB_VALUE_REDACTED]", clean)
    for dp in DRUG_PATTERNS:
        clean = dp.sub("[MEDICATION_REDACTED]", clean)
    return clean

class PrivacyPreservingLogFilter(logging.Filter):
    """
    Logging filter ensuring that no raw log entries contain PHI/PII.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        return True


class EphemeralStorageManager:
    """
    Manages temporary upload directories.
    - Prevents directory traversal attacks (../ or null bytes).
    - Enforces 10 MB maximum file size limit.
    - Provides cleanup_document for on-demand wiping (TC-26).
    - Provides cleanup_expired using TTL.
    """
    def __init__(self, base_dir: Optional[str] = None, default_ttl_seconds: int = 1800):
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            self.base_dir = Path("backend/temp_uploads").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl_seconds

    def validate_path(self, document_id: str) -> Path:
        """
        Guards against directory traversal and null byte injections.
        """
        if not document_id or "\0" in document_id:
            raise ValueError("Invalid document ID: null byte detected or empty.")
        if ".." in document_id or "/" in document_id or "\\" in document_id:
            raise ValueError("Invalid document ID: path traversal attempt detected.")
        
        target = (self.base_dir / document_id).resolve()
        # Verify the target is strictly inside self.base_dir
        try:
            target.relative_to(self.base_dir)
        except ValueError:
            raise ValueError("Invalid document ID: path traversal outside base directory.")
        return target

    def save_upload(self, document_id: str, filename: str, content: bytes) -> Path:
        """
        Saves uploaded file into isolated ephemeral folder after verifying size <= 10MB.
        """
        if len(content) > 10 * 1024 * 1024:
            raise ValueError("File exceeds maximum allowed size of 10 MB.")
            
        doc_folder = self.validate_path(document_id)
        doc_folder.mkdir(parents=True, exist_ok=True)

        safe_filename = Path(filename).name
        if ".." in safe_filename or "\0" in safe_filename:
            safe_filename = "upload.bin"

        file_path = doc_folder / safe_filename
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    def cleanup_document(self, document_id: str) -> bool:
        """
        Securely removes document and all extracted files on-demand (TC-26).
        """
        try:
            doc_folder = self.validate_path(document_id)
            if doc_folder.exists() and doc_folder.is_dir():
                shutil.rmtree(doc_folder)
                return True
            elif doc_folder.exists() and doc_folder.is_file():
                doc_folder.unlink()
                return True
            return False
        except Exception:
            return False

    def cleanup_expired(self, max_age_seconds: Optional[int] = None) -> int:
        """
        Iterates over temporary directories and removes any older than max_age_seconds.
        """
        ttl = max_age_seconds if max_age_seconds is not None else self.default_ttl
        now = time.time()
        removed_count = 0

        if not self.base_dir.exists():
            return 0

        for item in self.base_dir.iterdir():
            try:
                mtime = item.stat().st_mtime
                if now - mtime > ttl:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    removed_count += 1
            except Exception:
                pass
        return removed_count

