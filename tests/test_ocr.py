import unittest
from backend.integrations.ocr import (
    assess_text_clarity,
    parse_biomarkers_from_text,
    apply_user_corrections,
    parse_number
)

class TestOCREngine(unittest.TestCase):
    """
    5 tests verifying:
    - Clean text parsing and structure
    - Blurry / noisy text assessment (requires_verification: true)
    - Handling missing reference ranges
    - Parsing challenges (Indian commas, < or > symbols)
    - User correction re-parsing & red flag updating
    """

    def test_01_parse_clean_report_text(self):
        sample = (
            "Hemoglobin 14.2 g/dL 13.0 - 17.0\n"
            "Total WBC 7200 /uL 4000 - 11000\n"
            "Platelets 260000 /uL 150000 - 450000"
        )
        biomarkers = parse_biomarkers_from_text(sample)
        self.assertEqual(len(biomarkers), 3)
        self.assertEqual(biomarkers[0]["name"], "Hemoglobin")
        self.assertEqual(biomarkers[0]["value"], 14.2)
        self.assertEqual(biomarkers[0]["reference_low"], 13.0)
        self.assertEqual(biomarkers[0]["reference_high"], 17.0)

    def test_02_assess_blurry_noisy_text(self):
        noisy_text = "????~~~____|||| H3m0gl0b1n ..### 13..5 g/dL ???~~~"
        requires_verification, noise_ratio = assess_text_clarity(noisy_text)
        self.assertTrue(requires_verification)
        self.assertGreater(noise_ratio, 0.15)

    def test_03_parse_missing_reference_range(self):
        text = "C-Reactive Protein 12.5 mg/L\nESR 22 mm/hr 0 - 20"
        biomarkers = parse_biomarkers_from_text(text)
        self.assertEqual(len(biomarkers), 2)
        crp = biomarkers[0]
        self.assertIsNone(crp["reference_low"])
        self.assertIsNone(crp["reference_high"])
        self.assertEqual(crp["status"], "no_range_on_report")

    def test_04_parse_ocr_challenges_special_tokens(self):
        text = (
            "TSH < 0.5 uIU/mL 0.4 - 4.2\n"
            "Platelet Count 3,25,000 /cumm 150000 - 450000"
        )
        biomarkers = parse_biomarkers_from_text(text)
        self.assertEqual(len(biomarkers), 2)
        self.assertEqual(biomarkers[0]["value"], 0.5)
        self.assertEqual(biomarkers[1]["value"], 325000.0)

    def test_05_apply_user_corrections_recalculation(self):
        corrected = "Serum Potassium 6.5 mmol/L 3.5 - 5.0"
        res = apply_user_corrections(corrected)
        self.assertEqual(len(res["biomarkers"]), 1)
        self.assertEqual(res["biomarkers"][0]["value"], 6.5)
        # Should now trigger Potassium emergency red flag!
        self.assertEqual(len(res["red_flags"]), 1)
        self.assertEqual(res["red_flags"][0]["urgency"], "EMERGENCY")

if __name__ == "__main__":
    unittest.main()

