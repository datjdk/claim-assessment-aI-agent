# Claim Assessment Report — CLM-APP-001
_Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human._

- Claim ID: CLM-APP-001
- Assessment ID: ASM-da7aef3d69
- Assessor: claim-agent (automated initial assessment)
- Assessment Date: 2026-10-28T11:02:27+00:00
- Policy ID / Version: POL-APP-001 / 2026-A
- Policyholder: Alex Example (INDIVIDUAL, PH-APP-001, insured as MEM-APP-001)
- Claim Type: OUTPATIENT
- Patient / Member: MEM-APP-001
- Treatment / Event Dates: 2026-09-15 to 2026-09-15
- Diagnosis / Treatment (verified): Acute bacterial sinusitis / Outpatient consultation; Prescribed treatment
- Diagnosis / Treatment (claimant-reported): Acute bacterial sinusitis / Outpatient consultation; Prescribed treatment
- Submitted Amount / Currency: 200.00 USD
- Audit reference: AUD-CLM-APP-001-3f2b8b18

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

## 3. Medical Necessity (Supported)
- Diagnosis: Acute bacterial sinusitis
- Treatment / procedure: Outpatient consultation; Prescribed treatment
- Clinical rationale: Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.
- Policy medical-necessity clause: APP-3.2 (PC-13)
- Clinical rule reference: CR-001 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 2.3
- Supporting evidence: A-D4 p.1, Assessment; A-D4 p.1, Plan; A-D4 p.1, Assessment
- Result: **Supported**
- Outstanding concerns: None

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
- Explanations: Failed

Assessment Status: **Ready for authorization**
Final Authorization Status: **Pending**

### Tool call log — AUD-CLM-APP-001-3f2b8b18
Context version: ctx-1/fixtures-2026.10-1

```
 1 11:02:27 OK      verifyDocument(A-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:02:27 OK      verifyDocument(A-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:02:27 OK      verifyDocument(A-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:02:27 OK      verifyDocument(A-D4) -> FOUND MEDICAL_REPORT COMPLETE
 5 11:02:27 OK      documentReview(CHK-OUTPATIENT v1.2) -> COMPLETE: 4/4 COMPLETE
 6 11:02:27 OK      lookupPolicy(POL-APP-001) -> FOUND v2026-A 7/7 PASS remaining=800.00
 7 11:02:27 OK      checkMedicalNecessity("Acute bacterial sinusitis", ["Outpatient consultation", "Prescribed treatment"]) -> SUPPORTED rule=CR-001
 8 11:02:27 OK      calculateBenefit(POL-APP-001, OUTPATIENT, 200.00) -> payable=180.00 member=20.00 remaining=620.00
 9 11:02:27 OK      decide() -> APPROVE payable=180.00
10 11:02:28 ERROR   openrouter.chat(attempt 1) -> error: OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (15881 chars): {"claim_id":"CLM-APP-001","currency":"USD","document_review":{"checklis…
11 11:02:28 ERROR   draftExplanations(anthropic/claude-haiku-) -> FAILED attempts=1
12 11:02:28 OK      validateReport() -> PASS citations=PASS reconciliation=PASS final_status=READY_FOR_AUTHORIZATION
```

### LLM request and response (OpenRouter)

**LLM call #11 draftExplanations -> FAILED (attempts=1)**  
Request: POST https://openrouter.ai/api/v1/chat/completions  model=anthropic/claude-haiku-  temperature=0.0  max_tokens=1000  (Authorization header not shown)  
**--- request message 1: system (603 chars)**  
```
You draft explanations for a human insurance claim assessor.
Rules:
- Use only the facts in the supplied JSON. Do not add clinical, policy or financial information.
- Do not make, change or question the recommendation. The application decided it; you explain it.
- Mention only clause IDs, document IDs and amounts that appear in the facts. Write amounts with two decimals exactly as given.
- Reply with one JSON object and nothing else. Its keys must be exactly: document_review, policy_verification, medical_necessity, benefit_calculation, recommendation. Each value is a short plain-text explanation.
```
**--- request message 2: user (15881 chars)**  
```
{"claim_id":"CLM-APP-001","currency":"USD","document_review":{"checklist":{"id":"CHK-OUTPATIENT","version":"1.2","source":{"document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","location":"Section 4.1, Outpatient claim documents"}},"rows":[{"document_type":"CLAIM_FORM","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-1","document_id":"A-D1","submitted_type":"CLAIM_FORM","detected_type":"CLAIM_FORM","verification":"VERIFIED","issues":[],"evidence":["A-D1"],"citation_ids":["PC-01"]},{"document_type":"ITEMIZED_INVOICE","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-2","document_id":"A-D2","submitted_type":"ITEMIZED_INVOICE","detected_type":"ITEMIZED_INVOICE","verification":"VERIFIED","issues":[],"evidence":["A-D2"],"citation_ids":["PC-02"]},{"document_type":"PAYMENT_RECEIPT","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-3","document_id":"A-D3","submitted_type":"PAYMENT_RECEIPT","detected_type":"PAYMENT_RECEIPT","verification":"VERIFIED","issues":[],"evidence":["A-D3"],"citation_ids":["PC-03"]},{"document_type":"MEDICAL_REPORT","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-4","document_id":"A-D4","submitted_type":"MEDICAL_REPORT","detected_type":"MEDICAL_REPORT","verification":"VERIFIED","issues":[],"evidence":["A-D4"],"citation_ids":["PC-04"]},{"document_type":"REFERRAL_LETTER","required":"CONDITIONAL","status":"NOT_APPLICABLE","requirement_id":"OP-REQ-5","document_id":null,"submitted_type":null,"detected_type":null,"verification":null,"issues":["Condition fact 'specialist_referral_required' not documented; requirement not triggered."],"evidence":[],"citation_ids":["PC-05"]}],"conclusion":"COMPLETE","outstanding_requests":[],"consistency_issues":[]},"policy_verification":{"status":"FOUND","policy_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","checks":[{"check":"policy_active","label":"Policy active on treatment date","result":"PASS","verified_fact":"Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15.","clause_ids":["APP-2.1"],"rule_ids":[],"citation_ids":["PC-06"],"evidence":["policy_record:POL-APP-001"]},{"check":"member_covered","label":"Member covered","result":"PASS","verified_fact":"Member MEM-APP-001 covered 2026-01-01 to 2026-12-31.","clause_ids":["APP-2.2"],"rule_ids":[],"citation_ids":["PC-07"],"evidence":["policy_record:POL-APP-001"]},{"check":"benefit_covered","label":"Claim type / benefit covered","result":"PASS","verified_fact":"OUTPATIENT benefit included.","clause_ids":["APP-3.1"],"rule_ids":[],"citation_ids":["PC-08"],"evidence":["policy_record:POL-APP-001"]},{"check":"waiting_period","label":"Waiting period","result":"PASS","verified_fact":"30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15.","clause_ids":["APP-4.1"],"rule_ids":[],"citation_ids":["PC-09"],"evidence":["policy_record:POL-APP-001"]},{"check":"submission_deadline","label":"Claim submitted within deadline","result":"PASS","verified_fact":"Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14).","clause_ids":[],"rule_ids":["CSR-2.1"],"citation_ids":["PC-10"],"evidence":["rule_set:CSR-2026","claim_submission:CLM-APP-001"]},{"check":"exclusions","label":"Exclusions","result":"PASS","verified_fact":"Verified procedure classification MEDICAL matches no exclusion.","clause_ids":["APP-6.1"],"rule_ids":[],"citation_ids":["PC-11"],"evidence":["A-D4"]},{"check":"limit","label":"Remaining benefit limit","result":"PASS","verified_fact":"Remaining OUTPATIENT limit USD 800.00 of 1000.00 as of 2026-09-17.","clause_ids":["APP-5.1"],"rule_ids":[],"citation_ids":["PC-12"],"evidence":["ledger:LED-APP-001-OP-2026"]}],"remaining_limit":"800.00","conclusion":"ELIGIBLE","reason":null},"medical_necessity":{"diagnosis":"Acute bacterial sinusitis","procedures":["Outpatient consultation","Prescribed treatment"],"result":"SUPPORTED","rule_id":"CR-001","rationale":"Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.","clinical_source":"Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 2.3","rule_set_version":"1.0","policy_clause_ids":["APP-3.2"],"citation_ids":["PC-13"],"evidence":[{"value":"Acute bacterial sinusitis","document_id":"A-D4","location":"p.1, Assessment"},{"value":["Outpatient consultation","Prescribed treatment"],"document_id":"A-D4","location":"p.1, Plan"},{"value":true,"document_id":"A-D4","location":"p.1, Assessment"}],"outstanding_concerns":[]},"benefit_calculation":{"status":"COMPLETE","currency":"USD","submitted":"200.00","excluded":"0.00","eligible":"200.00","deductible":"0.00","copay":"20.00","coinsurance":"0.00","limit_adjustment":"0.00","insurer_payable":"180.00","member_responsibility":"20.00","remaining_limit_before":"800.00","remaining_limit_after":"620.00","steps":[{"step":"EXCLUSIONS","amount":"0.00","detail":"Verified procedure classification MEDICAL matches no exclusion."},{"step":"DEDUCTIBLE","amount":"0.00","detail":"Deductible 0.00."},{"step":"COPAY","amount":"20.00","detail":"Copay 20.00 x 1 visit(s), capped at the amount left."},{"step":"COINSURANCE","amount":"0.00","detail":"Coinsurance rate 0.00."},{"step":"ANNUAL_LIMIT","amount":"0.00","detail":"Payable capped at remaining limit 800.00."}],"clause_ids":["APP-5.2","APP-5.3","APP-5.1"],"citation_ids":["PC-14","PC-15","PC-12"],"evidence":["A-D2","ledger:LED-APP-001-OP-2026","A-D4"],"pending_reasons":[]},"recommendation":{"outcome":"APPROVE","recommended_payable":"180.00","reasons":[{"finding":"Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31.","evidence":["policy_record:POL-APP-001"],"citation_ids":["PC-06","PC-07"]},{"finding":"Submitted on time: Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14).","evidence":["rule_set:CSR-2026","claim_submission:CLM-APP-001"],"citation_ids":["PC-10"]},{"finding":"Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion.","evidence":["A-D4","policy_record:POL-APP-001"],"citation_ids":["PC-08","PC-09","PC-11"]},{"finding":"Medical necessity SUPPORTED (CR-001): Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.","evidence":["A-D4","clinical_rule:CR-001"],"citation_ids":["PC-13"]},{"finding":"Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.","evidence":["A-D2","ledger:LED-APP-001-OP-2026","A-D4"],"citation_ids":["PC-14","PC-15","PC-12"]}],"information_requests":[],"escalations":[],"next_action":"Send to an authorized approver to authorize payment of USD 180.00.","authorization_owner":"Claims approver"},"policy_citations":{"citations":[{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-1","title":"CHK-OUTPATIENT CLAIM_FORM","location":"Section 4.1, Outpatient claim documents","text":"CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed.","citation_id":"PC-01","supported_findings":["Document requirement CLAIM_FORM"],"evidence_ids":["A-D1"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-2","title":"CHK-OUTPATIENT ITEMIZED_INVOICE","location":"Section 4.1, Outpatient claim documents","text":"ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified.","citation_id":"PC-02","supported_findings":["Document requirement ITEMIZED_INVOICE"],"evidence_ids":["A-D2"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-3","title":"CHK-OUTPATIENT PAYMENT_RECEIPT","location":"Section 4.1, Outpatient claim documents","text":"PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed.","citation_id":"PC-03","supported_findings":["Document requirement PAYMENT_RECEIPT"],"evidence_ids":["A-D3"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-4","title":"CHK-OUTPATIENT MEDICAL_REPORT","location":"Section 4.1, Outpatient claim documents","text":"MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity.","citation_id":"PC-04","supported_findings":["Document requirement MEDICAL_REPORT"],"evidence_ids":["A-D4"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-5","title":"CHK-OUTPATIENT REFERRAL_LETTER","location":"Section 4.1, Outpatient claim documents","text":"REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation.","citation_id":"PC-05","supported_findings":["Document requirement REFERRAL_LETTER"],"evidence_ids":[]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-2.1","title":"Period of cover","location":"Page 2, Section 2.1","text":"Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment.","citation_id":"PC-06","supported_findings":["Policy active on treatment date","Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31."],"evidence_ids":["policy_record:POL-APP-001"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-2.2","title":"Insured members","location":"Page 2, Section 2.2","text":"Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force.","citation_id":"PC-07","supported_findings":["Member covered","Coverage established: Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-09-15 to 2026-09-15. Member MEM-APP-001 covered 2026-01-01 to 2026-12-31."],"evidence_ids":["policy_record:POL-APP-001"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-3.1","title":"Outpatient benefit","location":"Page 4, Section 3.1","text":"We will pay for outpatient consultations and treatment prescribed by a registered medical practitioner, subject to the limits and cost-sharing shown in Section 5.","citation_id":"PC-08","supported_findings":["Claim type / benefit covered","Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion."],"evidence_ids":["policy_record:POL-APP-001","A-D4"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-4.1","title":"Waiting period","location":"Page 5, Section 4.1","text":"Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident.","citation_id":"PC-09","supported_findings":["Waiting period","Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion."],"evidence_ids":["policy_record:POL-APP-001","A-D4"]},{"kind":"RULE","source_document":"Fictional Claim Submission Rules CSR-2026","version":"2026.1","effective_date":"2026-01-01","clause_id":"CSR-2.1","title":"CSR-2026","location":"Section 2.1, Standard medical treatment","text":"Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date.","citation_id":"PC-10","supported_findings":["Claim submitted within deadline","Submitted on time: Submitted 2026-09-18, 3 days after last treatment 2026-09-15; OUTPATIENT deadline 60 days (2026-11-14)."],"evidence_ids":["rule_set:CSR-2026","claim_submission:CLM-APP-001"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-6.1","title":"Cosmetic treatment exclusion","location":"Page 8, Section 6.1","text":"We will not pay for cosmetic or aesthetic treatment performed to change appearance where there is no documented medical indication.","citation_id":"PC-11","supported_findings":["Exclusions","Benefit applies: OUTPATIENT benefit included. 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-09-15. Verified procedure classification MEDICAL matches no exclusion."],"evidence_ids":["A-D4","policy_record:POL-APP-001"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-5.1","title":"Annual outpatient limit","location":"Page 6, Section 5.1","text":"The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,000.00.","citation_id":"PC-12","supported_findings":["Remaining benefit limit","Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.","Benefit calculation"],"evidence_ids":["ledger:LED-APP-001-OP-2026","A-D2","A-D4"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-3.2","title":"Medical necessity","location":"Page 4, Section 3.2","text":"Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner.","citation_id":"PC-13","supported_findings":["Medical necessity SUPPORTED (CR-001): Outpatient consultation and prescribed treatment are an appropriate response to documented acute bacterial sinusitis.","Medical necessity"],"evidence_ids":["A-D4","clinical_rule:CR-001"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-5.2","title":"Deductible","location":"Page 6, Section 5.2","text":"No deductible applies to outpatient benefits under this plan.","citation_id":"PC-14","supported_findings":["Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.","Benefit calculation"],"evidence_ids":["A-D2","ledger:LED-APP-001-OP-2026","A-D4"]},{"kind":"POLICY","source_document":"Fictional Essential Health Plan, Policy Wording 2026-A","version":"2026-A","effective_date":"2026-01-01","clause_id":"APP-5.3","title":"Outpatient copay","location":"Page 6, Section 5.3","text":"The member pays a fixed copay of USD 20.00 for each outpatient visit. No coinsurance applies to outpatient benefits.","citation_id":"PC-15","supported_findings":["Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member responsibility; remaining limit 800.00 -> 620.00.","Benefit calculation"],"evidence_ids":["A-D2","ledger:LED-APP-001-OP-2026","A-D4"]}]}}
```
**--- response attempt 1: ERROR OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}**  

# Claim Assessment Report — CLM-REJ-001
_Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human._

- Claim ID: CLM-REJ-001
- Assessment ID: ASM-e2d1c51e4b
- Assessor: claim-agent (automated initial assessment)
- Assessment Date: 2026-10-28T11:02:28+00:00
- Policy ID / Version: POL-REJ-001 / 2026-B
- Policyholder: Morgan Sample (INDIVIDUAL, PH-REJ-001, not an insured member)
- Claim Type: OUTPATIENT
- Patient / Member: MEM-REJ-001
- Treatment / Event Dates: 2026-08-20 to 2026-08-20
- Diagnosis / Treatment (verified): — / Elective cosmetic rhinoplasty
- Diagnosis / Treatment (claimant-reported): — / Elective cosmetic rhinoplasty
- Submitted Amount / Currency: 2000.00 USD
- Audit reference: AUD-CLM-REJ-001-6b5ad7de

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

## 3. Medical Necessity (Not supported)
- Diagnosis: —
- Treatment / procedure: Elective cosmetic rhinoplasty
- Clinical rationale: The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.
- Policy medical-necessity clause: REJ-3.2 (PC-13)
- Clinical rule reference: CR-002 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 7.1
- Supporting evidence: R-D4 p.1, Assessment; R-D4 p.1, Procedure; R-D4 p.1, Assessment; R-D4 p.1, Procedure
- Result: **Not supported**
- Outstanding concerns: None

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

## 5. Recommendation (Reject)
- Recommendation: **Reject**
- Recommended payable amount: 0.00
- Specific reasons:
  1. Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication. — Evidence: R-D4; Citations: PC-11
  2. Medical necessity NOT_SUPPORTED (CR-002): The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment. — Evidence: R-D4; clinical_rule:CR-002; Citations: PC-13
  3. Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00. — Evidence: R-D2; ledger:LED-REJ-001-OP-2026; R-D4; Citations: PC-11; PC-14; PC-12
- Escalations or reservations: None
- Next action / authorization owner: Route to human denial review; the denial notice must cite the clauses above. — Senior claims assessor (denial review)

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
- Explanations: Failed

Assessment Status: **Ready for authorization**
Final Authorization Status: **Pending**

### Tool call log — AUD-CLM-REJ-001-6b5ad7de
Context version: ctx-1/fixtures-2026.10-1

```
 1 11:02:28 OK      verifyDocument(R-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:02:28 OK      verifyDocument(R-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:02:28 OK      verifyDocument(R-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:02:28 OK      verifyDocument(R-D4) -> FOUND MEDICAL_REPORT COMPLETE
 5 11:02:28 OK      documentReview(CHK-OUTPATIENT v1.2) -> COMPLETE: 4/4 COMPLETE
 6 11:02:28 OK      lookupPolicy(POL-REJ-001) -> FOUND v2026-B 6/7 PASS exclusions=FAIL remaining=1500.00
 7 11:02:28 OK      checkMedicalNecessity(null, ["Elective cosmetic rhinoplasty"]) -> NOT_SUPPORTED rule=CR-002
 8 11:02:28 OK      calculateBenefit(POL-REJ-001, OUTPATIENT, 2000.00) -> payable=0.00 member=2000.00 remaining=1500.00
 9 11:02:28 OK      decide() -> REJECT payable=0.00
10 11:02:28 ERROR   openrouter.chat(attempt 1) -> error: OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (14361 chars): {"claim_id":"CLM-REJ-001","currency":"USD","document_review":{"checklis…
11 11:02:28 ERROR   draftExplanations(anthropic/claude-haiku-) -> FAILED attempts=1
12 11:02:28 OK      validateReport() -> PASS citations=PASS reconciliation=PASS final_status=READY_FOR_AUTHORIZATION
```

### LLM request and response (OpenRouter)

**LLM call #11 draftExplanations -> FAILED (attempts=1)**  
Request: POST https://openrouter.ai/api/v1/chat/completions  model=anthropic/claude-haiku-  temperature=0.0  max_tokens=1000  (Authorization header not shown)  
**--- request message 1: system (603 chars)**  
```
You draft explanations for a human insurance claim assessor.
Rules:
- Use only the facts in the supplied JSON. Do not add clinical, policy or financial information.
- Do not make, change or question the recommendation. The application decided it; you explain it.
- Mention only clause IDs, document IDs and amounts that appear in the facts. Write amounts with two decimals exactly as given.
- Reply with one JSON object and nothing else. Its keys must be exactly: document_review, policy_verification, medical_necessity, benefit_calculation, recommendation. Each value is a short plain-text explanation.
```
**--- request message 2: user (14361 chars)**  
```
{"claim_id":"CLM-REJ-001","currency":"USD","document_review":{"checklist":{"id":"CHK-OUTPATIENT","version":"1.2","source":{"document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","location":"Section 4.1, Outpatient claim documents"}},"rows":[{"document_type":"CLAIM_FORM","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-1","document_id":"R-D1","submitted_type":"CLAIM_FORM","detected_type":"CLAIM_FORM","verification":"VERIFIED","issues":[],"evidence":["R-D1"],"citation_ids":["PC-01"]},{"document_type":"ITEMIZED_INVOICE","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-2","document_id":"R-D2","submitted_type":"ITEMIZED_INVOICE","detected_type":"ITEMIZED_INVOICE","verification":"VERIFIED","issues":[],"evidence":["R-D2"],"citation_ids":["PC-02"]},{"document_type":"PAYMENT_RECEIPT","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-3","document_id":"R-D3","submitted_type":"PAYMENT_RECEIPT","detected_type":"PAYMENT_RECEIPT","verification":"VERIFIED","issues":[],"evidence":["R-D3"],"citation_ids":["PC-03"]},{"document_type":"MEDICAL_REPORT","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-4","document_id":"R-D4","submitted_type":"MEDICAL_REPORT","detected_type":"MEDICAL_REPORT","verification":"VERIFIED","issues":[],"evidence":["R-D4"],"citation_ids":["PC-04"]},{"document_type":"REFERRAL_LETTER","required":"CONDITIONAL","status":"NOT_APPLICABLE","requirement_id":"OP-REQ-5","document_id":null,"submitted_type":null,"detected_type":null,"verification":null,"issues":["Condition fact 'specialist_referral_required' not documented; requirement not triggered."],"evidence":[],"citation_ids":["PC-05"]}],"conclusion":"COMPLETE","outstanding_requests":[],"consistency_issues":[]},"policy_verification":{"status":"FOUND","policy_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","checks":[{"check":"policy_active","label":"Policy active on treatment date","result":"PASS","verified_fact":"Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-08-20 to 2026-08-20.","clause_ids":["REJ-2.1"],"rule_ids":[],"citation_ids":["PC-06"],"evidence":["policy_record:POL-REJ-001"]},{"check":"member_covered","label":"Member covered","result":"PASS","verified_fact":"Member MEM-REJ-001 covered 2026-01-01 to 2026-12-31.","clause_ids":["REJ-2.2"],"rule_ids":[],"citation_ids":["PC-07"],"evidence":["policy_record:POL-REJ-001"]},{"check":"benefit_covered","label":"Claim type / benefit covered","result":"PASS","verified_fact":"OUTPATIENT benefit included.","clause_ids":["REJ-3.1"],"rule_ids":[],"citation_ids":["PC-08"],"evidence":["policy_record:POL-REJ-001"]},{"check":"waiting_period","label":"Waiting period","result":"PASS","verified_fact":"30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-08-20.","clause_ids":["REJ-4.1"],"rule_ids":[],"citation_ids":["PC-09"],"evidence":["policy_record:POL-REJ-001"]},{"check":"submission_deadline","label":"Claim submitted within deadline","result":"PASS","verified_fact":"Submitted 2026-08-27, 7 days after last treatment 2026-08-20; OUTPATIENT deadline 60 days (2026-10-19).","clause_ids":[],"rule_ids":["CSR-2.1"],"citation_ids":["PC-10"],"evidence":["rule_set:CSR-2026","claim_submission:CLM-REJ-001"]},{"check":"exclusions","label":"Exclusions","result":"FAIL","verified_fact":"Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication.","clause_ids":["REJ-6.4"],"rule_ids":[],"citation_ids":["PC-11"],"evidence":["R-D4"]},{"check":"limit","label":"Remaining benefit limit","result":"PASS","verified_fact":"Remaining OUTPATIENT limit USD 1500.00 of 1500.00 as of 2026-08-26.","clause_ids":["REJ-5.1"],"rule_ids":[],"citation_ids":["PC-12"],"evidence":["ledger:LED-REJ-001-OP-2026"]}],"remaining_limit":"1500.00","conclusion":"INELIGIBLE","reason":null},"medical_necessity":{"diagnosis":null,"procedures":["Elective cosmetic rhinoplasty"],"result":"NOT_SUPPORTED","rule_id":"CR-002","rationale":"The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.","clinical_source":"Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 7.1","rule_set_version":"1.0","policy_clause_ids":["REJ-3.2"],"citation_ids":["PC-13"],"evidence":[{"value":null,"document_id":"R-D4","location":"p.1, Assessment"},{"value":["Elective cosmetic rhinoplasty"],"document_id":"R-D4","location":"p.1, Procedure"},{"value":false,"document_id":"R-D4","location":"p.1, Assessment"},{"value":"COSMETIC_ELECTIVE","document_id":"R-D4","location":"p.1, Procedure"}],"outstanding_concerns":[]},"benefit_calculation":{"status":"COMPLETE","currency":"USD","submitted":"2000.00","excluded":"2000.00","eligible":"0.00","deductible":"0.00","copay":"0.00","coinsurance":"0.00","limit_adjustment":"0.00","insurer_payable":"0.00","member_responsibility":"2000.00","remaining_limit_before":"1500.00","remaining_limit_after":"1500.00","steps":[{"step":"EXCLUSIONS","amount":"2000.00","detail":"Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication."},{"step":"DEDUCTIBLE","amount":"0.00","detail":"Deductible 0.00."},{"step":"COPAY","amount":"0.00","detail":"Copay 20.00 x 1 visit(s), capped at the amount left."},{"step":"COINSURANCE","amount":"0.00","detail":"Coinsurance rate 0.00."},{"step":"ANNUAL_LIMIT","amount":"0.00","detail":"Payable capped at remaining limit 1500.00."}],"clause_ids":["REJ-6.4","REJ-5.2","REJ-5.1"],"citation_ids":["PC-11","PC-14","PC-12"],"evidence":["R-D2","ledger:LED-REJ-001-OP-2026","R-D4"],"pending_reasons":[]},"recommendation":{"outcome":"REJECT","recommended_payable":"0.00","reasons":[{"finding":"Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication.","evidence":["R-D4"],"citation_ids":["PC-11"]},{"finding":"Medical necessity NOT_SUPPORTED (CR-002): The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.","evidence":["R-D4","clinical_rule:CR-002"],"citation_ids":["PC-13"]},{"finding":"Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.","evidence":["R-D2","ledger:LED-REJ-001-OP-2026","R-D4"],"citation_ids":["PC-11","PC-14","PC-12"]}],"information_requests":[],"escalations":[],"next_action":"Route to human denial review; the denial notice must cite the clauses above.","authorization_owner":"Senior claims assessor (denial review)"},"policy_citations":{"citations":[{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-1","title":"CHK-OUTPATIENT CLAIM_FORM","location":"Section 4.1, Outpatient claim documents","text":"CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed.","citation_id":"PC-01","supported_findings":["Document requirement CLAIM_FORM"],"evidence_ids":["R-D1"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-2","title":"CHK-OUTPATIENT ITEMIZED_INVOICE","location":"Section 4.1, Outpatient claim documents","text":"ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified.","citation_id":"PC-02","supported_findings":["Document requirement ITEMIZED_INVOICE"],"evidence_ids":["R-D2"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-3","title":"CHK-OUTPATIENT PAYMENT_RECEIPT","location":"Section 4.1, Outpatient claim documents","text":"PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed.","citation_id":"PC-03","supported_findings":["Document requirement PAYMENT_RECEIPT"],"evidence_ids":["R-D3"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-4","title":"CHK-OUTPATIENT MEDICAL_REPORT","location":"Section 4.1, Outpatient claim documents","text":"MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity.","citation_id":"PC-04","supported_findings":["Document requirement MEDICAL_REPORT"],"evidence_ids":["R-D4"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-5","title":"CHK-OUTPATIENT REFERRAL_LETTER","location":"Section 4.1, Outpatient claim documents","text":"REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation.","citation_id":"PC-05","supported_findings":["Document requirement REFERRAL_LETTER"],"evidence_ids":[]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-2.1","title":"Period of cover","location":"Page 2, Section 2.1","text":"Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment.","citation_id":"PC-06","supported_findings":["Policy active on treatment date"],"evidence_ids":["policy_record:POL-REJ-001"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-2.2","title":"Insured members","location":"Page 2, Section 2.2","text":"Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force.","citation_id":"PC-07","supported_findings":["Member covered"],"evidence_ids":["policy_record:POL-REJ-001"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-3.1","title":"Outpatient benefit","location":"Page 4, Section 3.1","text":"We will pay for outpatient consultations, day procedures and treatment prescribed by a registered medical practitioner, subject to Sections 5 and 6.","citation_id":"PC-08","supported_findings":["Claim type / benefit covered"],"evidence_ids":["policy_record:POL-REJ-001"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-4.1","title":"Waiting period","location":"Page 5, Section 4.1","text":"Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident.","citation_id":"PC-09","supported_findings":["Waiting period"],"evidence_ids":["policy_record:POL-REJ-001"]},{"kind":"RULE","source_document":"Fictional Claim Submission Rules CSR-2026","version":"2026.1","effective_date":"2026-01-01","clause_id":"CSR-2.1","title":"CSR-2026","location":"Section 2.1, Standard medical treatment","text":"Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date.","citation_id":"PC-10","supported_findings":["Claim submitted within deadline"],"evidence_ids":["rule_set:CSR-2026","claim_submission:CLM-REJ-001"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-6.4","title":"Cosmetic and aesthetic procedures exclusion","location":"Page 9, Section 6.4","text":"We will not pay for any cosmetic or aesthetic procedure, including rhinoplasty, performed to change appearance where there is no medical indication documented by the treating practitioner. This exclusion does not apply to reconstructive surgery required because of an accident or a documented functional impairment.","citation_id":"PC-11","supported_findings":["Exclusions","Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no documented medical indication.","Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.","Benefit calculation"],"evidence_ids":["R-D4","R-D2","ledger:LED-REJ-001-OP-2026"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-5.1","title":"Annual outpatient limit","location":"Page 6, Section 5.1","text":"The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,500.00.","citation_id":"PC-12","supported_findings":["Remaining benefit limit","Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.","Benefit calculation"],"evidence_ids":["ledger:LED-REJ-001-OP-2026","R-D2","R-D4"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-3.2","title":"Medical necessity","location":"Page 4, Section 3.2","text":"Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner.","citation_id":"PC-13","supported_findings":["Medical necessity NOT_SUPPORTED (CR-002): The treating practitioner documents an elective cosmetic procedure and explicitly records no medical indication or functional impairment.","Medical necessity"],"evidence_ids":["R-D4","clinical_rule:CR-002"]},{"kind":"POLICY","source_document":"Fictional Standard Health Plan, Policy Wording 2026-B","version":"2026-B","effective_date":"2026-01-01","clause_id":"REJ-5.2","title":"Outpatient cost-sharing","location":"Page 6, Section 5.2","text":"No deductible or coinsurance applies to outpatient benefits. The member pays a fixed copay of USD 20.00 for each outpatient visit.","citation_id":"PC-14","supported_findings":["Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00 member responsibility; remaining limit 1500.00 -> 1500.00.","Benefit calculation"],"evidence_ids":["R-D2","ledger:LED-REJ-001-OP-2026","R-D4"]}]}}
```
**--- response attempt 1: ERROR OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}**  

# Claim Assessment Report — CLM-RFI-001
_Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human._

- Claim ID: CLM-RFI-001
- Assessment ID: ASM-c3dc9314d7
- Assessor: claim-agent (automated initial assessment)
- Assessment Date: 2026-10-28T11:02:28+00:00
- Policy ID / Version: POL-RFI-001 / 2026-C
- Policyholder: Fictional Hillcrest Logistics Ltd (ORGANIZATION, PH-RFI-001, not an insured member)
- Claim Type: OUTPATIENT
- Patient / Member: MEM-RFI-001
- Treatment / Event Dates: 2026-10-02 to 2026-10-02
- Diagnosis / Treatment (verified): Not verified / Not verified
- Diagnosis / Treatment (claimant-reported): Acute lower back pain / Outpatient consultation; Physiotherapy session
- Submitted Amount / Currency: 300.00 USD
- Audit reference: AUD-CLM-RFI-001-a5a9ec9f

## 1. Document Review (Unresolved items)
| Requirement | Document ID | Document Type | Required | Status | Submitted / Detected | Verification | Issues | Evidence | Citation |
|---|---|---|---|---|---|---|---|---|---|
| OP-REQ-1 | I-D1 | CLAIM_FORM | Yes | Complete | CLAIM_FORM / CLAIM_FORM | Verified | — | I-D1 | PC-01 |
| OP-REQ-2 | I-D2 | ITEMIZED_INVOICE | Yes | Complete | ITEMIZED_INVOICE / ITEMIZED_INVOICE | Verified | — | I-D2 | PC-02 |
| OP-REQ-3 | I-D3 | PAYMENT_RECEIPT | Yes | Complete | PAYMENT_RECEIPT / PAYMENT_RECEIPT | Verified | — | I-D3 | PC-03 |
| OP-REQ-4 | — | MEDICAL_REPORT | Yes | Missing | — / — | — | Submitted I-D4 declared MEDICAL_REPORT but detected APPOINTMENT_CONFIRMATION. | I-D4 | PC-04 |
| OP-REQ-5 | — | REFERRAL_LETTER | Conditional | Not applicable | — / — | — | Condition fact 'specialist_referral_required' not documented; requirement not triggered. | — | PC-05 |
| — | I-D4 | APPOINTMENT_CONFIRMATION | No | Complete | MEDICAL_REPORT / APPOINTMENT_CONFIRMATION | Verified | Submitted as MEDICAL_REPORT but the content is an appointment confirmation. It contains no diagnosis, clinical findings or treatment record. | I-D4 | — |

Document-review conclusion: **Unresolved items**
Outstanding requests: REQ-CLM-RFI-001-1: MEDICAL_REPORT from PROVIDER — Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity.

## 2. Policy Verification (Not yet determined)
| Check | Result | Verified Fact | Policy Clause | Citation | Evidence |
|---|---|---|---|---|---|
| Policy active on treatment date | Pass | Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-10-02 to 2026-10-02. | RFI-2.1 | PC-06 | policy_record:POL-RFI-001 |
| Member covered | Pass | Member MEM-RFI-001 covered 2026-01-01 to 2026-12-31. | RFI-2.2 | PC-07 | policy_record:POL-RFI-001 |
| Claim type / benefit covered | Pass | OUTPATIENT benefit included. | RFI-3.1 | PC-08 | policy_record:POL-RFI-001 |
| Waiting period | Pass | 30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-10-02. | RFI-4.1 | PC-09 | policy_record:POL-RFI-001 |
| Claim submitted within deadline | Pass | Submitted 2026-10-06, 4 days after last treatment 2026-10-02; OUTPATIENT deadline 60 days (2026-12-01). | CSR-2.1 | PC-10 | rule_set:CSR-2026; claim_submission:CLM-RFI-001 |
| Exclusions | Uncertain | No verified procedure classification; exclusions cannot be assessed. | — | — | — |
| Remaining benefit limit | Pass | Remaining OUTPATIENT limit USD 1200.00 of 1500.00 as of 2026-10-05. | RFI-5.1 | PC-11 | ledger:LED-RFI-001-OP-2026 |

Policy-verification conclusion: **Not yet determined**

## 3. Medical Necessity (Insufficient evidence)
- Diagnosis: Not verified
- Treatment / procedure: —
- Clinical rationale: —
- Policy medical-necessity clause: RFI-3.2 (PC-13)
- Clinical rule reference: — — —
- Supporting evidence: —
- Result: **Insufficient evidence**
- Outstanding concerns: No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).

## 4. Benefit Calculation (Pending)
Status: **Pending** (USD)

| Component | Amount | Evidence / Policy Clause |
|---|---|---|
| Submitted amount | 300.00 | — |
| Excluded amount | PENDING | — |
| Eligible / covered amount | PENDING | Calculation |
| Deductible | PENDING | Policy cost-sharing clause |
| Copay | PENDING | Policy cost-sharing clause |
| Coinsurance | PENDING | Policy cost-sharing clause |
| Limit adjustment | PENDING | Annual limit clause / ledger |
| **Insurer payable** | **PENDING** | Calculation |
| **Member responsibility** | **PENDING** | Calculation |
| Remaining limit before → after | PENDING → PENDING | Benefit ledger |

- Calculation order: not run
- Clauses applied: — (—)
- Reconciliation: Not applicable
- Pending because: Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.

## 5. Recommendation (Request more information)
- Recommendation: **Request more information**
- Recommended payable amount: PENDING
- Specific reasons:
  1. MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity. — Evidence: I-D4; Citations: PC-12; PC-04
- Information request REQ-CLM-RFI-001-1: MEDICAL_REPORT from PROVIDER. Why: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity. Requirement: OP-REQ-4 (Fictional Claims Procedure Manual CPM-2026 v1.2, Section 4.1, Outpatient claim documents); policy condition: RFI-7.2. Reassessment trigger: Reassess when a MEDICAL_REPORT for CLM-RFI-001 is received and verified.
- Escalations or reservations: Exclusions uncertain: No verified procedure classification; exclusions cannot be assessed.; Medical necessity INSUFFICIENT_EVIDENCE: No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).; Benefit calculation PENDING: Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.
- Next action / authorization owner: Send the information requests; hold the claim as PENDING_INFORMATION and reassess on receipt. — Claims assessor

## 6. Policy Citations (Pass)
| Citation | Kind | Source Document | Version / Effective | Clause / Location | Relevant Wording | Supported Finding | Evidence |
|---|---|---|---|---|---|---|---|
| PC-01 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-1 — Section 4.1, Outpatient claim documents | CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed. | Document requirement CLAIM_FORM | I-D1 |
| PC-02 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-2 — Section 4.1, Outpatient claim documents | ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified. | Document requirement ITEMIZED_INVOICE | I-D2 |
| PC-03 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-3 — Section 4.1, Outpatient claim documents | PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed. | Document requirement PAYMENT_RECEIPT | I-D3 |
| PC-04 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-4 — Section 4.1, Outpatient claim documents | MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity. | Document requirement MEDICAL_REPORT; MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity. | I-D4 |
| PC-05 | Procedural | Fictional Claims Procedure Manual CPM-2026 | 1.2 / — | OP-REQ-5 — Section 4.1, Outpatient claim documents | REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation. | Document requirement REFERRAL_LETTER | — |
| PC-06 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-2.1 — Page 2, Section 2.1 | Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment. | Policy active on treatment date | policy_record:POL-RFI-001 |
| PC-07 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-2.2 — Page 2, Section 2.2 | Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force. | Member covered | policy_record:POL-RFI-001 |
| PC-08 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-3.1 — Page 4, Section 3.1 | We will pay for outpatient consultations, physiotherapy and treatment prescribed by a registered medical practitioner, subject to the limits and cost-sharing shown in Section 5. | Claim type / benefit covered | policy_record:POL-RFI-001 |
| PC-09 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-4.1 — Page 5, Section 4.1 | Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident. | Waiting period | policy_record:POL-RFI-001 |
| PC-10 | Rule | Fictional Claim Submission Rules CSR-2026 | 2026.1 / 2026-01-01 | CSR-2.1 — Section 2.1, Standard medical treatment | Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date. | Claim submitted within deadline | rule_set:CSR-2026; claim_submission:CLM-RFI-001 |
| PC-11 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-5.1 — Page 6, Section 5.1 | The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,500.00. | Remaining benefit limit | ledger:LED-RFI-001-OP-2026 |
| PC-12 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-7.2 — Page 10, Section 7.2 | Each outpatient claim must be supported by a medical report from the treating practitioner stating the diagnosis and the treatment provided. We may defer assessment until this report is received. | MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity. | I-D4 |
| PC-13 | Policy | Fictional Active Health Plan, Policy Wording 2026-C | 2026-C / 2026-01-01 | RFI-3.2 — Page 4, Section 3.2 | Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner. | Medical necessity | — |

- Citation coverage check: Pass
- Report validation: Pass
- Explanations: Failed

Assessment Status: **Waiting for information**
Final Authorization Status: **Pending**

### Tool call log — AUD-CLM-RFI-001-a5a9ec9f
Context version: ctx-1/fixtures-2026.10-1

```
 1 11:02:28 OK      verifyDocument(I-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:02:28 OK      verifyDocument(I-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:02:28 OK      verifyDocument(I-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:02:28 OK      verifyDocument(I-D4) -> FOUND APPOINTMENT_CONFIRMATION COMPLETE issues=TYPE_MISMATCH
 5 11:02:28 OK      documentReview(CHK-OUTPATIENT v1.2) -> UNRESOLVED_ITEMS: 3/4 COMPLETE; OP-REQ-4 MEDICAL_REPORT MISSING
 6 11:02:28 OK      lookupPolicy(POL-RFI-001) -> FOUND v2026-C 6/7 PASS exclusions=UNCERTAIN remaining=1200.00
 7 11:02:28 SKIPPED checkMedicalNecessity -> No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).
 8 11:02:28 SKIPPED calculateBenefit -> Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.
 9 11:02:28 OK      decide() -> REQUEST_MORE_INFO payable=null requests=REQ-CLM-RFI-001-1 escalations=3
10 11:02:29 ERROR   openrouter.chat(attempt 1) -> error: OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (13513 chars): {"claim_id":"CLM-RFI-001","currency":"USD","document_review":{"checklis…
11 11:02:29 ERROR   draftExplanations(anthropic/claude-haiku-) -> FAILED attempts=1
12 11:02:29 OK      validateReport() -> PASS citations=PASS reconciliation=NOT_APPLICABLE final_status=PENDING_INFORMATION
```

### LLM request and response (OpenRouter)

**LLM call #11 draftExplanations -> FAILED (attempts=1)**  
Request: POST https://openrouter.ai/api/v1/chat/completions  model=anthropic/claude-haiku-  temperature=0.0  max_tokens=1000  (Authorization header not shown)  
**--- request message 1: system (603 chars)**  
```
You draft explanations for a human insurance claim assessor.
Rules:
- Use only the facts in the supplied JSON. Do not add clinical, policy or financial information.
- Do not make, change or question the recommendation. The application decided it; you explain it.
- Mention only clause IDs, document IDs and amounts that appear in the facts. Write amounts with two decimals exactly as given.
- Reply with one JSON object and nothing else. Its keys must be exactly: document_review, policy_verification, medical_necessity, benefit_calculation, recommendation. Each value is a short plain-text explanation.
```
**--- request message 2: user (13513 chars)**  
```
{"claim_id":"CLM-RFI-001","currency":"USD","document_review":{"checklist":{"id":"CHK-OUTPATIENT","version":"1.2","source":{"document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","location":"Section 4.1, Outpatient claim documents"}},"rows":[{"document_type":"CLAIM_FORM","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-1","document_id":"I-D1","submitted_type":"CLAIM_FORM","detected_type":"CLAIM_FORM","verification":"VERIFIED","issues":[],"evidence":["I-D1"],"citation_ids":["PC-01"]},{"document_type":"ITEMIZED_INVOICE","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-2","document_id":"I-D2","submitted_type":"ITEMIZED_INVOICE","detected_type":"ITEMIZED_INVOICE","verification":"VERIFIED","issues":[],"evidence":["I-D2"],"citation_ids":["PC-02"]},{"document_type":"PAYMENT_RECEIPT","required":"Y","status":"COMPLETE","requirement_id":"OP-REQ-3","document_id":"I-D3","submitted_type":"PAYMENT_RECEIPT","detected_type":"PAYMENT_RECEIPT","verification":"VERIFIED","issues":[],"evidence":["I-D3"],"citation_ids":["PC-03"]},{"document_type":"MEDICAL_REPORT","required":"Y","status":"MISSING","requirement_id":"OP-REQ-4","document_id":null,"submitted_type":null,"detected_type":null,"verification":null,"issues":["Submitted I-D4 declared MEDICAL_REPORT but detected APPOINTMENT_CONFIRMATION."],"evidence":["I-D4"],"citation_ids":["PC-04"]},{"document_type":"REFERRAL_LETTER","required":"CONDITIONAL","status":"NOT_APPLICABLE","requirement_id":"OP-REQ-5","document_id":null,"submitted_type":null,"detected_type":null,"verification":null,"issues":["Condition fact 'specialist_referral_required' not documented; requirement not triggered."],"evidence":[],"citation_ids":["PC-05"]},{"document_type":"APPOINTMENT_CONFIRMATION","required":"N","status":"COMPLETE","requirement_id":null,"document_id":"I-D4","submitted_type":"MEDICAL_REPORT","detected_type":"APPOINTMENT_CONFIRMATION","verification":"VERIFIED","issues":["Submitted as MEDICAL_REPORT but the content is an appointment confirmation. It contains no diagnosis, clinical findings or treatment record."],"evidence":["I-D4"],"citation_ids":[]}],"conclusion":"UNRESOLVED_ITEMS","outstanding_requests":[{"request_id":"REQ-CLM-RFI-001-1","required_item":"MEDICAL_REPORT","why_needed":"Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity.","request_to":"PROVIDER","requirement_id":"OP-REQ-4","checklist_source":"Fictional Claims Procedure Manual CPM-2026 v1.2, Section 4.1, Outpatient claim documents","policy_clause_id":"RFI-7.2","reassessment_trigger":"Reassess when a MEDICAL_REPORT for CLM-RFI-001 is received and verified.","status":"OPEN"}],"consistency_issues":[]},"policy_verification":{"status":"FOUND","policy_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","checks":[{"check":"policy_active","label":"Policy active on treatment date","result":"PASS","verified_fact":"Policy ACTIVE 2026-01-01 to 2026-12-31; treatment 2026-10-02 to 2026-10-02.","clause_ids":["RFI-2.1"],"rule_ids":[],"citation_ids":["PC-06"],"evidence":["policy_record:POL-RFI-001"]},{"check":"member_covered","label":"Member covered","result":"PASS","verified_fact":"Member MEM-RFI-001 covered 2026-01-01 to 2026-12-31.","clause_ids":["RFI-2.2"],"rule_ids":[],"citation_ids":["PC-07"],"evidence":["policy_record:POL-RFI-001"]},{"check":"benefit_covered","label":"Claim type / benefit covered","result":"PASS","verified_fact":"OUTPATIENT benefit included.","clause_ids":["RFI-3.1"],"rule_ids":[],"citation_ids":["PC-08"],"evidence":["policy_record:POL-RFI-001"]},{"check":"waiting_period","label":"Waiting period","result":"PASS","verified_fact":"30-day waiting period from 2026-01-01 satisfied from 2026-01-31; treatment 2026-10-02.","clause_ids":["RFI-4.1"],"rule_ids":[],"citation_ids":["PC-09"],"evidence":["policy_record:POL-RFI-001"]},{"check":"submission_deadline","label":"Claim submitted within deadline","result":"PASS","verified_fact":"Submitted 2026-10-06, 4 days after last treatment 2026-10-02; OUTPATIENT deadline 60 days (2026-12-01).","clause_ids":[],"rule_ids":["CSR-2.1"],"citation_ids":["PC-10"],"evidence":["rule_set:CSR-2026","claim_submission:CLM-RFI-001"]},{"check":"exclusions","label":"Exclusions","result":"UNCERTAIN","verified_fact":"No verified procedure classification; exclusions cannot be assessed.","clause_ids":[],"rule_ids":[],"citation_ids":[],"evidence":[]},{"check":"limit","label":"Remaining benefit limit","result":"PASS","verified_fact":"Remaining OUTPATIENT limit USD 1200.00 of 1500.00 as of 2026-10-05.","clause_ids":["RFI-5.1"],"rule_ids":[],"citation_ids":["PC-11"],"evidence":["ledger:LED-RFI-001-OP-2026"]}],"remaining_limit":"1200.00","conclusion":"UNDETERMINED","reason":null},"medical_necessity":{"diagnosis":null,"procedures":[],"result":"INSUFFICIENT_EVIDENCE","rule_id":null,"rationale":null,"clinical_source":null,"rule_set_version":null,"policy_clause_ids":["RFI-3.2"],"citation_ids":["PC-13"],"evidence":[],"outstanding_concerns":["No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION)."]},"benefit_calculation":{"status":"PENDING","currency":"USD","submitted":"300.00","excluded":null,"eligible":null,"deductible":null,"copay":null,"coinsurance":null,"limit_adjustment":null,"insurer_payable":null,"member_responsibility":null,"remaining_limit_before":null,"remaining_limit_after":null,"steps":[],"clause_ids":[],"citation_ids":[],"evidence":[],"pending_reasons":["Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE."]},"recommendation":{"outcome":"REQUEST_MORE_INFO","recommended_payable":null,"reasons":[{"finding":"MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity.","evidence":["I-D4"],"citation_ids":["PC-12","PC-04"]}],"information_requests":[{"request_id":"REQ-CLM-RFI-001-1","required_item":"MEDICAL_REPORT","why_needed":"Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity.","request_to":"PROVIDER","requirement_id":"OP-REQ-4","checklist_source":"Fictional Claims Procedure Manual CPM-2026 v1.2, Section 4.1, Outpatient claim documents","policy_clause_id":"RFI-7.2","reassessment_trigger":"Reassess when a MEDICAL_REPORT for CLM-RFI-001 is received and verified.","status":"OPEN"}],"escalations":["Exclusions uncertain: No verified procedure classification; exclusions cannot be assessed.","Medical necessity INSUFFICIENT_EVIDENCE: No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).","Benefit calculation PENDING: Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE."],"next_action":"Send the information requests; hold the claim as PENDING_INFORMATION and reassess on receipt.","authorization_owner":"Claims assessor"},"policy_citations":{"citations":[{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-1","title":"CHK-OUTPATIENT CLAIM_FORM","location":"Section 4.1, Outpatient claim documents","text":"CLAIM_FORM is REQUIRED: Identifies the member, policy, treatment date and amount claimed.","citation_id":"PC-01","supported_findings":["Document requirement CLAIM_FORM"],"evidence_ids":["I-D1"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-2","title":"CHK-OUTPATIENT ITEMIZED_INVOICE","location":"Section 4.1, Outpatient claim documents","text":"ITEMIZED_INVOICE is REQUIRED: Itemizes the charges so covered and excluded amounts can be identified.","citation_id":"PC-02","supported_findings":["Document requirement ITEMIZED_INVOICE"],"evidence_ids":["I-D2"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-3","title":"CHK-OUTPATIENT PAYMENT_RECEIPT","location":"Section 4.1, Outpatient claim documents","text":"PAYMENT_RECEIPT is REQUIRED: Confirms the member paid the amount being reimbursed.","citation_id":"PC-03","supported_findings":["Document requirement PAYMENT_RECEIPT"],"evidence_ids":["I-D3"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-4","title":"CHK-OUTPATIENT MEDICAL_REPORT","location":"Section 4.1, Outpatient claim documents","text":"MEDICAL_REPORT is REQUIRED: Documents the diagnosis and treatment needed to assess coverage and medical necessity.","citation_id":"PC-04","supported_findings":["Document requirement MEDICAL_REPORT","MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity."],"evidence_ids":["I-D4"]},{"kind":"PROCEDURAL","source_document":"Fictional Claims Procedure Manual CPM-2026","version":"1.2","effective_date":null,"clause_id":"OP-REQ-5","title":"CHK-OUTPATIENT REFERRAL_LETTER","location":"Section 4.1, Outpatient claim documents","text":"REFERRAL_LETTER is CONDITIONAL: Confirms a referral where the policy requires one for specialist consultation.","citation_id":"PC-05","supported_findings":["Document requirement REFERRAL_LETTER"],"evidence_ids":[]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-2.1","title":"Period of cover","location":"Page 2, Section 2.1","text":"Cover under this policy applies to treatment received between the effective date and the expiry date shown in the schedule, provided the policy is in force on the date of treatment.","citation_id":"PC-06","supported_findings":["Policy active on treatment date"],"evidence_ids":["policy_record:POL-RFI-001"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-2.2","title":"Insured members","location":"Page 2, Section 2.2","text":"Only persons named as insured members in the schedule are covered, and only for treatment received while their individual cover is in force.","citation_id":"PC-07","supported_findings":["Member covered"],"evidence_ids":["policy_record:POL-RFI-001"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-3.1","title":"Outpatient benefit","location":"Page 4, Section 3.1","text":"We will pay for outpatient consultations, physiotherapy and treatment prescribed by a registered medical practitioner, subject to the limits and cost-sharing shown in Section 5.","citation_id":"PC-08","supported_findings":["Claim type / benefit covered"],"evidence_ids":["policy_record:POL-RFI-001"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-4.1","title":"Waiting period","location":"Page 5, Section 4.1","text":"Outpatient benefits are payable only for treatment received after 30 days of continuous cover from the member's cover start date, except for treatment following an accident.","citation_id":"PC-09","supported_findings":["Waiting period"],"evidence_ids":["policy_record:POL-RFI-001"]},{"kind":"RULE","source_document":"Fictional Claim Submission Rules CSR-2026","version":"2026.1","effective_date":"2026-01-01","clause_id":"CSR-2.1","title":"CSR-2026","location":"Section 2.1, Standard medical treatment","text":"Reimbursement claims for standard medical treatment (inpatient or outpatient) must be submitted within 60 days from the last date of treatment or the discharge date.","citation_id":"PC-10","supported_findings":["Claim submitted within deadline"],"evidence_ids":["rule_set:CSR-2026","claim_submission:CLM-RFI-001"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-5.1","title":"Annual outpatient limit","location":"Page 6, Section 5.1","text":"The maximum we will pay for all outpatient benefits per member in a policy year is USD 1,500.00.","citation_id":"PC-11","supported_findings":["Remaining benefit limit"],"evidence_ids":["ledger:LED-RFI-001-OP-2026"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-7.2","title":"Claim evidence","location":"Page 10, Section 7.2","text":"Each outpatient claim must be supported by a medical report from the treating practitioner stating the diagnosis and the treatment provided. We may defer assessment until this report is received.","citation_id":"PC-12","supported_findings":["MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. Documents the diagnosis and treatment needed to assess coverage and medical necessity."],"evidence_ids":["I-D4"]},{"kind":"POLICY","source_document":"Fictional Active Health Plan, Policy Wording 2026-C","version":"2026-C","effective_date":"2026-01-01","clause_id":"RFI-3.2","title":"Medical necessity","location":"Page 4, Section 3.2","text":"Treatment is covered only when it is medically necessary for the diagnosis documented by the treating practitioner.","citation_id":"PC-13","supported_findings":["Medical necessity"],"evidence_ids":[]}]}}
```
**--- response attempt 1: ERROR OpenRouter returned HTTP 400: {"error":{"message":"anthropic/claude-haiku- is not a valid model ID","code":400},"user_id":"user_3LJbH54IDtMQ6Jofosn33x0OEVJ"}**  

