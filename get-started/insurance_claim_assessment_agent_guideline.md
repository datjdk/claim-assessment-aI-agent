# Insurance Claim Assessment — Agent Operating Guideline

> **Purpose:** A structured operating guideline for a human assessor or claims-assessment agent reviewing health insurance claims.  
> **Status:** Reference SOP / implementation template, not a substitute for insurer-approved procedures, the actual insurance contract, clinical judgment, or applicable law.  
> **Version:** 2.0 | **Date:** 2026-10-27  
> **Reference model:** Publicly described Papaya claims-administration and claims-automation processes (see [References](#references)).

## 0. Agent operating principles

1. **Never invent policy terms, clause identifiers, benefit limits, document requirements, or clinical findings.** Read the actual insurer-specific policy documents and checklist configuration before making a decision.
2. Review the **policy version effective on the treatment/event date**, including endorsements, product schedules, waiting periods, and member eligibility.
3. Separate **fact** (supported by evidence), **policy interpretation** (supported by clauses), and **clinical assessment** (supported by records and qualified medical review).
4. Maintain a traceable evidence trail: **claim ID -> finding -> source document and page/field -> exact policy clause and page -> calculation/recommendation**.
5. Missing or inconsistent evidence usually warrants `REQUEST_MORE_INFO` or escalation, not an automatic rejection.
6. Escalate unclear clauses, clinical disputes, unusual amounts, suspected fraud, and decisions beyond the assessor's authority.
7. An assessor's recommendation is **not automatically the final claim decision**. Apply the insurer's approval matrix and legal notice requirements.
8. Handle medical and personal data only through authorized systems and according to applicable privacy requirements.

## 1. Input entities and required checks

| Entity | Key fields | Assessor/agent check |
|---|---|---|
| Claim | `claim_id`, `claim_type`, `diagnosis`, `treatment_dates`, `claimed_amount`, `provider` | Is the claim identifiable, internally consistent and assigned correctly? |
| Insured member | `member_id`, `name`, `date_of_birth`, `policy_id`, `relationship` | Is this patient covered on the event date? |
| Policy | `policy_id`, `version`, `effective_from`, `effective_to`, `status`, `endorsements` | Which contractual text applies to the event? |
| Policy clauses | `clause_id`, `title`, `exact_text`, `page`, `effective_version` | Which exact provision supports each finding? |
| Benefits | `benefit_type`, `limits`, `sublimits`, `remaining_balance`, `deductible`, `copay`, `coinsurance` | What services and amounts are eligible? |
| Document requirements | `claim_type`, `document_type`, `requirement`, `condition`, `policy_or_procedure_source` | Which documents are mandatory, conditional or additional? |
| Claim documents | `document_id`, `document_type`, `received_date`, `completeness_status`, `verification_status`, `issues` | Are they present, complete, genuine to the required verification standard and mutually consistent? |
| Medical assessment | `diagnosis`, `procedure`, `clinical_evidence`, `reviewer`, `findings` | Does the evidence support medical necessity under the policy? |
| Claim history | `prior_claims`, `prior_payments`, `duplicate_flags`, `remaining_limits` | Is there duplicate reimbursement or reduced remaining coverage? |
| Calculation | `submitted`, `excluded`, `eligible`, `deductible`, `copay`, `coinsurance`, `payable`, `member_responsibility` | Is the calculation correct and policy-supported? |
| Information requests | `request_id`, `required_item`, `why_needed`, `request_to`, `due_date`, `status` | Is missing information tracked and resolved? |
| Assessment / decision | `assessment_id`, `recommendation`, `reasoning`, `citations`, `approver`, `final_decision` | Is the decision auditable and appropriately authorized? |

## 2. Workflow (ordered gates)

### Step 1 — Intake and identity validation
- Verify claim ID, linked policy, member, claim type, treatment/event dates, diagnosis and submitted amount.
- Check obvious duplicate claims and previously paid claims.
- **Output:** `claim_validated = true/false`; list inconsistencies.
- **If materially incomplete:** create information request; do not assume facts.

### Step 2 — Document review
- Load the insurer's approved document-checklist rules for the claim type, policy product and circumstances.
- Apply conditional requirements (e.g., surgery report if surgery occurred).
- For every document capture `required`, `submitted`, `status = COMPLETE | INCOMPLETE | MISSING`, `verification_status`, `issues`, `document_id`, and page references.
- Cross-check dates, patient details, diagnosis, invoice totals, payment receipts and medical reports.
- **Output:** complete document-review table, unresolved gaps and evidence citations.
- **If material evidence missing:** recommend `REQUEST_MORE_INFO`, unless authorized procedures allow assessment using available evidence.

### Step 3 — Policy verification
- Identify actual policy version and endorsements effective on event/treatment dates.
- Verify active coverage on event dates, member eligibility, covered claim type and benefits, waiting periods, exclusions, limits/sublimits and remaining benefit balance.
- Record **exact clause ID + policy document version + page/location + relevant wording** for each substantive coverage finding.
- **Output:** policy verification table with pass/fail/uncertain and clause citations.
- **If clause applicability unclear:** escalate; never manufacture an interpretation.

### Step 4 — Medical necessity
- Compare diagnosis, procedure/treatment, dates, urgency, clinical documentation and policy-specific medical necessity criteria.
- Flag clinical contradictions or questions requiring a qualified medical reviewer.
- **Output:** `SUPPORTED | NOT_SUPPORTED | INSUFFICIENT_EVIDENCE | REFER_TO_MEDICAL_REVIEW`, with evidence and policy citations.
- A non-clinical assessor must not independently make specialist clinical judgments outside authorization.

### Step 5 — Benefit calculation
- Reconcile submitted invoice charges, identify covered/eligible and excluded line items using cited policy terms.
- Apply coverage sublimits, annual balance, deductible, fixed copay and/or coinsurance **in the exact sequence specified by the policy**.
- Check prior payments, coordination of benefits, currency and rounding rules.
- Reconcile: `submitted_amount = excluded_amount + eligible_amount` where categories do not overlap; and `eligible_amount = insurer_payable + member_share_of_eligible_amount` after applicable adjustments.
- Total member responsibility generally includes excluded charges plus eligible cost-sharing, subject to actual contract and provider arrangements.
- **Output:** itemized calculation and policy references. If a necessary input is unknown, mark payout `PENDING`, do not guess.

### Step 6 — Risk and quality screening
- Check duplicates, anomalous invoicing, identity/document inconsistencies and possible fraud/waste/abuse indicators under approved procedures.
- A risk indicator is **not** proof of fraud. Refer for authorized specialist investigation rather than alleging fraud.
- **Output:** `CLEAR | FLAGGED_FOR_REVIEW`, reason and escalation owner.

### Step 7 — Structured assessment report
- Complete **all six required report sections** in [Section 4](#4-required-assessment-report-template): Document Review; Policy Verification; Medical Necessity; Benefit Calculation; Recommendation; Policy Citations.
- Tie each material conclusion to source evidence and exact relevant policy clauses; label unresolved questions.

### Step 8 — Recommend outcome and route

| Recommendation | When appropriate | Required next action |
|---|---|---|
| `APPROVE` | Coverage and eligible amount established with sufficient evidence and required reviews satisfied | Recommend full/partial payable amount and send for authorization |
| `REJECT` | An applicable contractual or legally valid reason for denial is established by sufficient evidence | Cite exact clause, explain factual applicability, route for required denial review/notice |
| `REQUEST_MORE_INFO` | Material evidence or clarification is needed for coverage, medical necessity or payout | Name the item, why needed, recipient, relevant requirement, due date and reassessment trigger |

- Record decision time, assessor, report version, evidence references and approval status.
- Final decision/payment belongs to the authorized role or automated process allowed by insurer governance.

## 3. Decision guardrails

1. Do **not** approve where coverage cannot be established or required medical review remains unresolved.
2. Do **not** reject merely because a document is missing; follow the evidence-request and procedural rules.
3. Do **not** reject by citing a generic exclusion without proving it applies to the specific medical procedure and facts.
4. Do **not** finalize a numeric payable amount if charges or policy-sharing rules remain indeterminate.
5. Do **not** cite an example or assumed clause as though it came from a real policy.
6. Where policy terms conflict or are unclear, escalate to the policy/legal/claims specialist.
7. A policy citation supports a coverage rule; medical necessity must also be supported by clinical evidence and qualified review as applicable.
8. Record the version of the policy and benefit schedule used, along with policy pages/locations and document IDs.

## 4. Required assessment report template

> Copy this template for each claim. Replace placeholders only with verified values. Every material recommendation point must be tied to **both evidence and applicable exact policy wording**. If no valid policy citation is available, flag the point as `UNVERIFIED` and do not present it as a confirmed contractual conclusion.

```markdown
# Claim Assessment Report
- Claim ID: <claim_id>
- Assessment ID: <assessment_id>
- Assessor: <assessor_name_or_agent_id>
- Assessment Date: <ISO date>
- Policy ID / Version: <id / version applicable to treatment date>
- Claim Type: <type>
- Patient / Member: <member ID>
- Treatment / Event Dates: <dates>
- Diagnosis / Treatment: <verified facts>
- Submitted Amount / Currency: <amount>

## 1. Document Review
| Document ID | Document Type | Required (Y/N/Conditional) | Status (COMPLETE/INCOMPLETE/MISSING) | Verification | Issues | Evidence Reference |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |
Document-review conclusion: <COMPLETE | UNRESOLVED_ITEMS>
Outstanding requests: <item, reason, recipient, due date or NONE>

## 2. Policy Verification
| Check | Result (PASS/FAIL/UNCERTAIN) | Verified Fact | Policy Clause / Page | Evidence Reference |
|---|---|---|---|---|
| Policy active on event date | ... | ... | ... | ... |
| Member covered | ... | ... | ... | ... |
| Claim type / benefit covered | ... | ... | ... | ... |
| Waiting periods and exclusions | ... | ... | ... | ... |
| Limits / remaining balance | ... | ... | ... | ... |
Policy-verification conclusion: <ELIGIBLE | INELIGIBLE | UNDETERMINED>

## 3. Medical Necessity
- Diagnosis: <verified diagnosis + evidence source>
- Treatment / procedure: <verified treatment + evidence source>
- Clinical rationale: <facts in reports, no unsupported clinical inference>
- Policy medical-necessity clause: <exact clause / version / page>
- Medical review / clinical guideline reference (if applicable): <reference>
- Result: <SUPPORTED | NOT_SUPPORTED | INSUFFICIENT_EVIDENCE | REFER_TO_MEDICAL_REVIEW>
- Outstanding concerns: <issues or NONE>

## 4. Benefit Calculation
| Component | Amount | Evidence / Policy Clause |
|---|---:|---|
| Submitted amount | ... | Invoice ID / page |
| Excluded amount | ... | Policy clause / invoice line |
| Eligible / covered amount | ... | Policy clauses / calculation |
| Deductible | ... | Policy clause |
| Copay (fixed, if applicable) | ... | Policy clause |
| Coinsurance (percentage, if applicable) | ... | Policy clause |
| Other limits / adjustments | ... | Policy clause / ledger |
| Insurer payable | ... or PENDING | Calculation |
| Member responsibility | ... or PENDING | Calculation |
- Calculation formula/order: <explicit policy-based steps>
- Currency, rounding and remaining limits: <details>
- Reconciliation: <PASS | NEEDS_REVIEW>

## 5. Recommendation
- Recommendation: <APPROVE | REJECT | REQUEST_MORE_INFO>
- Recommended payable amount: <amount or PENDING>
- Specific reasons (each needs evidence AND policy clause):
  1. <fact> — Evidence: <document / page>; Policy: <clause / version / page>
  2. <fact> — Evidence: <document / page>; Policy: <clause / version / page>
- For REQUEST_MORE_INFO: <item, purpose, recipient, deadline, reassessment trigger>
- Escalations or reservations: <details or NONE>
- Next action / authorization owner: <role>

## 6. Policy Citations
| Citation ID | Policy Document | Version / Effective Date | Clause ID / Page | Relevant Policy Wording | Supported Finding | Evidence ID |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |
- Citation coverage check: <PASS | FAIL; explain any missing citation>
- Policy ambiguity / conflicts: <details or NONE>

Assessment Status: <DRAFT | READY_FOR_AUTHORIZATION | PENDING_INFORMATION | ESCALATED>
Final Authorization Status: <PENDING | APPROVED | REJECTED | NOT_APPLICABLE>
```

## 5. Worked example (fictional training claim)

**IMPORTANT:** Names, amounts and **all clause numbers below are invented training data**. They must never be treated as Papaya's or an actual insurer's policy wording.

### Claim context

| Field | Example |
|---|---|
| Claim ID | `CLM-2026-00456` |
| Policy | `HI-2026-00125` (fictional, version `2026-A`) |
| Member | John Smith |
| Claim type | Inpatient hospitalization / surgery |
| Diagnosis | Acute appendicitis |
| Treatment | Laparoscopic appendectomy |
| Admission / discharge | 2026-10-10 to 2026-10-13 |
| Submitted amount | USD 8,500 |

### 5.1 Document Review

| Document ID | Document | Required | Status | Issues |
|---|---|---|---|---|
| DOC-01 | Claim form | Yes | COMPLETE | None; member identifiers match |
| DOC-02 | Itemized hospital invoice | Yes | COMPLETE | USD 500 non-medical room upgrade identified |
| DOC-03 | Discharge summary | Yes | COMPLETE | Dates match |
| DOC-04 | Diagnosis report | Yes for this scenario | COMPLETE | Acute appendicitis documented |
| DOC-05 | Surgery report | Conditional: surgery performed | COMPLETE | Appendectomy documented |
| DOC-06 | Payment receipt | Yes for reimbursement example | COMPLETE | Amount reconciles |

**Document-review conclusion:** `COMPLETE` (verification assumed for illustration).

### 5.2 Policy Verification

| Check | Example verified fact | Fictional clause | Outcome |
|---|---|---|---|
| Active on treatment date | Coverage 2026-01-01 to 2026-12-31 | §2.1 | PASS |
| Member covered | John Smith is a covered member | §2.2 | PASS |
| Hospitalization benefit | Included | §3.1 | PASS |
| Necessary surgery benefit | Included | §3.2 | PASS |
| Waiting period | Satisfied | §4.1 | PASS |
| Remaining benefit | USD 30,000 before claim | §5.1 | PASS |
| Room upgrade exclusion | Non-medical upgrade excluded | §6.3 | ADJUSTMENT |

**Policy conclusion:** `ELIGIBLE` under assumed fictional contract terms.

### 5.3 Medical Necessity

| Check | Example finding |
|---|---|
| Diagnosis | Acute appendicitis documented in DOC-04 |
| Treatment | Laparoscopic appendectomy documented in DOC-05 |
| Relationship | Clinical records in this **hypothetical** scenario support the treatment |
| Hospitalization | Admission and discharge records align |
| Policy reference | Fictional §3.2 |
| Conclusion | `SUPPORTED` for training scenario; refer uncertain real cases to clinical reviewer |

### 5.4 Benefit Calculation

| Item | USD | Fictional evidence / clause |
|---|---:|---|
| Submitted amount | 8,500 | DOC-02 |
| Excluded room upgrade | -500 | §6.3; DOC-02 |
| Eligible / covered amount | 8,000 | §3.1–§3.2 |
| Deductible | -500 | §5.2 |
| Coinsurance: 10% × (8,000 − 500) | -750 | §5.3 |
| **Insurer payable** | **6,750** | Illustrative calculation |
| **Member responsibility** | **1,750** | USD 500 excluded + USD 500 deductible + USD 750 coinsurance |

### 5.5 Recommendation

- **Recommendation:** `APPROVE`
- **Recommended payable:** USD 6,750
- **Reason 1:** Member covered at event date — fictional §§2.1–2.2; policy/member record.
- **Reason 2:** Hospitalization and surgery covered — fictional §§3.1–3.2; DOC-03 through DOC-05.
- **Reason 3:** Non-medical room upgrade excluded — fictional §6.3; DOC-02 line item.
- **Reason 4:** Cost-sharing yields insurer payable USD 6,750 — fictional §§5.1–5.3; DOC-02 and benefit ledger.
- **Next action:** Authorized approval review; assessor does not independently authorize payment.

### 5.6 Policy Citations

| Citation | Fictional clause | Finding supported | Evidence |
|---|---|---|---|
| PC-01 | §2.1 | Effective coverage | Policy record |
| PC-02 | §2.2 | Covered member | Member record |
| PC-03 | §3.1 | Inpatient coverage | DOC-03 |
| PC-04 | §3.2 | Surgery coverage/necessity condition | DOC-04, DOC-05 |
| PC-05 | §4.1 | Waiting period | Policy record |
| PC-06 | §5.1 | Remaining limit | Benefit ledger |
| PC-07 | §5.2 | USD 500 deductible | Fictional benefits schedule |
| PC-08 | §5.3 | 10% coinsurance | Fictional benefits schedule |
| PC-09 | §6.3 | USD 500 room upgrade exclusion | DOC-02 |

**Production requirement:** Replace the fictional references above with actual policy document/version, full clause identifiers, page locations and relevant contractual text before recommendation submission.

## 6. Alternative outcome examples

| Recommendation | Illustrative trigger | Required evidence and policy support |
|---|---|---|
| `APPROVE` | Covered appendectomy, sufficient evidence, calculated payout | Coverage, medical records, correct cost-sharing clauses |
| `REJECT` | An elective cosmetic procedure unequivocally falls within a relevant exclusion | Verified treatment classification + **actual** applicable exclusion clause; required denial review |
| `REQUEST_MORE_INFO` | Surgery report missing and necessary to verify a claimed procedure | Approved document requirement + explanation of why evidence matters + specific request |

## 7. Report quality and validation checklist

- [ ] Correct claim, policy version and treatment dates linked.
- [ ] Member covered on event date.
- [ ] Every required document has a completeness status and issues recorded.
- [ ] Document identities and material fields cross-checked.
- [ ] Claim type and benefit coverage verified against actual policy terms.
- [ ] Waiting periods, exclusions, sublimits and remaining benefits checked.
- [ ] Medical necessity assessed within authority or referred to clinical review.
- [ ] Duplicate, anomaly and risk flags resolved or escalated.
- [ ] Benefit amounts calculated with the correct contract-defined order.
- [ ] Insurer payable and member responsibility reconcile.
- [ ] Recommendation is one of `APPROVE`, `REJECT`, `REQUEST_MORE_INFO`.
- [ ] **Each material recommendation reason cites both source evidence and an exact applicable policy clause.**
- [ ] Any outstanding information requests are specific, tracked and assigned.
- [ ] Proper approval authority / escalation routing is selected.
- [ ] Personal data is restricted to authorized users and systems.

## 8. Suggested claim system status lifecycle

`SUBMITTED -> ASSIGNED -> UNDER_ASSESSMENT -> (PENDING_INFORMATION -> UNDER_ASSESSMENT)* -> ASSESSMENT_COMPLETED -> PENDING_AUTHORIZATION -> APPROVED | REJECTED -> (PAYMENT_PROCESSING if approved) -> CLOSED`

Exception states may include `ESCALATED`, `MEDICAL_REVIEW`, or `FRAUD_REVIEW` under insurer rules. A `REQUEST_MORE_INFO` recommendation corresponds to pending information, **not** a final denial.

## 9. References

- [Papaya — Claims Automation](https://www.papaya.asia/solutions/claims-automation) — Public overview of document handling, medical necessity, benefits, fraud/waste/abuse screening, adjudication and evidence traceability.
- [Papaya — Claims Administration Services](https://www.papaya.asia/dich-vu-boi-thuong) — Public service overview.
- [Techcom Life — Claims handbook via Papaya](https://www.techcomlife.com/dich-vu-khach-hang/so-tay-khach-hang-giai-quyet-quyen-loi-bao-hiem-qua-doi-tac-papaya-81/) — Examples of document requirements by claim type.

**Evidence note:** These public references inform the general process. They do not verify the invented policy clauses or figures in the training example. Always use insurer-approved policies, clinical review rules, local regulations and delegated authority to assess real claims.
