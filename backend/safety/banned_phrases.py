import re
from typing import Tuple

MANDATORY_DISCLAIMER = "This explains your report. It does not replace your doctor."

BANNED_DIAGNOSIS_PATTERNS = [
    r"\byou\s+have\s+(?:diabetes|cancer|anemia|kidney\s+disease|hypertension|infection|leukemia)\b",
    r"\byou\s+are\s+suffering\s+from\b",
    r"\bconfirms\s+a\s+case\s+of\b",
    r"\bdiagnosed\s+with\b",
    r"\bthis\s+proves\s+you\s+have\b",
    r"\byou\s+are\s+free\s+of\s+disease\b",
    r"\byou\s+are\s+completely\s+healthy\b",
    r"\bthere\s+is\s+no\s+disease\b",
]

BANNED_DOSAGE_PATTERNS = [
    r"\bdiscontinue\s+(?:your\s+)?medication\b",
    r"\bstop\s+taking\s+(?:your\s+)?(?:medicine|tablets|pills|medication|insulin|dose)\b",
    r"\bincrease\s+(?:your\s+)?(?:dose|dosage)\b",
    r"\bdecrease\s+(?:your\s+)?(?:dose|dosage)\b",
    r"\bdouble\s+(?:your\s+)?dose\b",
    r"\bstart\s+taking\s+[a-z0-9\s]+\s+without\s+a\s+doctor\b",
    r"\bchange\s+(?:your\s+)?dosage\b",
]

BANNED_PHYSICIAN_BYPASS_PATTERNS = [
    r"\bno\s+need\s+to\s+see\s+(?:a|your)\s+doctor\b",
    r"\byou\s+don['’]?t\s+need\s+a\s+doctor\b",
    r"\bskip\s+(?:your\s+)?doctor\s+visit\b",
    r"\byou\s+can\s+treat\s+this\s+at\s+home\s+instead\s+of\s+seeing\s+a\s+doctor\b",
]

ALL_BANNED_PATTERNS = (
    BANNED_DIAGNOSIS_PATTERNS +
    BANNED_DOSAGE_PATTERNS +
    BANNED_PHYSICIAN_BYPASS_PATTERNS
)

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in ALL_BANNED_PATTERNS]

SAFETY_FALLBACK_REPLACEMENTS = {
    "diagnosis": "Lab values reflect specific measurements and cannot determine a medical diagnosis on their own. Please consult your physician for an accurate medical evaluation.",
    "medication": "Any changes to medication dosage or schedules must only be directed by your treating physician.",
    "bypass": "Always consult your healthcare provider to discuss your lab results."
}

def contains_banned_phrases(text: str) -> bool:
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False

def sanitize_ai_output(text: str) -> Tuple[str, bool]:
    """
    Scans AI-generated text for any banned diagnostic, dosage, or bypass statements.
    Replaces detected safety violations with approved clinical disclaimers.
    Returns (sanitized_text, was_modified).
    """
    modified = False
    sanitized = text

    for pattern in [re.compile(p, re.IGNORECASE) for p in BANNED_DIAGNOSIS_PATTERNS]:
        if pattern.search(sanitized):
            sanitized = pattern.sub(f"[{SAFETY_FALLBACK_REPLACEMENTS['diagnosis']}]", sanitized)
            modified = True

    for pattern in [re.compile(p, re.IGNORECASE) for p in BANNED_DOSAGE_PATTERNS]:
        if pattern.search(sanitized):
            sanitized = pattern.sub(f"[{SAFETY_FALLBACK_REPLACEMENTS['medication']}]", sanitized)
            modified = True

    for pattern in [re.compile(p, re.IGNORECASE) for p in BANNED_PHYSICIAN_BYPASS_PATTERNS]:
        if pattern.search(sanitized):
            sanitized = pattern.sub(f"[{SAFETY_FALLBACK_REPLACEMENTS['bypass']}]", sanitized)
            modified = True

    return sanitized, modified

