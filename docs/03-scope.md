ReportSaathi — Project Scope

Stage: 3 — Scope Definition

Owner: Person 1 — Product Strategy & Design Lead

Status: Draft — Pending Final Team Review and Confirmation

Source Documents: 01-problem.md (Stage 1) and 02-research.md (Stage 2)

1. Document Alignment & Source Reconciliation

This scope translates the clinical communication gaps, Indian regulatory rules, and technical risks identified in 01-problem.md and 02-research.md into actionable product boundaries.

Identified Conflicts & Ambiguities Marked for Team Confirmation

Handwritten Prescription Scope vs. Safety Risk: Both 01-problem.md and 02-research.md highlight handwritten prescriptions as a major user pain point (citing 36.8% poor comprehension in Das et al., 2025). However,  documents also flag handwritten OCR misinterpretation (e.g., look-alike drug names or misread decimal points) as a top safety hazard. Scope Decision: Full automated interpretation of messy handwritten prescriptions is postponed from the MVP; the MVP will prioritize printed laboratory reports and clearly printed prescriptions, flagging illegible or handwritten items for manual verification.

Discharge Summaries: Mentioned in 01-problem.md alongside lab reports and prescriptions, but 02-research.md focuses predominantly on laboratory reports and prescriptions. Scope Decision: Multi-page hospital discharge summaries are postponed to post-MVP due to layout complexity and higher clinical synthesis risk.

Target Languages: 01-problem.md lists Hindi, Kannada, Tamil, Marathi, and Bengali as examples, while the team proposal narrows the MVP to English, Hindi, and Kannada. Marked as a team proposal pending confirmation.

Audio / Voice Output: 01-problem.md briefly mentions "reading or listening" in regional languages, and 02-research.md notes low literacy barriers. Text-to-speech is not in the initial MVP proposal and is categorized under Later — Future Enhancements.

2. Project Objective

What ReportSaathi Will Accomplish: Provide a safe, non-clinical web tool that translates printed medical laboratory reports and clearly printed prescriptions into plain-language explanations in the user's preferred language.

Who the MVP Is Designed For: Patients without a medical background and family caregivers in India who need to understand their medical paperwork before or after a doctor consultation.

Core Problem Solved: Bridges the comprehension gap caused by clinical jargon, Latin prescription abbreviations (e.g., BD, TDS, SOS), raw numerical tables (where 62% of low-literacy/numeracy patients fail to identify out-of-range values per Zikmund-Fisher et al., 2014), and rushed outpatient consultations.

Value Provided: Replaces panic-inducing web searches and unverified general AI chats with calm, structured explanations strictly bounded to the report's printed reference ranges, accompanied by a customized 3both–5 question checklist for the patient's next doctor visit.

What It Deliberately Avoids: ReportSaathi is an educational comprehension aid—not a diagnostic engine, medical device, or telemedicine platform. It will never diagnose diseases, prescribe or alter medications, or invent medical reference ranges.

3. Core User Journey

The end-to-end user flow separates essential MVP steps from post-MVP enhancements:

Opening ReportSaathi (MVP): User accesses the responsive web application without mandatory account creation or login.

Selecting Preferred Language (MVP): User selects their reading language (proposed: English, Hindi, or Kannada) alongside a clear upfront consent and non-medical disclaimer notice.

Selecting Explanation Level (MVP — Proposed): User chooses how detailed the explanation should be (proposed: Simple, Standard, or Detailed) to match their health literacy comfort level.

Uploading a Medical Document (MVP): User uploads a clear photo or PDF of a printed laboratory report or printed prescription (proposed formats: PDF, JPG, JPEG, PNG; proposed limit: 10 MB).

Extracting Information Using OCR (MVP): The system extracts text, test names, numerical values, units, and printed reference ranges while redacting personal identifiers (PII) prior to AI processing.

Reviewing and Correcting Extracted Information (MVP): User views extracted values side-by-side with the uploaded document to verify accuracy and manually correct any OCR misreads before generating explanations.

Explaining Medical Terminology and Laboratory Values (MVP): System explains what each test or prescribed medicine generally represents in plain language, preserving original numbers, units, and prescribed dosage instructions.

Displaying Reference-Range-Based Value Status (MVP): System maps each lab result strictly against the reference range printed on that specific report (e.g., Within printed range, Above printed range, Below printed range, or Range not printed).

Showing Appropriate Medical Safety Warnings (MVP): Deterministic backend rules display standard medical disclaimers, uncertainty flags for unclear text, and urgent escalation notices if critical keywords or extreme deviations appear.

Generating Questions for the Doctor (MVP): System generates 3–5 practical, report-specific questions the patient or caregiver can ask their doctor or pharmacist.

Saving, Sharing, or Downloading Explanations (MVP / Partial Enhancement): Downloading a clean summary PDF belongs in the MVP; direct messaging/link sharing flows are proposed enhancements pending privacy review.

Providing Optional Feedback (MVP — Proposed): User can optionally rate whether the explanation was clear and helpful without submitting personal health data.

4. Feature Prioritization

MVP — Must Have (Essential for Safe Validation)

Feature

User Value

Dev Complexity

Medical Risk

Why Necessary for First Release

Document Upload (PDF/JPG/JPEG/PNG)

High

Low

Low

Core entry point to work with existing patient paperwork without hospital integration.

PII Redaction & Temporary Processing

High

Medium

Low

Essential to protect patient privacy and comply with Indian data protection principles.

OCR Extraction + Side-by-Side Verification

High

Medium

High

Prevents silent OCR decimal/unit errors from reaching the patient unchecked.

Printed-Range-Only Lab Value Mapping

High

Medium

Medium

Directly solves numerical confusion while preventing hallucinated clinical norms.

Plain-Language Term & Medicine Explainer

High

Medium

Medium

Core value proposition; translates medical jargon and frequency codes (BD/OD/SOS).

Deterministic Safety & Escalation Engine

High

Medium

High

Acts as a hard guardrail independent of the LLM to block diagnoses and flag urgent signs.

Doctor Visit Question Checklist (3–5 Qs)

High

Low

Low

Converts passive reading into active, productive doctor-patient communication.

PDF Summary Export

Medium

Low

Low

Allows patients to print or carry the plain-language summary and questions to their clinic.

Later — Future Enhancements (Post-MVP Validation)

Feature

User Value

Dev Complexity

Medical Risk

Rationale for Postponement

Handwritten Prescription Interpretation

High

High

Very High

High OCR error rate on cursive Indian prescriptions creates unacceptable drug-confusion risks for v1.

Multi-Page Hospital Discharge Summaries

Medium

High

High

Complex clinical narratives require advanced summarization validation not needed to prove core value.

Text-to-Speech (Audio Read-Aloud)

High

Medium

Low

Valuable for low-literacy users, but adds localization and audio UI complexity after text accuracy is proven.

Additional Indian Languages (Tamil, Marathi, Bengali, etc.)

High

Medium

Medium

Expanding beyond initial languages requires dedicated clinical translation verification per language.

Optional Encrypted Longitudinal History

Medium

High

Medium

Requires user authentication, long-term PHI storage, and DPDP consent/erasure workflows.

Never — Out of Scope (Violates Safety & Product Boundaries)

Feature

User Value

Dev Complexity

Medical Risk

Reason for Permanent Exclusion

Disease Diagnosis or Differential Lists

Misleading

Medium

Critical

Violates core safety boundaries, API terms, and triggers medical device regulation (SaMD).

Prescribing or Suggesting Medications/OTC/Home Remedies

Misleading

Medium

Critical

Constitutes unauthorized practice of medicine and risks harmful drug interactions.

Advising Dose Changes or Stopping Meds

Misleading

Low

Critical

Directly endangers patient safety; only the prescribing doctor may alter treatment plans.

Inventing Missing Reference Ranges

Low

Low

High

Reference ranges vary by lab equipment and methodology; external ranges cause false alarms or reassurance.

Raw Medical Imaging Interpretation (X-ray/MRI/CT)

Low

Very High

Critical

Out of scope; only text-based radiologist reports may be explained later if validated.

Live Doctor Teleconsultation Marketplace

Low

Very High

High

Shifts focus from a neutral comprehension companion ("Saathi") to a commercial clinical service.

5. Initial MVP Boundaries Evaluation

The table below evaluates proposed MVP decisions against 01-problem.md and 02-research.md:

Proposed Decision

Status

Strategic & Safety Evaluation

Web application

Confirmed Direction

Lowest friction across mobile and desktop browsers without requiring app store downloads.

English, Hindi, and Kannada

Team Proposal (Pending)

Aligns with regional language needs in 02-research.md; requires native medical review for Hindi and Kannada.

Simple, Standard, Detailed levels

Team Proposal (Pending)

Supports varying literacy levels (REALM findings), though prompt testing is needed to ensure all three levels remain strictly non-diagnostic.

PDF, JPG, JPEG, PNG uploads

Team Proposal (Pending)

Covers standard digital lab PDFs and smartphone camera photos.

10 MB upload limit

Team Proposal (Pending)

Reasonable technical cap for multi-page lab PDFs and high-res photos; confirm during architecture design.

OCR-based text extraction

Confirmed Requirement

Essential for reading existing patient documents; must focus on printed text in MVP.

Manual correction of extracted values

Confirmed Requirement

Critical safety control from 01-problem.md so users can fix misread numbers before explanation.

Printed-range-only lab explanations

Confirmed Requirement

Core non-negotiable guardrail; if a range is absent on the report, the system must state it is unavailable.

Prescription explanation without altering instructions

Confirmed Requirement

Explains general drug purpose and translates printed timing (e.g., BD to twice daily) while keeping exact doctor instructions intact.

Doctor consultation question generation

Confirmed Requirement

Core differentiator identified in both Stage 1 and Stage 2 documents.

Deterministic backend safety checks

Confirmed Requirement

Necessary to enforce hard rules (blocked terms, red-flag triggers) outside probabilistic LLM outputs.

PDF download and sharing

Partially Confirmed

Local PDF download is low-risk and confirmed for MVP; external link/WhatsApp sharing carries PHI exposure risks and should be postponed or restricted to local file download in MVP.

Optional feedback

Team Proposal (Pending)

Useful for validating comprehension gains, provided feedback logs exclude uploaded medical text.

Temporary document processing

Confirmed Requirement

Ephemeral processing minimizes privacy exposure and DPDP compliance overhead in MVP.

No mandatory registration or login

Confirmed Requirement

Removes adoption barriers for caregivers/patients and avoids storing user account databases in MVP.

Specific Postponement Decision — Handwritten Prescriptions: While handwritten prescriptions are a documented pain point (02-research.md), automated OCR of cursive handwriting poses a severe safety risk of misreading look-alike drug names or dosages. In the MVP, ReportSaathi will process printed laboratory reports and printed prescriptions. If a user uploads a handwritten document, the system will detect low OCR confidence and display a clear warning instructing the user to verify the prescription directly with their doctor or pharmacist rather than guessing.

6. Medical Safety Requirements

The following safety rules are non-negotiable for MVP release:

No Disease Diagnosis: The system must never name a disease as a diagnosis for the user (e.g., never state "You have diabetes" or "This indicates kidney failure").

No Treatment Recommendations: The system must never recommend therapies, lifestyle cures, dietary changes, supplements, or over-the-counter medicines.

No Medication Modifications: The system must never advise starting, stopping, skipping, or altering the dose or timing of any prescribed medication.

No Invented Reference Ranges: Lab values may only be compared against reference ranges explicitly printed on the uploaded report. If no range is printed, the system must state: "Reference range not printed on report—please confirm with your doctor."

Preservation of Original Values and Units: Every explanation must display the exact extracted numeric value, measurement unit (e.g., mg/dL, mmol/L), and printed frequency alongside the plain-language text.

Clear Communication of Uncertainty: Any blurry text, low-confidence OCR extraction, or unfamiliar abbreviation must be explicitly marked as "Unclear—please verify with your doctor or pharmacist" rather than guessed.

Mandatory User Verification Step: Users must be shown the extracted test values/medicine names and prompted to verify them against their original paper report before viewing the explanation.

Prominent Medical Disclaimers: Every screen and exported PDF must state clearly that ReportSaathi is an educational tool only, does not provide medical advice, and does not replace a qualified doctor.

Deterministic Safety Checks Independent of LLM: A rule-based backend layer must inspect inputs and outputs independently of the AI model to block prohibited diagnostic/prescriptive phrases and detect critical red-flag keywords.

Escalation Guidance for Urgent Findings: When extreme deviations or urgent clinical warning signs are detected, the system must display a calm, prominent notice advising prompt medical attention or urgent care consultation.

Qualified Medical Professional Sign-Off: A qualified medical doctor must review and approve the safety rules, red-flag triggers, disclaimer wording, and sample outputs across English, Hindi, and Kannada prior to production launch.

7. Privacy and Legal Boundaries

Based on the Indian regulatory landscape documented in 02-research.md, privacy and legal considerations are separated into confirmed operational requirements and areas requiring formal legal review.

Confirmed Operational Requirements (From Source Documents)

Digital Personal Data Protection (DPDP) Act, 2023 (In Force): ReportSaathi must obtain free, informed, specific, and unambiguous user consent before processing any uploaded medical document, preceded by a clear notice in English or supported 8th Schedule languages (Hindi, Kannada). Data processing must be strictly limited to generating the requested explanation, with reasonable security safeguards and immediate deletion mechanisms.

AI Provider Data Governance (Gemini API Terms, 2025): Unpaid/free AI API tiers prohibit submitting sensitive health information (PHI) and permit human review and model training on user data. ReportSaathi must use paid enterprise API tiers governed by Data Processing Addendums where user inputs are not used to train models.

ICMR Ethical Guidelines for AI in Healthcare (2023): Requires human oversight, transparency that AI is generating educational explanations, bias/accuracy monitoring across Indian languages, and strict prevention of autonomous clinical decision-making.

Non-SaMD Positioning (CDSCO Guidance): To avoid classification and regulatory licensing as Software as a Medical Device (SaMD), ReportSaathi must strictly remain a plain-language educational explainer without diagnostic or clinical decision-support claims.

Issues Requiring Legal Review Before Production

DPDP Rules Implementation Details: Procedural rules under Section 40 of the DPDP Act (covering exact breach notification timelines, standardized consent notice templates, and Data Protection Impact Assessment triggers) require legal verification as rules are notified.

Information Technology Act, 2000 & SPDI Rules Transition: Legal counsel must confirm interim compliance obligations regarding sensitive personal data handling during the transition from IT Act Section 43A / SPDI Rules to the DPDP framework.

Consumer Protection Act, 2019 & Liability Disclaimers: Legal review is required to ensure terms of use, disclaimers, and grievance redressal mechanisms adequately protect against product liability or misleading service claims in India.

Telemedicine & Healthcare Guidelines: Confirm that doctor-visit question generation and red-flag escalation notices do not inadvertently cross into regulated telemedicine practice guidelines.

Compliance Note: Implementing encryption, PII redaction, and disclaimers reduces technical risk, but does not by itself certify legal compliance. Formal legal sign-off is required before public release.

8. Data and Storage Scope

Information Processed: Uploaded document files (PDF/images), extracted raw text, structured test parameters (test name, value, unit, printed reference range), medicine names/schedules, selected language, explanation level, and optional anonymous feedback.

Temporary Storage Scope: Uploaded files and extracted text should reside strictly in transient/ephemeral storage solely for the duration of the active user session to perform OCR, user verification, and explanation generation.

Permanent Report History: Excluded from the MVP. Storing permanent user medical history introduces high security liability, requires user authentication, and triggers complex DPDP data retention and erasure workflows.

Document Deletion Mechanism: Documents and derived text must be automatically purged immediately upon session completion or within a short automated time-to-live (TTL) window, with a manual "Clear / Delete Now" button available to the user at any time.

Protection from Logs and Third-Party Services:

Application error logs, analytics events, and optional user feedback must never record uploaded images, raw OCR text, patient names, or medical values.

Personal identifiers (patient name, phone number, address, doctor/hospital IDs) should be redacted before sending text to external AI APIs.

Only paid, zero-data-retention / no-training API endpoints may be used.

Pending Technical Confirmations:

Storage Platform: Supabase is a proposed option for temporary storage/backend services, not a confirmed decision.

Exact Retention & Backup Policy: The exact session TTL (e.g., immediate purge vs. short-lived encrypted cache) and verification that automated cloud backups do not retain ephemeral uploads are pending technical confirmation.

9. Dependencies and Unresolved Decisions

Decision

Current Status

Why It Matters

OCR Technology

Unresolved / Pending Evaluation

Must accurately extract tables, decimal points, units, and Indian lab formats without misreading numbers.

AI Model / Provider

Proposed (Paid API tier required)

Must support English, Hindi, and Kannada accurately while guaranteeing no model training or human review on patient data.

Database and Storage

Proposed (Supabase under consideration)

Determines how ephemeral files are isolated, encrypted, and permanently purged without residual backups.

Medical Reviewer

Unassigned / Pending Confirmation

A qualified Indian medical doctor must audit safety rules, red-flag triggers, and regional language translations before launch.

Red-Flag Validation

Pending Clinical Review

Deterministic rules for urgent warnings must be clinically validated to avoid false panic or missed emergencies.

Privacy and Consent Flow

Drafted in Scope / Pending Legal Review

Consent notices in English, Hindi, and Kannada must satisfy DPDP Act, 2023 requirements before collecting user uploads.

Document Retention & Purge Policy

Pending Technical Confirmation

Exact TTL duration and backup exclusion rules must be defined to ensure ephemeral processing guarantees.

PDF Generation

Proposed for MVP / Implementation Pending

Client-side vs. server-side PDF generation affects whether explained health data ever touches persistent storage.

Sharing Implementation

Postponed / Pending Security Review

Direct link sharing risks exposing sensitive health data; local PDF download is safer for MVP.

Administrator Requirements

Unresolved / Pending Confirmation

Need to confirm if an internal dashboard is needed to review anonymized user feedback and safety trigger logs without viewing PHI.

Production Deployment

Pending Architecture & Sign-Off

Hosting region (e.g., India data residency considerations), SSL, and rate limiting must be finalized before launch.

10. MVP Success Criteria

The MVP will be considered complete and ready for controlled user testing when it meets all functional, safety, and privacy criteria below. (Note: Numeric accuracy percentages and latency benchmarks are marked as pending until baseline testing is conducted with real sample reports.)

Upload Functionality: Users can successfully upload valid PDF, JPG, JPEG, and PNG files within the agreed size limit and receive clear error messages for unsupported formats or oversized files.

OCR Extraction and Correction: The system extracts test names, values, units, and printed reference ranges into an editable verification screen where users can modify any misread field before generating explanations.

Explanation Quality: Explanations present clear, jargon-free summaries at the selected level without altering the meaning of the source document.

Language Support: All interface elements, consent notices, explanations, warnings, and doctor questions render accurately in English, Hindi, and Kannada (subject to native speaker and medical review).

Reference Range Accuracy: 100% of lab status labels rely exclusively on the reference range printed on the uploaded report; reports lacking printed ranges explicitly state that no range was provided.

Medical Safety: Zero occurrences of disease diagnosis, treatment advice, or dosage modification across a standardized safety test suite, verified by deterministic backend checks and qualified medical reviewer sign-off.

Prescription Instruction Preservation: Printed medication names, doses, and frequencies are preserved accurately alongside plain-language explanations of general drug purpose.

Doctor Question Generation: Every completed report analysis generates 3 to 5 relevant, non-prescriptive questions tailored to the user's specific report values or medicines.

Privacy and Deletion: Uploaded files and extracted text are automatically deleted after the session ends (or immediately upon user request), with zero PHI written to application logs.

PDF Generation: Users can download a clean, readable PDF containing the plain-language explanation, original values, doctor questions, and prominent medical disclaimers.

Performance & Accuracy Targets (Pending Validation): Specific benchmarks for OCR field extraction accuracy, end-to-end processing speed, and user comprehension improvement are pending validation during Stage 4/5 prototype testing.

11. Final Scope Recommendation

1. What the Team Should Build First (MVP Core)

Build a streamlined, no-login web application focused on printed laboratory reports and clearly printed prescriptions in English, Hindi, and Kannada. Prioritize the core safety loop: Upload $\rightarrow$ PII Redaction & OCR $\rightarrow$ Side-by-Side User Verification $\rightarrow$ Printed-Range-Only Explanation & Deterministic Safety Checks $\rightarrow$ 3–5 Doctor Questions $\rightarrow$ Local PDF Download, backed by automatic session deletion.

2. What Should Be Postponed (Post-MVP)

Handwritten prescription interpretation (postpone until OCR accuracy and clinical safety guardrails for handwriting are proven).

Multi-page hospital discharge summaries.

Text-to-speech audio playback and expansion to additional regional languages beyond the initial three.

Cloud link sharing and persistent user accounts / longitudinal health history.

3. What Should Never Be Implemented

Disease diagnosis, differential diagnosis, or symptom-checking predictions.

Prescribing, recommending, or suggesting changes to medications, doses, supplements, or home remedies.

Supplying external or invented laboratory reference ranges when missing from a report.

Direct interpretation of raw medical imaging (X-rays, MRIs, CT scans).

4. Most Important Risks to Resolve Before Development

OCR Reliability on Indian Lab Formats: Validate OCR accuracy on diverse, real-world Indian diagnostic lab layouts (multi-column tables, varied units, and skewed smartphone photos) before locking the architecture.

LLM Prompt Leakage vs. Deterministic Guardrails: Design and test strict prompt boundaries and deterministic backend filters so the AI never falls back on external medical reference ranges or diagnostic phrasing.

Medical Reviewer & Legal Onboarding: Secure a qualified Indian medical doctor to validate safety rules/red flags and obtain legal review of the DPDP consent notice and disclaimers prior to any public user testing.