from typing import Dict, List, Optional, Tuple, Any

MANDATORY_DISCLAIMER = "This explains your report. It does not replace your doctor."

def evaluate_biomarker(
    name: str,
    value: float,
    unit: str,
    low: Optional[float] = None,
    high: Optional[float] = None
) -> Tuple[str, str]:
    """
    Evaluates a biomarker value against printed reference ranges on the report.
    Rules:
    - If low or high is None/not provided: 'no_range_on_report'
    - Within 5% of boundaries: 'borderline'
    - Outside printed range (< low or > high): 'needs_attention'
    - Strictly inside (beyond 5% buffer): 'normal'
    Returns: (status, interpretation_text)
    """
    if low is None or high is None:
        return (
            "no_range_on_report",
            f"No reference range was printed for {name} on this report. "
            "Please check with your doctor to interpret this value in context of your health."
        )

    if low >= high:
        # Edge case protection for inverted or identical ranges
        if value < low:
            return ("needs_attention", f"Value {value} {unit} is below the printed range minimum ({low} {unit}).")
        elif value > high:
            return ("needs_attention", f"Value {value} {unit} is above the printed range maximum ({high} {unit}).")
        else:
            return ("normal", f"Value {value} {unit} matches the reference value ({low} {unit}).")

    span = high - low
    buffer = 0.05 * span

    if value < low:
        return ("needs_attention", f"Value {value} {unit} is below the printed range ({low} - {high} {unit}).")
    elif value > high:
        return ("needs_attention", f"Value {value} {unit} is above the printed range ({low} - {high} {unit}).")
    elif (value - low) <= buffer:
        return ("borderline", f"Value {value} {unit} is borderline low, near the lower boundary ({low} {unit}).")
    elif (high - value) <= buffer:
        return ("borderline", f"Value {value} {unit} is borderline high, near the upper boundary ({high} {unit}).")
    else:
        return ("normal", f"Value {value} {unit} is within the printed reference range ({low} - {high} {unit}).")


def check_red_flags(biomarkers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministic rule engine checking for immediate life-threatening emergency thresholds.
    MUST run programmatically BEFORE any AI explanation.
    Critical Thresholds:
    - Potassium: >= 6.2 mmol/L (Severe Hyperkalemia) or <= 2.8 mmol/L (Severe Hypokalemia)
    - Platelets: <= 20,000 /uL (Critical Thrombocytopenia)
    - Hemoglobin: <= 7.0 g/dL (Severe Life-Threatening Anemia)
    - Glucose: <= 50 mg/dL (Severe Hypoglycemia) or >= 350 mg/dL (DKA/HHS risk)
    - Creatinine: >= 5.0 mg/dL (Acute Renal Failure)
    """
    alerts: List[Dict[str, Any]] = []

    for b in biomarkers:
        name = str(b.get("name", "")).strip().lower()
        val = b.get("value")
        if val is None:
            continue
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            continue
            
        unit = str(b.get("unit", "")).strip()

        # Potassium
        if "potassium" in name or name == "k+":
            if val_float >= 6.2:
                alerts.append({
                    "biomarker": b.get("name", "Potassium"),
                    "value": val_float,
                    "unit": unit or "mmol/L",
                    "threshold_rule": ">= 6.2 mmol/L",
                    "message": "CRITICAL EMERGENCY: Potassium is severely high (Severe Hyperkalemia). Risk of life-threatening cardiac arrhythmia. Seek immediate emergency medical care.",
                    "urgency": "EMERGENCY"
                })
            elif val_float <= 2.8:
                alerts.append({
                    "biomarker": b.get("name", "Potassium"),
                    "value": val_float,
                    "unit": unit or "mmol/L",
                    "threshold_rule": "<= 2.8 mmol/L",
                    "message": "CRITICAL EMERGENCY: Potassium is dangerously low (Severe Hypokalemia). Risk of dangerous heart rhythms and muscle paralysis. Seek immediate medical attention.",
                    "urgency": "EMERGENCY"
                })

        # Platelets
        elif "platelet" in name or "plt" in name:
            if val_float <= 20000:
                alerts.append({
                    "biomarker": b.get("name", "Platelet Count"),
                    "value": val_float,
                    "unit": unit or "/uL",
                    "threshold_rule": "<= 20,000 /uL",
                    "message": "CRITICAL EMERGENCY: Platelet count is critically low (Severe Thrombocytopenia). High risk of spontaneous internal or mucosal bleeding. Seek immediate hospital evaluation.",
                    "urgency": "EMERGENCY"
                })

        # Hemoglobin
        elif "hemoglobin" in name or name == "hb":
            if val_float <= 7.0:
                alerts.append({
                    "biomarker": b.get("name", "Hemoglobin"),
                    "value": val_float,
                    "unit": unit or "g/dL",
                    "threshold_rule": "<= 7.0 g/dL",
                    "message": "CRITICAL EMERGENCY: Hemoglobin is severely low (Life-threatening Anemia). Oxygen delivery to vital organs is compromised. Immediate medical assessment or transfusion consultation is required.",
                    "urgency": "EMERGENCY"
                })

        # Glucose
        elif "glucose" in name or "sugar" in name or "rbs" in name or "fbs" in name:
            if val_float <= 50:
                alerts.append({
                    "biomarker": b.get("name", "Blood Glucose"),
                    "value": val_float,
                    "unit": unit or "mg/dL",
                    "threshold_rule": "<= 50 mg/dL",
                    "message": "CRITICAL EMERGENCY: Blood sugar is critically low (Severe Hypoglycemia). Risk of neuroglycopenia, loss of consciousness, or seizures. Consume fast-acting glucose immediately and get emergency help.",
                    "urgency": "EMERGENCY"
                })
            elif val_float >= 350:
                alerts.append({
                    "biomarker": b.get("name", "Blood Glucose"),
                    "value": val_float,
                    "unit": unit or "mg/dL",
                    "threshold_rule": ">= 350 mg/dL",
                    "message": "CRITICAL EMERGENCY: Blood glucose is extremely elevated (Risk of DKA / Hyperosmolar Hyperglycemic State). Requires urgent medical evaluation and stabilization.",
                    "urgency": "EMERGENCY"
                })

        # Creatinine
        elif "creatinine" in name:
            if val_float >= 5.0:
                alerts.append({
                    "biomarker": b.get("name", "Serum Creatinine"),
                    "value": val_float,
                    "unit": unit or "mg/dL",
                    "threshold_rule": ">= 5.0 mg/dL",
                    "message": "CRITICAL EMERGENCY: Creatinine is markedly elevated indicating acute or severe kidney impairment. Urgent nephrological or hospital evaluation needed.",
                    "urgency": "EMERGENCY"
                })

    return alerts

