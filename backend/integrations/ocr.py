import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from backend.safety.rules import evaluate_biomarker, check_red_flags

COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "tesseract"
]

def find_tesseract_binary() -> str:
    for p in COMMON_TESSERACT_PATHS:
        if os.path.exists(p):
            return p
    return "tesseract"

def run_tesseract(image_path: str) -> str:
    """
    Executes Tesseract CLI on given image or PDF file path.
    Falls back gracefully if image cannot be parsed or OCR fails.
    """
    cmd = [find_tesseract_binary(), str(image_path), "stdout"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout
    except Exception as e:
        return ""

def assess_text_clarity(text: str) -> Tuple[bool, float]:
    """
    Algorithmic noise/clarity scoring.
    Evaluates:
    - Non-alphanumeric noise ratio (> 0.15 indicates poor scan/blurry text)
    - Presence of garbled tokens
    - Very short character counts
    Returns: (requires_verification: bool, noise_ratio: float)
    """
    if not text or len(text.strip()) < 15:
        return True, 1.0

    cleaned = text.strip()
    total_chars = len(cleaned)
    # Count noise characters (non-alphanumeric and not standard punctuation/units/spaces)
    noise_chars = len(re.findall(r"[^\w\s.,%/\-<>()+:]", cleaned))
    noise_ratio = noise_chars / float(total_chars)

    # Specific gibberish artifacts common in bad OCR
    has_heavy_distortion = bool(re.search(r"(\?{3,}|\~{2,}|\_{4,}|[|]{3,}|)", cleaned))

    requires_verification = (noise_ratio > 0.15) or has_heavy_distortion or (len(cleaned.split()) < 3)
    return requires_verification, round(noise_ratio, 3)

def parse_number(val_str: str) -> Optional[float]:
    """
    Parses numbers including Indian numbering commas e.g. '3,25,000' or '13.5'.
    """
    try:
        clean = val_str.replace(",", "").strip()
        return float(clean)
    except (ValueError, TypeError):
        return None

def parse_biomarkers_from_text(raw_text: str) -> List[Dict[str, Any]]:
    """
    Robust regex and tabular parser extracting test names, values, units,
    and printed ranges from raw OCR text.
    Handles:
    - Standard tabular format: Test Name | Value | Unit | Range
    - Indian comma numbers: '3,25,000'
    - Inequality operators: '< 0.5', '> 1.0'
    - Missing ranges (low/high set to None -> triggers 'no_range_on_report')
    """
    biomarkers: List[Dict[str, Any]] = []
    lines = raw_text.splitlines()

    # Pattern for lines: Name ... Value ... Unit ... Range
    # e.g.: "Hemoglobin 13.5 g/dL 12.0 - 15.5"
    # e.g.: "Platelet Count 2,40,000 /uL 150000 - 450000"
    # e.g.: "C-Reactive Protein (CRP) 12.5 mg/L" (missing range)
    # e.g.: "Thyroid Stimulating Hormone (TSH) < 0.5 uIU/mL 0.4 - 4.2"
    
    range_regex = re.compile(
        r"(?:(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?))",
        re.IGNORECASE
    )

    for line in lines:
        line_str = line.strip()
        if not line_str or len(line_str) < 4:
            continue

        # Look for range in line
        range_match = range_regex.search(line_str)
        ref_low: Optional[float] = None
        ref_high: Optional[float] = None
        remaining_line = line_str

        if range_match:
            try:
                ref_low = float(range_match.group(1))
                ref_high = float(range_match.group(2))
                # remove the range substring so it doesn't collide with the test value
                remaining_line = line_str[:range_match.start()] + line_str[range_match.end():]
            except Exception:
                pass

        # Look for value with optional operator and unit
        # Pattern matches: optional '<' or '>' then number with optional commas/decimals
        val_match = re.search(
            r"([<>]?\s*\d+(?:,\d+)*(?:\.\d+)?)\s*([a-zA-Z/%]+(?:/[a-zA-Z0-9]+)?)?",
            remaining_line
        )

        if val_match:
            raw_val_token = val_match.group(1).strip()
            unit_token = (val_match.group(2) or "").strip()

            # Name is whatever precedes the value
            name_part = remaining_line[:val_match.start()].strip(" :|-_\t")
            
            # Filter out non-test lines (headers, patient info, etc.)
            ignored_headers = ["date", "patient", "dr.", "doctor", "name", "age", "sex", "gender", "sample", "report", "test name"]
            if any(name_part.lower().startswith(h) for h in ignored_headers):
                continue
            if len(name_part) < 2:
                continue

            # Handle operator in value
            val_clean = raw_val_token.lstrip("<> ").strip()
            num_val = parse_number(val_clean)
            if num_val is None:
                continue

            status, interpretation = evaluate_biomarker(
                name=name_part,
                value=num_val,
                unit=unit_token,
                low=ref_low,
                high=ref_high
            )

            biomarkers.append({
                "name": name_part,
                "value": num_val,
                "unit": unit_token,
                "reference_low": ref_low,
                "reference_high": ref_high,
                "status": status,
                "interpretation": interpretation
            })

    return biomarkers

def apply_user_corrections(corrected_text: str) -> Dict[str, Any]:
    """
    Re-parses patient-edited text, re-evaluates clinical statuses against printed ranges,
    and re-triggers deterministic red flag checks.
    """
    biomarkers = parse_biomarkers_from_text(corrected_text)
    red_flags = check_red_flags(biomarkers)
    requires_verification, noise_ratio = assess_text_clarity(corrected_text)

    return {
        "biomarkers": biomarkers,
        "red_flags": red_flags,
        "requires_verification": requires_verification,
        "noise_ratio": noise_ratio
    }

