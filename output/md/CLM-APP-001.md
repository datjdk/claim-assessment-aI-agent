# Claim Assessment Report — CLM-APP-001
_Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human._

- Claim ID: CLM-APP-001
- Assessment ID: ASM-9966348219
- Assessor: claim-agent (automated initial assessment)
- Assessment Date: 2026-10-28T11:30:39+00:00
- Policy ID / Version: POL-APP-001 / 2026-A
- Policyholder: Alex Example (INDIVIDUAL, PH-APP-001, insured as MEM-APP-001)
- Claim Type: OUTPATIENT
- Patient / Member: MEM-APP-001
- Treatment / Event Dates: 2026-09-15 to 2026-09-15
- Diagnosis / Treatment (verified): Acute bacterial sinusitis / Outpatient consultation; Prescribed treatment
- Diagnosis / Treatment (claimant-reported): Acute bacterial sinusitis / Outpatient consultation; Prescribed treatment
- Submitted Amount / Currency: 200.00 USD
- Audit reference: AUD-CLM-APP-001-ed700f0a

## 1. Document Review (Complete)
| Requirement | Document ID | Document Type | Required | Status | Submitted / Detected | Verification | Issues | Evidence | Citation |
|---|---|---|---|---|---|---|---|---|---|
| OP-REQ-1 | A-D1 | CLAIM_FORM | Yes | Complete | CLAIM_FORM / CLAIM_FORM | Verified | — | A-D1 | PC-01 |
| OP-REQ-2 | A-D2 | ITEMIZED_INVOICE | Yes | Complete | ITEMIZED_INVOICE / ITEMIZED_INVOICE | Verified | — | A-D2 | PC-02 |
| OP-REQ-3 | A-D3 | PAYMENT_RECEIPT | Yes | Complete | PAYMENT_RECEIPT / PAYMENT_RECEIPT | Verified | — | A-D3 | PC-03 |
| OP-REQ-4 | A-D4 | MEDICAL_REPORT | Yes | Complete | MEDICAL_REPORT / MEDICAL_REPORT | Verified | — | A-D4 | PC-04 |
| OP-REQ-5 | — | REFERRAL_LETTER | Conditional | Not applicable | — / — | — | Condition fact 'specialist_referral_required' not documented; requirement not triggered. | — | PC-05 |

Document-review conclusion: **Complete**
Outstanding requests: None

> **Assessor note (LLM draft, validated against report facts):** Checklist CHK-OUTPATIENT version 1.2 found required outpatient claim documents COMPLETE and VERIFIED; referral letter not applicable; no outstanding requests or consistency issues.

## 2. Policy Verification (Eligible)
| Check | Result | Verified Fact | Policy Clause | Citation | Evidence |
|---|---|---|---|---|---|
| Policy active on treatment date | Pass | Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. | APP-2.1 | PC-06 | policy_record:POL-APP-001 |
| Member covered | Pass | Member MEM-APP-001 covered 2026-01-01 to 2026-12-31. | APP-2.2 | PC-07 | policy_record:POL-APP-001 |
| Claim type / benefit covered | Pass | OUTPATIENT benefit included. | APP-3.1 | PC-08 | policy_record:POL-APP-001 |
| Waiting period | Pass | 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. | APP-4.1 | PC-09 | policy_record:POL-APP-001 |
| Claim submitted within deadline | Pass | Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14). | CSR-2.1 | PC-10 | rule_set:CSR-2026; claim_submission:CLM-APP-001 |
| Exclusions | Pass | Verified procedure classification MEDICAL matches no exclusion. | APP-6.1 | PC-11 | A-D4 |
| Remaining benefit limit | Pass | Remaining OUTPATIENT limit USD 800.00 of 1000.00 as of 2026-09-17. | APP-5.1 | PC-12 | ledger:LED-APP-001-OP-2026 |

Policy-verification conclusion: **Eligible**

> **Assessor note (LLM draft, validated against report facts):** Policy Fictional Essential Health Plan, Policy Wording 2026-A version 2026-A FOUND ELIGIBLE; policy active, member covered, OUTPATIENT benefit included, waiting period satisfied, submission within deadline, exclusions no match, remaining limit USD 800.00 of 1000.00.

## 3. Medical Necessity (Supported)
- Diagnosis: Acute bacterial sinusitis
- Treatment / procedure: Outpatient consultation; Prescribed treatment
- Clinical rationale: Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.
- Policy medical-necessity clause: APP-3.2 (PC-13)
- Clinical rule reference: CR-001 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 2.3
- Supporting evidence: A-D4 p.1, Assessment; A-D4 p.1, Plan; A-D4 p.1, Assessment
- Result: **Supported**
- Outstanding concerns: None

> **Assessor note (LLM draft, validated against report facts):** Medical necessity SUPPORTED under CR-001 for documented acute bacterial sinusitis; outpatient consultation and prescribed treatment appropriate; policy clause APP-3.2; evidence A-D4.

## 4. Benefit Calculation (Complete)
Status: **Complete** (USD)

| Component | Amount | Evidence / Policy Clause |
|---|---|---|
| Submitted amount | 200.00 | A-D2 |
| Excluded amount | 0.00 | APP-5.2; APP-5.3; APP-5.1 |
| Eligible / covered amount | 200.00 | Calculation |
| Deductible | 0.00 | Policy cost-sharing clause |
| Copay | 20.00 | Policy cost-sharing clause |
| Coinsurance | 0.00 | Policy cost-sharing clause |
| Limit adjustment | 0.00 | Annual limit clause / ledger |
| **Insurer payable** | **180.00** | Calculation |
| **Member responsibility** | **20.00** | Calculation |
| Remaining limit before → after | 800.00 → 620.00 | Benefit ledger |

- Calculation order: EXCLUSIONS (0.00) → DEDUCTIBLE (0.00) → COPAY (20.00) → COINSURANCE (0.00) → ANNUAL_LIMIT (0.00)
- Clauses applied: APP-5.2; APP-5.3; APP-5.1 (PC-14; PC-15; PC-12)
- Reconciliation: Pass

> **Assessor note (LLM draft, validated against report facts):** Calculation COMPLETE: submitted USD 200.00, excluded USD 0.00, eligible USD 200.00, deductible USD 0.00, copay USD 20.00, coinsurance USD 0.00, limit adjustment USD 0.00, insurer payable USD 180.00, member responsibility USD 20.00, remaining limit before USD 800.00, after USD 620.00.

## 5. Recommendation (Approve)
- Recommendation: **Approve**
- Recommended payable amount: 180.00
- Specific reasons:
  1. Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31. — Evidence: policy_record:POL-APP-001; Citations: PC-06; PC-07
  2. Submitted on time: Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14). — Evidence: rule_set:CSR-2026; claim_submission:CLM-APP-001; Citations: PC-10
  3. Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion. — Evidence: A-D4; policy_record:POL-APP-001; Citations: PC-08; PC-09; PC-11
  4. Medical necessity SUPPORTED (CR-001): Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis. — Evidence: A-D4; clinical_rule:CR-001; Citations: PC-13
  5. Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00. — Evidence: A-D2; ledger:LED-APP-001-OP-2026; A-D4; Citations: PC-14; PC-15; PC-12
- Escalations or reservations: None
- Next action / authorization owner: Send to an authorized approver to authorize payment of USD 180.00. — Claims approver

> **Assessor note (LLM draft, validated against report facts):** Recommendation outcome APPROVE, recommended payable USD 180.00; next action send to an authorized approver to authorize payment of USD 180.00.

## 6. Policy Citations (Pass)
| Citation | Kind | Source Document | Version / Effective | Clause / Location | Relevant Wording | Supported Finding | Evidence |
|---|---|---|---|---|---|---|---|
| PC-01 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-1 — Section 4.1, Outpatient claim documents | CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed. | Document requirement CLAIM_FORM | A-D1 |
| PC-02 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-2 — Section 4.1, Outpatient claim documents | ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified. | Document requirement ITEMIZED_INVOICE | A-D2 |
| PC-03 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-3 — Section 4.1, Outpatient claim documents | PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed. | Document requirement PAYMENT_RECEIPT | A-D3 |
| PC-04 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-4 — Section 4.1, Outpatient claim documents | MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity. | Document requirement MEDICAL_REPORT | A-D4 |
| PC-05 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-5 — Section 4.1, Outpatient claim documents | REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation. | Document requirement REFERRAL_LETTER | — |
| PC-06 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-2.1 — Page 2, Section 2.1 | Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment. | Policy active on treatment date; Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31. | policy_record:POL-APP-001 |
| PC-07 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-2.2 — Page 2, Section 2.2 | Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force. | Member covered; Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31. | policy_record:POL-APP-001 |
| PC-08 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-3.1 — Page 4, Section 3.1 | We will pay for outpatient consultations and treatment prescribed by a registered medical practitioner, subject to the limits and cost-sharing shown in Section 5. | Claim type / benefit covered; Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion. | policy_record:POL-APP-001; A-D4 |
| PC-09 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-4.1 — Page 5, Section 4.1 | Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident. | Waiting period; Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion. | policy_record:POL-APP-001; A-D4 |
| PC-10 | Rule | Fictional Claim Submission Rules CSR-2026 | 2026.1 / 2026-01-01 | CSR-2.1 — Section 2.1, Standard medical treatment | Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date. | Claim submitted within deadline; Submitted on time: Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14). | rule_set:CSR-2026; claim_submission:CLM-APP-001 |
| PC-11 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-6.1 — Page 8, Section 6.1 | We will not pay for cosmetic or aesthetic treatment performed to change appearance where there is no documented medical indication. | Exclusions; Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion. | A-D4; policy_record:POL-APP-001 |
| PC-12 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-5.1 — Page 6, Section 5.1 | The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,000.00. | Remaining benefit limit; Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.; Benefit calculation | ledger:LED-APP-001-OP-2026; A-D2; A-D4 |
| PC-13 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-3.2 — Page 4, Section 3.2 | Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner. | Medical necessity SUPPORTED (CR-001): Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.; Medical necessity | A-D4; clinical_rule:CR-001 |
| PC-14 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-5.2 — Page 6, Section 5.2 | No deductible applies to outpatient benefits under this plan. | Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.; Benefit calculation | A-D2; ledger:LED-APP-001-OP-2026; A-D4 |
| PC-15 | Policy | Fictional Essential Health Plan, Policy Wording 2026-A | 2026-A / 2026-01-01 | APP-5.3 — Page 6, Section 5.3 | The member pays a fixed copay of USD 20.00 for each outpatient visit. No coinsurance applies to outpatient benefits. | Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.; Benefit calculation | A-D2; ledger:LED-APP-001-OP-2026; A-D4 |

- Citation coverage check: Pass
- Report validation: Pass
- Explanations: Drafted (model recursive/flint-v1.0:free)

Assessment Status: **Ready for authorization**
Final Authorization Status: **Pending**

### Tool call log — AUD-CLM-APP-001-ed700f0a
Context version: ctx-1/fixtures-2026.10-1

```
 1 11:30:39 OK      verifyDocument(A-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:30:39 OK      verifyDocument(A-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:30:39 OK      verifyDocument(A-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:30:39 OK      verifyDocument(A-D4) -> FOUND MEDICAL_REPORT COMPLETE
 5 11:30:39 OK      documentReview(CHK-OUTPATIENT v1.2) -> COMPLETE: 4/4 COMPLETE
 6 11:30:39 OK      lookupPolicy(POL-APP-001) -> FOUND v2026-A 7/7 PASS remaining=800.00
 7 11:30:39 OK      checkMedicalNecessity("Acute bacterial sinusitis", ["Outpatient consultation", "Prescribed treatment"]) -> SUPPORTED rule=CR-001
 8 11:30:39 OK      calculateBenefit(POL-APP-001, OUTPATIENT, 200.00) -> payable=180.00 member=20.00 remaining=620.00
 9 11:30:39 OK      decide() -> APPROVE payable=180.00
10 11:30:57 OK      openrouter.chat(attempt 1) -> validation=PASS tokens=4288/1936 recursive/flint-v1.0:free id=gen-1793187041-dQdYkp5hlAtu7PzSFvQB
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (15881 chars): {"claim_id":"CLM-APP-001","currency":"USD","document_review":{"checklis…
   ↳ response (1169 chars): {"document_review":"Checklist CHK-OUTPATIENT version 1.2 found required…
11 11:30:57 OK      draftExplanations(recursive/flint-v1.0:free) -> DRAFTED attempts=1 served=recursive/flint-v1.0:free tokens=4288/1936
12 11:30:57 OK      validateReport() -> PASS citations=PASS reconciliation=PASS final_status=READY_FOR_AUTHORIZATION
```
