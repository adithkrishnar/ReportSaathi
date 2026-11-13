import os
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.safety.rules import (
    evaluate_biomarker,
    check_red_flags,
    MANDATORY_DISCLAIMER
)
from backend.safety.banned_phrases import sanitize_ai_output
from backend.safety.privacy import (
    PrivacyPreservingLogFilter,
    EphemeralStorageManager
)
from backend.integrations.ocr import (
    run_tesseract,
    assess_text_clarity,
    parse_biomarkers_from_text,
    apply_user_corrections
)

# Setup Privacy-Preserving Logger
logger = logging.getLogger("ReportSaathi")
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_handler.addFilter(PrivacyPreservingLogFilter())
logger.addHandler(log_handler)

app = FastAPI(
    title="ReportSaathi API",
    description="Educational plain-language medical report and prescription explainer backend.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage_manager = EphemeralStorageManager()

# Temporary in-memory document store for active session workflows
DOC_STORE: Dict[str, Dict[str, Any]] = {}

# ----------------- Pydantic Models -----------------

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "ReportSaathi API"

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    size_bytes: int
    message: str

class BiomarkerItem(BaseModel):
    name: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    status: Literal['normal', 'borderline', 'needs_attention', 'no_range_on_report']
    interpretation: Optional[str] = None
    explanation: Optional[str] = None

class RedFlagAlertItem(BaseModel):
    biomarker: str
    value: float
    unit: str
    threshold_rule: str
    message: str
    urgency: Literal['EMERGENCY', 'URGENT']

class ExtractRequest(BaseModel):
    document_id: str

class ExtractResponse(BaseModel):
    document_id: str
    raw_text: str
    requires_verification: bool
    noise_ratio: float
    biomarkers: List[BiomarkerItem]
    red_flags: List[RedFlagAlertItem]

class CorrectionsRequest(BaseModel):
    corrected_text: str = Field(..., min_length=1, description="Non-empty user corrected text")

class CorrectionsResponse(BaseModel):
    document_id: str
    biomarkers: List[BiomarkerItem]
    red_flags: List[RedFlagAlertItem]
    requires_verification: bool
    noise_ratio: float

class ExplainRequest(BaseModel):
    document_id: str
    language: Literal['English', 'Hindi', 'Kannada'] = 'English'
    reading_level: Literal['Simple', 'Standard', 'Detailed'] = 'Standard'

class MedicineInstructionItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    instructions: str

class ExplainResponse(BaseModel):
    document_id: str
    language: str
    reading_level: str
    disclaimer: str
    summary: str
    biomarkers: List[BiomarkerItem]
    red_flags: List[RedFlagAlertItem]
    doctor_questions: List[str]
    prescriptions: List[MedicineInstructionItem]
    status: str

class QuestionsRequest(BaseModel):
    document_id: str

class QuestionsResponse(BaseModel):
    document_id: str
    doctor_questions: List[str]

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    message: str

# ----------------- Multilingual & Level Templates -----------------

BIOMARKER_KNOWLEDGE: Dict[str, Dict[str, Dict[str, str]]] = {
    "hemoglobin": {
        "English": {
            "Simple": "Hemoglobin is the protein in your blood that carries oxygen throughout your body.",
            "Standard": "Hemoglobin is the iron-rich protein in red blood cells that transports oxygen from your lungs to your tissues and organs.",
            "Detailed": "Hemoglobin (Hb) is a tetrameric protein found inside erythrocytes that binds molecular oxygen in pulmonary capillaries for delivery to systemic tissues."
        },
        "Hindi": {
            "Simple": "हीमोग्लोबिन आपके रक्त में मौजूद प्रोटीन है जो पूरे शरीर में ऑक्सीजन पहुंचाता है।",
            "Standard": "हीमोग्लोबिन लाल रक्त कोशिकाओं में मौजूद प्रोटीन है जो फेफड़ों से शरीर के सभी अंगों तक ऑक्सीजन ले जाता है।",
            "Detailed": "हीमोग्लोबिन लाल रक्त कोशिकाओं में स्थित एक महत्वपूर्ण प्रोटीन है जो फेफड़ों से ऑक्सीजन को शरीर के ऊतकों तक पहुंचाता है।"
        },
        "Kannada": {
            "Simple": "ಹಿಮೋಗ್ಲೋಬಿನ್ ನಿಮ್ಮ ರಕ್ತದಲ್ಲಿರುವ ಪ್ರೋಟೀನ್ ಆಗಿದ್ದು, ಇದು ದೇಹದಾದ್ಯಂತ ಆಮ್ಲಜನಕವನ್ನು ಸಾಗಿಸುತ್ತದೆ.",
            "Standard": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಕೆಂಪು ರಕ್ತ ಕಣಗಳಲ್ಲಿರುವ ಪ್ರೋಟೀನ್ ಆಗಿದ್ದು, ಶ್ವಾಸಕೋಶದಿಂದ ಅಂಗಗಳಿಗೆ ಆಮ್ಲಜನಕವನ್ನು ಸಾಗಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "Detailed": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಕೆಂಪು ರಕ್ತ ಕಣಗಳಲ್ಲಿರುವ ಕಬ್ಬಿಣ-ಸಮೃದ್ಧ ಪ್ರೋಟೀನ್ ಆಗಿದ್ದು, ಶ್ವಾಸಕೋಶದಿಂದ ಅಂಗಾಂಶಗಳಿಗೆ ಆಮ್ಲಜನಕವನ್ನು ಸಾಗಿಸುತ್ತದೆ."
        }
    },
    "platelet": {
        "English": {
            "Simple": "Platelets are blood cells that help stop bleeding by forming clots.",
            "Standard": "Platelets (thrombocytes) are specialized blood cell fragments that cluster together to clot blood and stop bleeding when injuries occur.",
            "Detailed": "Platelets are disc-shaped cell fragments derived from bone marrow megakaryocytes essential for primary hemostasis and vascular wall integrity."
        },
        "Hindi": {
            "Simple": "प्लेटलेट्स रक्त कोशिकाएं हैं जो चोट लगने पर खून का थक्का बनाकर बहाव रोकती हैं।",
            "Standard": "प्लेटलेट्स रक्त कोशिकाएं हैं जो रक्त का थक्का बनाने और चोट के दौरान अत्यधिक रक्तस्राव को रोकने में मदद करती हैं।",
            "Detailed": "प्लेटलेट्स अस्थि मज्जा में बनने वाले सेल फ्रैग्मेंट्स हैं जो हेमोस्टेसिस (रक्त का थक्का जमना) में केंद्रीय भूमिका निभाते हैं।"
        },
        "Kannada": {
            "Simple": "ಪ್ಲೇಟ್‌ಲೆಟ್‌ಗಳು ಗಾಯವಾದಾಗ ರಕ್ತ ಹೆಪ್ಪುಗಟ್ಟಲು ಸಹಾಯ ಮಾಡುವ ರಕ್ತ ಕಣಗಳಾಗಿವೆ.",
            "Standard": "ಪ್ಲೇಟ್‌ಲೆಟ್‌ಗಳು ರಕ್ತ ಹೆಪ್ಪುಗಟ್ಟುವಿಕೆಗೆ ಕಾರಣವಾಗುವ ಪ್ರಮುಖ ಕಣಗಳಾಗಿದ್ದು, ರಕ್ತಸ್ರಾವವನ್ನು ತಡೆಯುತ್ತವೆ.",
            "Detailed": "ಪ್ಲೇಟ್‌ಲೆಟ್‌ಗಳು ಅಸ್ಥಿಮಜ್ಜೆಯಿಂದ ಉತ್ಪತ್ತಿಯಾಗುವ ಜೀವಕೋಶಗಳಾಗಿದ್ದು, ಪ್ರಾಥಮಿಕ ಹೆಮೊಸ್ಟಾಸಿಸ್ ಮತ್ತು ರಕ್ತ ಹೆಪ್ಪುಗಟ್ಟುವಿಕೆಗೆ ಪ್ರಮುಖವಾಗಿವೆ."
        }
    },
    "wbc": {
        "English": {
            "Simple": "White blood cells help your body fight off illnesses and infections.",
            "Standard": "White blood cells (leukocytes) form the primary defense system of your body, combating viral, bacterial, and inflammatory threats.",
            "Detailed": "White blood cells comprise neutrophils, lymphocytes, monocytes, eosinophils, and basophils, orchestrating innate and adaptive immune responses."
        },
        "Hindi": {
            "Simple": "सफेद रक्त कोशिकाएं (WBC) आपके शरीर को बीमारियों और संक्रमण से लड़ने में मदद करती हैं।",
            "Standard": "सफेद रक्त कोशिकाएं (ल्यूकोसाइट्स) आपकी प्रतिरक्षा प्रणाली का मुख्य हिस्सा हैं जो बैक्टीरिया और वायरस से लड़ती हैं।",
            "Detailed": "ल्यूकोसाइट्स प्रतिरक्षा तंत्र के अभिन्न घटक हैं जो रोगजनकों और सूजन के खिलाफ प्रतिरक्षा प्रतिक्रिया का संचालन करते हैं।"
        },
        "Kannada": {
            "Simple": "ಬಿಳಿ ರಕ್ತ ಕಣಗಳು ನಿಮ್ಮ ದೇಹಕ್ಕೆ ಸೋಂಕು ಮತ್ತು ಕಾಯಿಲೆಗಳ ವಿರುದ್ಧ ಹೋರಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ.",
            "Standard": "ಬಿಳಿ ರಕ್ತ ಕಣಗಳು ರೋಗನಿರೋಧಕ ವ್ಯವಸ್ಥೆಯ ಪ್ರಮುಖ ಅಂಗವಾಗಿದ್ದು, ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮತ್ತು ವೈರಸ್ ವಿರುದ್ಧ ರಕ್ಷಣೆ ನೀಡುತ್ತವೆ.",
            "Detailed": "ಲ್ಯುಕೋಸೈಟ್‌ಗಳು ಪ್ರತಿರಕ್ಷಣಾ ವ್ಯವಸ್ಥೆಯ ಮುಖ್ಯ ಕಣಗಳಾಗಿದ್ದು, ಸೋಂಕುಗಳ ವಿರುದ್ಧ ದೇಹವನ್ನು ರಕ್ಷಿಸುತ್ತವೆ."
        }
    }
}

# ----------------- API Endpoints -----------------

@app.get("/api/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint"""
    return HealthResponse()

def handle_upload(filename: Optional[str], content: bytes) -> UploadResponse:
    """
    Internal handler for upload validation and persistence.
    """
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    ext = Path(filename).suffix.lower()
    allowed_exts = {".pdf", ".jpg", ".jpeg", ".png"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Only PDF, JPG, JPEG, and PNG are supported."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the maximum 10 MB size limit."
        )

    document_id = str(uuid.uuid4())
    saved_path = storage_manager.save_upload(document_id, filename, content)

    DOC_STORE[document_id] = {
        "document_id": document_id,
        "filename": filename,
        "file_path": str(saved_path),
        "raw_text": "",
        "biomarkers": [],
        "red_flags": [],
        "requires_verification": False,
        "noise_ratio": 0.0
    }

    logger.info(f"File uploaded successfully with document_id={document_id}")
    return UploadResponse(
        document_id=document_id,
        filename=filename,
        size_bytes=len(content),
        message="File uploaded successfully."
    )

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Enforces:
    - 10 MB maximum upload limit (413 Payload Too Large)
    - Empty file rejection (400 Bad Request)
    - Supported formats: PDF, JPG, JPEG, PNG (415 Unsupported Media Type)
    """
    content = await file.read()
    return handle_upload(file.filename, content)

@app.post("/api/extract", response_model=ExtractResponse)
def extract_document(payload: ExtractRequest):
    """
    Runs OCR on uploaded file, scores clarity, and parses biomarkers.
    """
    doc_id = payload.document_id
    doc_info = DOC_STORE.get(doc_id)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_id}' not found."
        )

    file_path = doc_info["file_path"]
    ocr_text = run_tesseract(file_path)

    # If OCR output is empty (e.g., scanned PDF or testing without Tesseract installed),
    # fallback to any existing text file or empty string
    txt_sidecar = Path(file_path).with_suffix(".txt")
    if not ocr_text and txt_sidecar.exists():
        with open(txt_sidecar, "r", encoding="utf-8") as tf:
            ocr_text = tf.read()

    requires_verification, noise_ratio = assess_text_clarity(ocr_text)
    biomarkers = parse_biomarkers_from_text(ocr_text)
    red_flags = check_red_flags(biomarkers)

    doc_info["raw_text"] = ocr_text
    doc_info["requires_verification"] = requires_verification
    doc_info["noise_ratio"] = noise_ratio
    doc_info["biomarkers"] = biomarkers
    doc_info["red_flags"] = red_flags

    return ExtractResponse(
        document_id=doc_id,
        raw_text=ocr_text,
        requires_verification=requires_verification,
        noise_ratio=noise_ratio,
        biomarkers=biomarkers,
        red_flags=red_flags
    )

@app.post("/api/extract/{document_id}/corrections", response_model=CorrectionsResponse)
def post_corrections(document_id: str, payload: CorrectionsRequest):
    """
    Applies patient corrections to raw text. Validates non-empty corrected text (422).
    Re-evaluates biomarkers and deterministic red flags.
    """
    if not payload.corrected_text or not payload.corrected_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Corrected text must not be empty."
        )

    doc_info = DOC_STORE.get(document_id)
    if not doc_info:
        # Create minimal session entry if not in store
        doc_info = {"document_id": document_id}
        DOC_STORE[document_id] = doc_info

    result = apply_user_corrections(payload.corrected_text)
    doc_info["raw_text"] = payload.corrected_text
    doc_info["biomarkers"] = result["biomarkers"]
    doc_info["red_flags"] = result["red_flags"]
    doc_info["requires_verification"] = result["requires_verification"]
    doc_info["noise_ratio"] = result["noise_ratio"]

    return CorrectionsResponse(
        document_id=document_id,
        biomarkers=result["biomarkers"],
        red_flags=result["red_flags"],
        requires_verification=result["requires_verification"],
        noise_ratio=result["noise_ratio"]
    )

@app.post("/api/explain", response_model=ExplainResponse)
def explain_report(payload: ExplainRequest):
    """
    Generates educational explanation strictly adhering to safety rules:
    - Runs deterministic check_red_flags() FIRST.
    - Compares biomarkers ONLY against printed report ranges.
    - Sanitizes output via banned phrases regex filter.
    - Appends mandatory disclaimer.
    """
    doc_id = payload.document_id
    doc_info = DOC_STORE.get(doc_id)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_id}' not found."
        )

    biomarkers = doc_info.get("biomarkers", [])
    # Re-verify red flags deterministically before any text generation
    red_flags = check_red_flags(biomarkers)

    lang = payload.language
    level = payload.reading_level

    # Generate biomarker explanations
    enriched_biomarkers: List[BiomarkerItem] = []
    for b in biomarkers:
        b_name = b.get("name", "")
        lookup_key = ""
        for k in ["hemoglobin", "platelet", "wbc"]:
            if k in b_name.lower():
                lookup_key = k
                break

        if lookup_key and lookup_key in BIOMARKER_KNOWLEDGE:
            explanation = BIOMARKER_KNOWLEDGE[lookup_key].get(lang, {}).get(level, "")
        else:
            explanation = f"{b_name} is a standard blood laboratory parameter."

        b_item = BiomarkerItem(
            name=b_name,
            value=b.get("value", 0.0),
            unit=b.get("unit", ""),
            reference_low=b.get("reference_low"),
            reference_high=b.get("reference_high"),
            status=b.get("status", "no_range_on_report"),
            interpretation=b.get("interpretation", ""),
            explanation=explanation
        )
        enriched_biomarkers.append(b_item)

    # Summary synthesis
    if red_flags:
        summary_raw = (
            f"Urgent clinical indicators were identified in your report ({len(red_flags)} critical threshold(s)). "
            "Please review the emergency alert at the top of this page and contact emergency medical services or your physician immediately."
        )
    elif enriched_biomarkers:
        summary_raw = (
            f"Your report contains {len(enriched_biomarkers)} laboratory value(s). "
            "Each measurement is compared strictly against the reference range printed on your laboratory report."
        )
    else:
        summary_raw = (
            "No laboratory values could be automatically identified from this image. "
            "Please verify that a medical laboratory report was uploaded, or type in your values manually."
        )

    # Banned phrase safety filter verification
    sanitized_summary, _ = sanitize_ai_output(summary_raw)

    doctor_questions = generate_doctor_questions_list(enriched_biomarkers, red_flags)

    return ExplainResponse(
        document_id=doc_id,
        language=lang,
        reading_level=level,
        disclaimer=MANDATORY_DISCLAIMER,
        summary=sanitized_summary,
        biomarkers=enriched_biomarkers,
        red_flags=red_flags,
        doctor_questions=doctor_questions,
        prescriptions=[],
        status="ready" if enriched_biomarkers or red_flags else "unclear"
    )

def generate_doctor_questions_list(biomarkers: List[Any], red_flags: List[Any]) -> List[str]:
    """
    Generates 3 to 6 targeted doctor consultation questions based on findings.
    """
    questions: List[str] = []

    if red_flags:
        questions.append("What immediate emergency steps should I take regarding my critical alert values?")
        questions.append("Does my condition require immediate hospital admission or medication adjustment by you?")

    out_of_range = [b for b in biomarkers if getattr(b, "status", None) in ("needs_attention", "borderline")]
    if out_of_range:
        names = ", ".join([getattr(b, "name", "parameter") for b in out_of_range[:3]])
        questions.append(f"What might be contributing to my {names} reading(s)?")
        questions.append("Would you recommend repeating this test or ordering any follow-up investigations?")

    no_ranges = [b for b in biomarkers if getattr(b, "status", None) == "no_range_on_report"]
    if no_ranges:
        names = ", ".join([getattr(b, "name", "parameter") for b in no_ranges[:2]])
        questions.append(f"How should I understand my result for {names} since no reference range was printed on the report?")

    questions.append("Are there any specific lifestyle, dietary, or hydration changes you recommend based on these findings?")
    questions.append("When would you like me to schedule my next follow-up appointment?")

    # Ensure between 3 and 6 questions
    return questions[:6] if len(questions) >= 3 else (questions + [
        "What signs or symptoms should prompt me to contact your clinic before our next visit?",
        "Should any of my current supplements or medicines be reviewed?"
    ])[:4]

@app.post("/api/questions", response_model=QuestionsResponse)
def get_questions(payload: QuestionsRequest):
    """Returns 3 to 6 targeted consultation questions for the doctor."""
    doc_id = payload.document_id
    doc_info = DOC_STORE.get(doc_id, {})
    biomarkers = doc_info.get("biomarkers", [])
    red_flags = doc_info.get("red_flags", [])

    questions = generate_doctor_questions_list(biomarkers, red_flags)
    return QuestionsResponse(document_id=doc_id, doctor_questions=questions)

@app.post("/api/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest):
    """Receives user rating (1-5) and feedback without personal health data."""
    logger.info(f"Feedback received: rating={payload.rating}")
    return FeedbackResponse(status="success", message="Thank you for your feedback.")
