# Claim Assessment AI Agent — Conversation Export

**Export date:** 2026-10-28  
**Format:** Markdown  
**Scope:** Conversation visible in the current thread, from the insurance process scenario through the request to export this conversation.

> **Export fidelity note:** This is a structured reconstruction of the conversation, **not a byte-for-byte ChatGPT transcript**. User messages are reproduced as shown. Earlier assistant responses are consolidated into faithful, detailed Markdown summaries and tables (rather than a literal copy of the interactive UI, expandable checklists, and every sentence). The previously generated full agent guideline is included verbatim in the appendix. For an exact platform transcript, use ChatGPT's native data export feature.

---

## Exchange 1 — Real-world insurance process scenario

### User

> Give me a real world scenario for a insurance company process:
> After a claim is submitted with supporting documents, an assessor reviews the claim against the policy terms, verifies documents, calculates benefits, and writes an assessment report with a recommendation (approve, reject, or request more information).

### Assistant — Scenario: Health Insurance Claim Assessment

**Illustrative claim:** John Smith files a health insurance reimbursement claim after emergency appendectomy.

| Field | Example |
|---|---|
| Insurer | ABC Health Insurance |
| Policy Number | HI-2026-00125 |
| Claim Number | CLM-2026-00456 |
| Insurance Plan | Comprehensive Health Insurance |
| Annual Sum Insured | $50,000 |
| Hospitalization | October 10–13, 2026 |
| Claim Submission | October 15, 2026 |
| Treatment | Emergency appendix surgery |
| Submitted Bill | $8,500 |
| Assigned Assessor | Sarah |

The walkthrough described the customer uploading a claim form, hospital invoice, medical diagnosis report, discharge summary, surgery report, and payment evidence. The assessor (1) validates the submission, (2) checks policy eligibility, (3) verifies evidence, (4) calculates benefits, (5) prepares an assessment report, and (6) recommends approve, reject, or request more information.

Illustrative policy checks included active coverage, insured membership, included surgery benefit, elapsed waiting period, available limit, $500 deductible, and 10% coinsurance after deductible.

| Calculation | Amount |
|---|---:|
| Total hospital bill | $8,500 |
| Noncovered private-room upgrade | -$500 |
| Eligible expenses | $8,000 |
| Deductible | -$500 |
| Coinsurance (10% of $7,500) | -$750 |
| **Recommended payout** | **$6,750** |
| Member responsibility | $1,750 |

The sample report recommended **approval of $6,750**, conditional on the company's final authorization requirements. Alternate outcomes were rejection for a well-supported applicable exclusion, or a request for information if necessary evidence was missing. The assessor's recommendation was distinguished from the insurer's final authorized decision.

---

## Exchange 2 — Must-have claim details

### User

> What are most must have claim details?

### Assistant — Essential claim information

The answer identified the minimum fields needed to identify, assess and track a claim.

| Field | Example |
|---|---|
| Claim ID | CLM-2026-00456 |
| Policy Number | HI-2026-00125 |
| Policyholder | John Smith |
| Claimant / Patient | John Smith |
| Claim Type | Inpatient Hospitalization |
| Submission Date | October 15, 2026 |
| Treatment Date | October 10, 2026 |
| Claim Reason | Emergency appendix surgery |
| Claimed Amount | $8,500 |
| Supporting Documents | Hospital bill, discharge summary, reports |
| Status | Under Assessment |
| Assigned Assessor | Sarah |

The assistant further recommended recording assessment fields: policy active, benefit included, exclusions, waiting period, document verification, eligible amount, deductible, coinsurance, recommended payment, rationale, recommendation and assessment date.

The proposed workflow statuses were **Submitted → Under Assessment → Approve / Reject / Request More Info**, with final authorization and payment handled separately.

The answer grouped system fields into Claim Information, Customer & Policy, Documents, Assessment and Decision, and noted that required fields vary by workflow stage.

---

## Exchange 3 — Four domain entities and real examples

### User

> Describe and provide real example in table format for entities:
> Claim details (type, amount, diagnosis, treatment dates)
> Policy data (benefits, limits, exclusions, copay)
> Document list (what was submitted, whether each doc is complete)
> Expected outcome (approve, reject, or request-more-info)

### Assistant — Entity examples

**Claim Details** contained Claim ID, Policy Number, Claimant, Type, Claimed Amount, Diagnosis, Treatment, Admission/Surgery/Discharge dates, Submission date, Hospital and Claim Status.

| Claim field | Example |
|---|---|
| Claim ID | CLM-2026-00456 |
| Type | Inpatient Hospitalization |
| Amount | $8,500 |
| Diagnosis | Acute Appendicitis |
| Treatment | Emergency Laparoscopic Appendectomy |
| Admission | October 10, 2026 |
| Surgery | October 11, 2026 |
| Discharge | October 13, 2026 |
| Hospital | City General Hospital |

**Policy Data** included number, type, policy status, effective/expiry dates, eligible benefits, annual limit, remaining limit, exclusions, deductible, coinsurance, waiting period and pre-existing-condition terms.

| Policy field | Example |
|---|---|
| Policy ID | HI-2026-00125 |
| Policy status | Active |
| Dates | Jan 1–Dec 31, 2026 |
| Benefits | Hospitalization, Surgery, Emergency Treatment |
| Annual limit | $50,000 |
| Remaining limit | $30,000 |
| Exclusions | Cosmetic surgery and nonmedical room upgrades |
| Deductible | $500 |
| Copay/coinsurance | 10% after deductible |
| Waiting period | 30 days for applicable nonemergency illness |

**Document List** tracked Submitted, Complete, Verification Status and Remarks separately. The example included Claim Form, Hospital Invoice, Discharge Summary, Diagnosis Report, Surgery Report, Payment Receipt, and Identity Document; all were marked submitted, complete and verified in the approval example.

**Expected Outcome / Assessment** recorded the assessment ID (ASM-2026-00981), assessor (Sarah Williams), coverage result, document status, benefit calculation, recommendation, reasoning, date and pending final authorization.

Three test outcomes were described:

| Scenario | Claim | Material condition | Expected outcome |
|---|---|---|---|
| A | Appendectomy, $8,500 | Covered and verified | APPROVE, $6,750 |
| B | Elective cosmetic treatment, $4,000 | Policy exclusion established | REJECT |
| C | Kidney stones, $6,000 | Surgery report missing | REQUEST_MORE_INFO |

Relationships: one policy to multiple claims; one claim to multiple documents; one claim to one or more assessment/reassessment records. Recommendation and final decision should be distinct.

---

## Exchange 4 — Who defines document requirements?

### User

> How do we know which documents need to be submitted for a claim type? Will each insurance company keep a check list or the assessor will decide it.

### Assistant — Company-maintained checklist plus assessor judgment

The answer explained that an insurer normally defines document requirements through claims operations/product/compliance teams. The claim system loads the applicable list; the assessor verifies completeness and may request additional evidence under company procedures.

| Claim Type | Typical Standard Documents | Conditional Documents |
|---|---|---|
| Hospitalization | Claim form, invoice, discharge summary, diagnosis report | Surgery report if operated |
| Outpatient | Consultation invoice, relevant medical record | Tests/labs if applicable |
| Accident | Claim form, accident details, medical report | Police report if applicable |
| Life/Death | Claim form, death certificate, identities, beneficiary records | Medical or police records |
| Critical Illness | Claim form, specialist diagnosis, tests | Biopsy/imaging for relevant diagnoses |
| Motor | Claim form, incident details, vehicle info, photos | Inspection, repair estimate, police report |
| Travel | Claim form, travel proof, loss evidence | Airline, baggage or medical records |

Recommended data entities: `ClaimType`, `DocumentType`, `DocumentChecklistRule`, `ClaimDocument`, `AdditionalDocumentRequest`. Requirements should be configurable by product, benefit, jurisdiction, effective dates and rule version.

Illustrative rule **BR-001**: after selecting claim type, the system loads its checklist; conditional requirements are activated by claim details (such as `surgery_performed = true`); missing material evidence is flagged and routed for a request rather than automatically rejected.

Examples cited in the original answer included public insurer claims pages from MSIG Vietnam, Chubb Vietnam, and ICICI Lombard.

---

## Exchange 5 — New assessor's operating guideline

### User

> Make a guideline for a new assessor that can start reviewing the claim against the policy terms, verifies documents, calculates benefits, and writes an assessment report with a recommendation (approve, reject, or request more information).
> The guideline Includes related entities need to checks, a defined clear workflow.

### Assistant — Assessor SOP

The assistant built an onboarding Standard Operating Procedure (SOP) and identified 10 entities: Claim Details, Insured Customer, Policy, Benefits and Limits, Document Checklist, Submitted Documents, Medical/Treatment Data, Claim History, Assessment, and Information Requests/Approvals.

The detailed workflow was:

1. Open and validate the claim.
2. Review policy terms and eligibility.
3. Determine the required documents.
4. Verify completeness and authenticity of documents.
5. Assess claim and medical eligibility.
6. Calculate benefits, exclusions, deductible and coinsurance.
7. Write a factual, evidence-supported assessment report.
8. Select one recommendation, then route for authorization or information follow-up.

The SOP included a reviewer checklist, example data for John Smith, a worked $6,750 payout, example approval report, distinctions between recommendation and authorized decision, and proposed statuses: Submitted, Assigned, Under Assessment, Pending Information, Assessment Completed, Pending Authorization, Approved/Rejected, Payment Processing and Closed.

Key controls: preserve document and clause evidence, refer specialized medical judgment, screen duplicate payments, record justified additional document requests, escalate suspect invoices without assuming fraud, and follow an authority matrix.

---

## Exchange 6 — Verify with Papaya and update report sections

### User

> Verify this workflow to real life insurance claims process. Can refer to papaya insurance claims process.
>
> Update the guideline with a structured report with these sections:
>
> 1. **Document Review** — list each document, its status (complete/incomplete/missing), and any issues
> 2. **Policy Verification** — confirm the policy is active, the member is covered, and the claim type is included
> 3. **Medical Necessity** — is the treatment appropriate for the diagnosis?
> 4. **Benefit Calculation** — submitted amount, covered amount, copay, member responsibility
> 5. **Recommendation** — APPROVE, REJECT, or REQUEST_MORE_INFO with specific reasoning
> 6. **Policy Citations** — every point in the recommendation must cite the specific policy clause it relies on

### Assistant — Verified workflow and six-section structured report

The assistant compared the workflow to publicly available Papaya Insurtech claims-automation and claims-administration descriptions, together with a Techcom Life/Papaya-assisted document guide. The comparison supported document classification, policy validation, medical necessity assessment, benefit calculation, fraud/waste/abuse screening, adjudication and audit-trail/citation requirements. It also clarified that vendor descriptions are not identical operating requirements for every insurer.

**Updated workflow:** Claim Intake → Document Review → Policy Verification → Medical Necessity → Benefit Calculation → Risk & Quality Screening → Policy-Cited Recommendation → Authorized decision or further evidence request.

The sample six-section report for claim CLM-2026-00456 was:

#### 1. Document Review

| Document | Required? | Status | Finding |
|---|---|---|---|
| Claim Form | Mandatory | Complete | Identity and policy match |
| Hospital Invoice | Mandatory | Complete | $8,500 itemized |
| Discharge Summary | Mandatory | Complete | Admission and discharge confirmed |
| Diagnosis Report | Case requirement | Complete | Acute appendicitis supported |
| Surgery Report | Conditional, surgery occurred | Complete | Appendectomy confirmed |
| Payment Evidence | Required for example reimbursement claim | Complete | Reconciles to invoice |
| Additional Medical Records | When necessary | Not required | Existing evidence sufficient |

#### 2. Policy Verification

| Check | Finding | Fictional clause |
|---|---|---|
| Policy effective | Jan 1–Dec 31, 2026 | §2.1 |
| Covered member | John Smith | §2.2 |
| Hospitalization covered | Yes | §3.1 |
| Surgery covered | Yes | §3.2 |
| Waiting period satisfied | Yes | §4.1 |
| Remaining limit | $30,000 | §5.1 |
| Nonmedical room upgrade excluded | $500 adjustment | §6.3 |

#### 3. Medical Necessity

Acute appendicitis was supported by diagnosis records. Laparoscopic appendectomy was consistent with the diagnosis and emergency treatment record. The reported stay had no unresolved inconsistency in the training example. Complex or disputed necessity should go to a qualified medical reviewer, not be decided solely from code/name matching.

#### 4. Benefit Calculation

| Component | Amount |
|---|---:|
| Submitted | $8,500 |
| Excluded nonmedical upgrade | -$500 |
| Eligible / covered | $8,000 |
| Deductible | -$500 |
| Coinsurance (10% × $7,500) | -$750 |
| **Insurer payable** | **$6,750** |
| **Member responsibility** | **$1,750** |

#### 5. Recommendation

`APPROVE` payment of `$6,750`, because insured coverage, hospitalization/surgery benefits, sufficient documentation, and medical necessity were established in the illustrative case. The recommendation included separate cited findings for effective policy, covered member, benefit, medical necessity, noncovered upgrade, deductible, coinsurance and available limit. `REJECT` was reserved for evidence-supported policy disqualification; `REQUEST_MORE_INFO` for necessary but unresolved evidence.

#### 6. Policy Citations

All sample clauses were explicitly **fictional training placeholders**, not real Papaya or insurer contract provisions:

| Fictional clause | Intended illustration |
|---|---|
| §2.1 | Effective policy coverage period |
| §2.2 | Eligible member |
| §3.1 | Inpatient hospitalization benefit |
| §3.2 | Medically necessary surgery |
| §4.1 | Waiting period |
| §5.1 | Annual limit |
| §5.2 | Deductible |
| §5.3 | Coinsurance |
| §6.1 | Qualifying elective cosmetic exclusion |
| §6.3 | Nonmedical room-upgrade exclusion |
| §7.1 | Required claim documentation |

Citation requirements: identify policy number, version, clause, page or stable location, quoted/precise operative text, relevant treatment date, and evidence references. An illustrative record paired §6.3 with invoice INV-001 line 7 to justify the $500 exclusion.

The final quality gates and business rules `BR-01` through `BR-08` checked valid policy version, document status, medical evidence, calculation reconciliation, cited recommendation, resolution of missing evidence, specialist referral, and separation of final authorization.

**Public reference links shared in the answer:**

- https://www.papaya.asia/solutions/claims-automation
- https://www.papaya.asia/dich-vu-boi-thuong
- https://www.techcomlife.com/dich-vu-khach-hang/so-tay-khach-hang-giai-quyet-quyen-loi-bao-hiem-qua-doi-tac-papaya-81/

---

## Exchange 7 — Export agent guideline to Markdown

### User

> export the guideline to md file that agent can easier read

### Assistant

The assistant created `insurance_claim_assessment_agent_guideline.md`, a 315-line agent-facing Markdown guideline with operating rules, claim entities, eight-step workflow, six-part assessment report, fictional illustrative claim data, decision rules, policy citation standards and validation checks.

The original file is reproduced in the appendix below.

---

## Exchange 8 — Export conversation

### User

> export all this conversation to md file

### Assistant

Created this Markdown conversation archive. It preserves the user's prompts and a structured account of each substantive assistant response. The existing full agent guideline is also appended so the complete practical specification is available in a single file.

---

# Appendix A — Complete Previously Exported Agent Guideline

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
