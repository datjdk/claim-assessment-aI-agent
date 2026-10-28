# Claim Assessment Report — CLM-REJ-001
_Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human._

- Claim ID: CLM-REJ-001
- Assessment ID: ASM-e8a5323ab8
- Assessor: claim-agent (automated initial assessment)
- Assessment Date: 2026-10-28T11:31:17+00:00
- Policy ID / Version: POL-REJ-001 / 2026-B
- Policyholder: Morgan Sample (INDIVIDUAL, PH-REJ-001, not an insured member)
- Claim Type: OUTPATIENT
- Patient / Member: MEM-REJ-001
- Treatment / Event Dates: 2026-08-20 to 2026-08-20
- Diagnosis / Treatment (verified): — / Elective cosmetic rhinoplasty
- Diagnosis / Treatment (claimant-reported): — / Elective cosmetic rhinoplasty
- Submitted Amount / Currency: 2000.00 USD
- Audit reference: AUD-CLM-REJ-001-80274dd6

## 1. Document Review (Complete)
| Requirement | Document ID | Document Type | Required | Status | Submitted / Detected | Verification | Issues | Evidence | Citation |
|---|---|---|---|---|---|---|---|---|---|
| OP-REQ-1 | R-D1 | CLAIM_FORM | Yes | Complete | CLAIM_FORM / CLAIM_FORM | Verified | — | R-D1 | PC-01 |
| OP-REQ-2 | R-D2 | ITEMIZED_INVOICE | Yes | Complete | ITEMIZED_INVOICE / ITEMIZED_INVOICE | Verified | — | R-D2 | PC-02 |
| OP-REQ-3 | R-D3 | PAYMENT_RECEIPT | Yes | Complete | PAYMENT_RECEIPT / PAYMENT_RECEIPT | Verified | — | R-D3 | PC-03 |
| OP-REQ-4 | R-D4 | MEDICAL_REPORT | Yes | Complete | MEDICAL_REPORT / MEDICAL_REPORT | Verified | — | R-D4 | PC-04 |
| OP-REQ-5 | — | REFERRAL_LETTER | Conditional | Not applicable | — / — | — | Condition fact 'specialist_referral_required' not documented; requirement not triggered. | — | PC-05 |

Document-review conclusion: **Complete**
Outstanding requests: None

> **Assessor note (LLM draft, validated against report facts):** Outpatient document checklist concluded COMPLETE; required documents R-D1, R-D2, R-D3 and R-D4 were verified, and the conditional referral was not applicable; no outstanding requests or consistency issues.

## 2. Policy Verification (Not eligible)
| Check | Result | Verified Fact | Policy Clause | Citation | Evidence |
|---|---|---|---|---|---|
| Policy active on treatment date | Pass | Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-08-20 to 2026-08-20. | REJ-2.1 | PC-06 | policy_record:POL-REJ-001 |
| Member covered | Pass | Member MEM-REJ-001 covered 2026-01-01 to 2026-12-31. | REJ-2.2 | PC-07 | policy_record:POL-REJ-001 |
| Claim type / benefit covered | Pass | OUTPATIENT benefit included. | REJ-3.1 | PC-08 | policy_record:POL-REJ-001 |
| Waiting period | Pass | 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-08-20. | REJ-4.1 | PC-09 | policy_record:POL-REJ-001 |
| Claim submitted within deadline | Pass | Submitted 2026-08-27, 7 days after last treatment 2026-08-20; OUTPATIENT deadline 60 days (2026-10-19). | CSR-2.1 | PC-10 | rule_set:CSR-2026; claim_submission:CLM-REJ-001 |
| Exclusions | Fail | Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication. | REJ-6.4 | PC-11 | R-D4 |
| Remaining benefit limit | Pass | Remaining OUTPATIENT limit USD 1500.00 of 1500.00 as of 2026-08-26. | REJ-5.1 | PC-12 | ledger:LED-REJ-001-OP-2026 |

Policy-verification conclusion: **Not eligible**

> **Assessor note (LLM draft, validated against report facts):** Policy verification found the policy checks, but the exclusions check failed under clause REJ-6.4 with procedure classification COSMETIC_ELECTIVE and no documented medical indication; overall conclusion was INELIGIBLE.

## 3. Medical Necessity (Not supported)
- Diagnosis: —
- Treatment / procedure: Elective cosmetic rhinoplasty
- Clinical rationale: The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.
- Policy medical-necessity clause: REJ-3.2 (PC-13)
- Clinical rule reference: CR-002 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 7.1
- Supporting evidence: R-D4 p.1, Assessment; R-D4 p.1, Procedure; R-D4 p.1, Assessment; R-D4 p.1, Procedure
- Result: **Not supported**
- Outstanding concerns: None

> **Assessor note (LLM draft, validated against report facts):** Medical necessity was NOT_SUPPORTED under clinical rule CR-002; the treating practitioner documented elective cosmetic rhinoplasty and no medical indication or functional impairment, with policy clause REJ-3.2.

## 4. Benefit Calculation (Complete)
Status: **Complete** (USD)

| Component | Amount | Evidence / Policy Clause |
|---|---|---|
| Submitted amount | 2000.00 | R-D2 |
| Excluded amount | 2000.00 | REJ-6.4; REJ-5.2; REJ-5.1 |
| Eligible / covered amount | 0.00 | Calculation |
| Deductible | 0.00 | Policy cost-sharing clause |
| Copay | 0.00 | Policy cost-sharing clause |
| Coinsurance | 0.00 | Policy cost-sharing clause |
| Limit adjustment | 0.00 | Annual limit clause / ledger |
| **Insurer payable** | **0.00** | Calculation |
| **Member responsibility** | **2000.00** | Calculation |
| Remaining limit before → after | 1500.00 → 1500.00 | Benefit ledger |

- Calculation order: EXCLUSIONS (2000.00) → DEDUCTIBLE (0.00) → COPAY (0.00) → COINSURANCE (0.00) → ANNUAL_LIMIT (0.00)
- Clauses applied: REJ-6.4; REJ-5.2; REJ-5.1 (PC-11; PC-14; PC-12)
- Reconciliation: Pass

> **Assessor note (LLM draft, validated against report facts):** Benefit calculation was COMPLETE; submitted USD 2000.00, excluded USD 2000.00, eligible USD 0.00, insurer payable USD 0.00, member responsibility USD 2000.00, and remaining limit before and after was USD 1500.00.

## 5. Recommendation (Reject)
- Recommendation: **Reject**
- Recommended payable amount: 0.00
- Specific reasons:
  1. Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication. — Evidence: R-D4; Citations: PC-11
  2. Medical necessity NOT_SUPPORTED (CR-002): The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment. — Evidence: R-D4; clinical_rule:CR-002; Citations: PC-13
  3. Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00. — Evidence: R-D2; ledger:LED-REJ-001-OP-2026; R-D4; Citations: PC-11; PC-14; PC-12
- Escalations or reservations: None
- Next action / authorization owner: Route to human denial review; the denial notice must cite the clauses above. — Senior claims assessor (denial review)

> **Assessor note (LLM draft, validated against report facts):** Recommendation outcome was REJECT with recommended payable USD 0.00; reasons included exclusions failed under REJ-6.4, medical necessity NOT_SUPPORTED under CR-002, and calculation showing USD 2000.00 submitted and excluded, USD 0.00 insurer payable, USD 2000.00 member responsibility, and remaining limit USD 1500.00.

## 6. Policy Citations (Pass)
| Citation | Kind | Source Document | Version / Effective | Clause / Location | Relevant Wording | Supported Finding | Evidence |
|---|---|---|---|---|---|---|---|
| PC-01 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-1 — Section 4.1, Outpatient claim documents | CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed. | Document requirement CLAIM_FORM | R-D1 |
| PC-02 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-2 — Section 4.1, Outpatient claim documents | ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified. | Document requirement ITEMIZED_INVOICE | R-D2 |
| PC-03 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-3 — Section 4.1, Outpatient claim documents | PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed. | Document requirement PAYMENT_RECEIPT | R-D3 |
| PC-04 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-4 — Section 4.1, Outpatient claim documents | MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity. | Document requirement MEDICAL_REPORT | R-D4 |
| PC-05 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-5 — Section 4.1, Outpatient claim documents | REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation. | Document requirement REFERRAL_LETTER | — |
| PC-06 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-2.1 — Page 2, Section 2.1 | Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment. | Policy active on treatment date | policy_record:POL-REJ-001 |
| PC-07 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-2.2 — Page 2, Section 2.2 | Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force. | Member covered | policy_record:POL-REJ-001 |
| PC-08 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-3.1 — Page 4, Section 3.1 | We will pay for outpatient consultations, day procedures and treatment prescribed by a registered medical practitioner, subject to Sections 5 and 6. | Claim type / benefit covered | policy_record:POL-REJ-001 |
| PC-09 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-4.1 — Page 5, Section 4.1 | Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident. | Waiting period | policy_record:POL-REJ-001 |
| PC-10 | Rule | Fictional Claim Submission Rules CSR-2026 | 2026.1 / 2026-01-01 | CSR-2.1 — Section 2.1, Standard medical treatment | Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date. | Claim submitted within deadline | rule_set:CSR-2026; claim_submission:CLM-REJ-001 |
| PC-11 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-6.4 — Page 9, Section 6.4 | We will not pay for any cosmetic or aesthetic procedure, including rhinoplasty, performed to change appearance where there is no medical indication documented by the treating practitioner. This exclusion does not apply to reconstructive surgery required because of an accident or a documented functional impairment. | Exclusions; Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication.; Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.; Benefit calculation | R-D4; R-D2; ledger:LED-REJ-001-OP-2026 |
| PC-12 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-5.1 — Page 6, Section 5.1 | The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,500.00. | Remaining benefit limit; Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.; Benefit calculation | ledger:LED-REJ-001-OP-2026; R-D2; R-D4 |
| PC-13 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-3.2 — Page 4, Section 3.2 | Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner. | Medical necessity NOT_SUPPORTED (CR-002): The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.; Medical necessity | R-D4; clinical_rule:CR-002 |
| PC-14 | Policy | Fictional Standard Health Plan, Policy Wording 2026-B | 2026-B / 2026-01-01 | REJ-5.2 — Page 6, Section 5.2 | No deductible or coinsurance applies to outpatient benefits. The member pays a fixed copay of USD 20.00 for each outpatient visit. | Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.; Benefit calculation | R-D2; ledger:LED-REJ-001-OP-2026; R-D4 |

- Citation coverage check: Pass
- Report validation: Pass
- Explanations: Drafted (model recursive/flint-v1.0:free)

Assessment Status: **Ready for authorization**
Final Authorization Status: **Pending**

### Tool call log — AUD-CLM-REJ-001-80274dd6
Context version: ctx-1/fixtures-2026.10-1

```
 1 11:31:17 OK      verifyDocument(R-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:31:17 OK      verifyDocument(R-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:31:17 OK      verifyDocument(R-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:31:17 OK      verifyDocument(R-D4) -> FOUND MEDICAL_REPORT COMPLETE
 5 11:31:17 OK      documentReview(CHK-OUTPATIENT v1.2) -> COMPLETE: 4/4 COMPLETE
 6 11:31:17 OK      lookupPolicy(POL-REJ-001) -> FOUND v2026-B 6/7 PASS exclusions=FAIL remaining=1500.00
 7 11:31:17 OK      checkMedicalNecessity(null, ["Elective cosmetic rhinoplasty"]) -> NOT_SUPPORTED rule=CR-002
 8 11:31:17 OK      calculateBenefit(POL-REJ-001, OUTPATIENT, 2000.00) -> payable=0.00 member=2000.00 remaining=1500.00
 9 11:31:17 OK      decide() -> REJECT payable=0.00
10 11:31:37 OK      openrouter.chat(attempt 1) -> validation=PASS tokens=3785/2406 recursive/flint-v1.0:free id=gen-1793187078-mtBXRh2bF8fYwG8eTter
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (14361 chars): {"claim_id":"CLM-REJ-001","currency":"USD","document_review":{"checklis…
   ↳ response (1299 chars): { "document_review": "Outpatient document checklist concluded COMPLETE;…
11 11:31:37 OK      draftExplanations(recursive/flint-v1.0:free) -> DRAFTED attempts=1 served=recursive/flint-v1.0:free tokens=3785/2406
12 11:31:37 OK      validateReport() -> PASS citations=PASS reconciliation=PASS final_status=READY_FOR_AUTHORIZATION
```
