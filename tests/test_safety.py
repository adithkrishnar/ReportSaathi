import unittest
from backend.safety.rules import (
    evaluate_biomarker,
    check_red_flags,
    MANDATORY_DISCLAIMER
)
from backend.safety.banned_phrases import (
    contains_banned_phrases,
    sanitize_ai_output
)

class TestSafetyEngine(unittest.TestCase):
    """
    13 safety tests verifying:
    - Normal range evaluation
    - Borderline boundary classification (within 5% buffer)
    - Needs attention (out of range) classification
    - Strict missing range handling ('no_range_on_report')
    - 5 Deterministic Red Flag emergency triggers
    - 4 Banned phrase & diagnostic suppression tests
    """

    def test_01_evaluate_normal_biomarker(self):
        status, _ = evaluate_biomarker("Hemoglobin", 14.0, "g/dL", 12.0, 16.0)
        self.assertEqual(status, "normal")

    def test_02_evaluate_borderline_low(self):
        # Range: 10.0 - 20.0 (span 10.0, 5% buffer is 0.5; 10.0 to 10.5 is borderline)
        status, _ = evaluate_biomarker("BiomarkerX", 10.3, "mg/dL", 10.0, 20.0)
        self.assertEqual(status, "borderline")

    def test_03_evaluate_borderline_high(self):
        # Range: 10.0 - 20.0 (19.5 to 20.0 is borderline)
        status, _ = evaluate_biomarker("BiomarkerX", 19.8, "mg/dL", 10.0, 20.0)
        self.assertEqual(status, "borderline")

    def test_04_evaluate_needs_attention_below_range(self):
        status, _ = evaluate_biomarker("Hemoglobin", 9.5, "g/dL", 12.0, 16.0)
        self.assertEqual(status, "needs_attention")

    def test_05_evaluate_needs_attention_above_range(self):
        status, _ = evaluate_biomarker("Total Cholesterol", 242.0, "mg/dL", 125.0, 200.0)
        self.assertEqual(status, "needs_attention")

    def test_06_evaluate_missing_range_strict_discipline(self):
        # Never invent population ranges
        status, text = evaluate_biomarker("CRP", 12.5, "mg/L", None, None)
        self.assertEqual(status, "no_range_on_report")
        self.assertIn("No reference range was printed", text)

    def test_07_red_flag_potassium_hyperkalemia_and_hypokalemia(self):
        high_k = [{"name": "Serum Potassium", "value": 6.8, "unit": "mmol/L"}]
        alerts_high = check_red_flags(high_k)
        self.assertEqual(len(alerts_high), 1)
        self.assertEqual(alerts_high[0]["urgency"], "EMERGENCY")
        self.assertIn("Hyperkalemia", alerts_high[0]["message"])

        low_k = [{"name": "Potassium", "value": 2.4, "unit": "mmol/L"}]
        alerts_low = check_red_flags(low_k)
        self.assertEqual(len(alerts_low), 1)
        self.assertIn("Hypokalemia", alerts_low[0]["message"])

    def test_08_red_flag_critical_platelets(self):
        crit_plt = [{"name": "Platelet Count", "value": 15000, "unit": "/uL"}]
        alerts = check_red_flags(crit_plt)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["urgency"], "EMERGENCY")
        self.assertIn("Thrombocytopenia", alerts[0]["message"])

    def test_09_red_flag_critical_hemoglobin(self):
        crit_hb = [{"name": "Hemoglobin", "value": 6.2, "unit": "g/dL"}]
        alerts = check_red_flags(crit_hb)
        self.assertEqual(len(alerts), 1)
        self.assertIn("Life-threatening Anemia", alerts[0]["message"])

    def test_10_red_flag_glucose_extremes(self):
        hypo = [{"name": "Blood Glucose Fasting", "value": 45, "unit": "mg/dL"}]
        alerts_hypo = check_red_flags(hypo)
        self.assertEqual(len(alerts_hypo), 1)
        self.assertIn("Hypoglycemia", alerts_hypo[0]["message"])

        hyper = [{"name": "Random Blood Sugar", "value": 380, "unit": "mg/dL"}]
        alerts_hyper = check_red_flags(hyper)
        self.assertEqual(len(alerts_hyper), 1)
        self.assertIn("DKA", alerts_hyper[0]["message"])

    def test_11_red_flag_creatinine_acute_renal_failure(self):
        crit_cr = [{"name": "Serum Creatinine", "value": 5.4, "unit": "mg/dL"}]
        alerts = check_red_flags(crit_cr)
        self.assertEqual(len(alerts), 1)
        self.assertIn("kidney impairment", alerts[0]["message"])

    def test_12_banned_diagnosis_and_dosage_detection(self):
        unsafe_diag = "Based on this report, you have diabetes."
        unsafe_dose = "You should stop taking your medication immediately."
        self.assertTrue(contains_banned_phrases(unsafe_diag))
        self.assertTrue(contains_banned_phrases(unsafe_dose))

    def test_13_sanitize_ai_output_replaces_with_clinical_fallbacks(self):
        unsafe_text = "The results prove you have diabetes. Please discontinue your medication."
        sanitized, was_modified = sanitize_ai_output(unsafe_text)
        self.assertTrue(was_modified)
        self.assertNotIn("you have diabetes", sanitized)
        self.assertNotIn("discontinue your medication", sanitized)
        self.assertIn("treating physician", sanitized)

if __name__ == "__main__":
    unittest.main()

