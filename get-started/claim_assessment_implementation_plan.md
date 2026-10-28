# Claim Assessment AI Agent — Implementation Plan

## 1. Objective

Build a prototype that assesses three fictional insurance claims and produces a structured report for a human assessor. The application reads sample JSON, verifies documents and policy eligibility, checks medical necessity, calculates benefits, recommends APPROVE, REJECT, or REQUEST_MORE_INFO, and provides an evidence-backed report for human authorization or override.

Use OpenRouter for language generation. The application controls calculations and recommendations; the LLM does not invent policy clauses, decide payment independently, or authorize a claim. All policy clauses, clinical results, documents, and claim amounts in the prototype are fictional fixtures.

## 2. Architecture

| Component | Responsibility |
|---|---|
| Claim loader | Load and validate a selected sample claim. |
| Assessment context | Hold the claim, member, treatment dates, checklist, and verified policy and benefit data. |
| Four assessment tools | Return deterministic results using sample JSON. |
| Orchestrator | Run tools in order, enforce prerequisites, handle errors, and record audit events. |
| Decision engine | Apply explicit rules to tool results and determine the recommendation. |
| Report builder | Assemble the six report sections from verified results and citations. |
| OpenRouter client | Draft reviewer-facing explanations from supplied assessment results. |
| Report validator | Check schema, calculation, evidence links, citations, and decision guardrails. |
| Human review | Record authorization or override, reviewer, reason, and time. |

## 3. Sample data

```text
sample_data/
├── claims.json
├── policies.json
├── documents.json
├── document_checklists.json
├── clinical_rules.json
├── benefit_balances.json
└── submission_deadlines.json
```

| File | Contents |
|---|---|
| `claims.json` | Claim IDs, members, dates, reported diagnosis and procedures, amounts, and document references. |
| `policies.json` | Fictional coverage periods, benefits, exclusions, waiting periods, cost-sharing, and exact clause text. |
| `documents.json` | Simulated detected types, completeness, issues, and extracted facts. |
| `document_checklists.json` | Required and conditional documents by claim type. |
| `clinical_rules.json` | Fictional diagnosis-and-procedure combinations and simulated results. |
| `benefit_balances.json` | Remaining benefit limits and balance information. |
| `submission_deadlines.json` | Claim submission rule sets (deadline days by claim type, anchor date, exact rule text, source and version), mapped to the policies they apply to. |

## 4. Main tools

| Tool | Deterministic prototype behavior |
|---|---|
| `verifyDocument(documentId)` | Find a document and return its detected type, completeness, issues, and extracted facts. The orchestrator compares results against the checklist. |
| `lookupPolicy(policyId)` | Retrieve the applicable policy fixture and check the policy period, member, benefits, waiting period, claim submission deadline, exclusions, cost-sharing, and limits using the assessment context. Return the version and exact clauses. |
| `checkMedicalNecessity(diagnosis, procedures)` | Match verified clinical facts against `clinical_rules.json`; return `SUPPORTED`, `NOT_SUPPORTED`, `INSUFFICIENT_EVIDENCE`, or `REFER_TO_MEDICAL_REVIEW`. |
| `calculateBenefit(policyId, claimType, amount)` | Apply verified policy terms and the benefit balance using decimal arithmetic. Return a complete calculation or `PENDING` when necessary inputs are unresolved. |

Unknown documents, policies, clinical rules, or benefit balances produce explicit unresolved results. They do not become assumptions.

### Input-to-parameter mapping

| Claim or verified data | Tool parameter |
|---|---|
| Each submitted document ID | `verifyDocument(documentId)` |
| Policy ID | `lookupPolicy(policyId)` |
| Diagnosis and procedures supported by document evidence | `checkMedicalNecessity(diagnosis, procedures)` |
| Policy ID, claim type, and submitted amount | `calculateBenefit(policyId, claimType, amount)` |

Claimant-reported diagnosis and procedures are not verified until supported by document review. The server-controlled assessment context supplies information not included in the public tool signatures.

## 5. Assessment workflow

1. Load and validate identifiers, dates, document references, currency, and monetary amounts.
2. Create the server-controlled assessment context.
3. Verify each submitted document and compare results with the applicable checklist.
4. Look up policy terms and verify coverage on the treatment date.
5. Assess medical necessity when sufficient verified clinical evidence exists.
6. Calculate benefits when necessary eligibility and calculation inputs are established.
7. Apply decision rules to verified results.
8. Assemble the report, request reviewer-facing explanations from OpenRouter, and validate the report.
9. Submit the recommendation for human review. Record it separately from final authorization.

Tool errors and skipped steps are explicit unresolved results.

## 6. OpenRouter integration

The backend calls the OpenRouter Chat Completions API (OpenAI-compatible) directly over HTTPS. The API key is a bearer token read from the `OPENROUTER_API_KEY` environment variable or a secret manager, never hardcoded or committed. The model receives relevant verified results and drafts explanations for the assessor. No local model installation is needed.

Reference request (the key comes from the environment):

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "openai/gpt-4o",
  "messages": [
    { "role": "user", "content": "<verified assessment facts and drafting instructions>" }
  ]
}'
```

The reply text is in `choices[0].message.content`. The response also returns the model that actually served the request, a response `id`, and token `usage`. Always set `max_tokens` (default 1000). Without it, OpenRouter reserves the model's full output budget against the key's credit limit and can reject the request with HTTP 402.

Whether a model enforces structured output depends on the model OpenRouter routes to, so application code always builds the report JSON itself. The model is asked for a JSON object of explanations, and that output is parsed and validated. Invalid output gets a bounded retry or goes to review, and never triggers an automatic claim decision. Validate model explanations against source facts and citations before presentation.

Pick a specific model (`OPENROUTER_MODEL`, default `openai/gpt-4o`) through testing. Record the model identifier, the served model, the response ID and the configuration with each assessment. OpenRouter forwards requests to third-party model providers, so review OpenRouter's and the upstream provider's data handling and organizational requirements before sending real claim or medical information.

### Claim submission deadline (reimbursement claims)

| Benefit | Deadline | Counted from |
|---|---|---|
| Standard medical treatment (inpatient / outpatient) | 60 days | Last date of treatment or discharge date |
| Maternity | 180 days | Date of childbirth or completion of treatment |

The deadlines are a separate data source, `submission_deadlines.json`, not part of each policy. `lookupPolicy` looks up the rule set that applies to the policy and records the `submission_deadline` check, citing the exact rule text, source document and version (citation kind `RULE`). A reimbursement claim submitted after the deadline is a `FAIL` and a specific denial basis, routed for human denial review. If the claim mode or the deadline for the claim type is unknown, the check is `UNCERTAIN` and the assessment is escalated, not decided.

## 7. Decision rules

| Outcome | Required conditions |
|---|---|
| `APPROVE` | Required evidence is sufficient; coverage is established; medical necessity and required reviews are resolved; calculation is complete; payment is within the applicable limit; citations and evidence are valid. |
| `REJECT` | Evidence establishes a specific denial basis supported by an applicable policy clause. Route for human denial review. |
| `REQUEST_MORE_INFO` | Material information is missing or incomplete. Include at least one specific open request explaining what is needed, why, and who should provide it. |

If a finding cannot be resolved through an information request, such as an unavailable policy record or a required clinical review, keep the assessment pending review. Do not force an unsupported approval or rejection.

## 8. Assessment report

| Section | Required content |
|---|---|
| **1. Document Review** | Each expected document, `COMPLETE`, `INCOMPLETE`, or `MISSING` status, submitted and detected types, issues, and evidence references. |
| **2. Policy Verification** | Policy active on the treatment date, member coverage, claim-type coverage, and applicable waiting periods, exclusions, and limits. Each check is `PASS`, `FAIL`, or `UNCERTAIN`. |
| **3. Medical Necessity** | Diagnosis, treatment, result, rationale, clinical source, supporting evidence, and outstanding concerns. |
| **4. Benefit Calculation** | Submitted amount, covered and excluded amounts, deductible, copay, coinsurance, insurer payable, member responsibility, and applicable remaining limit. |
| **5. Recommendation** | Outcome, specific reasons, recommended payment when known, information requests or escalations, and next action. |
| **6. Policy Citations** | Exact applicable clause text, policy document, version, clause ID, and location. Recommendation reasons link to citations and evidence. |

Include claim identifiers, assessment metadata, audit reference, citation-validation status, and human-review record. If a document declared as a medical report is an appointment confirmation, show the submitted document and mismatch; the required medical report remains `MISSING`.

Document requirements from a checklist cite the checklist as their procedural source. If an applicable policy clause cannot be established, mark the point unverified and route it for review; do not invent a clause. Unresolved calculation amounts are `null`, not zero.

## 9. Three-case execution simulation

### Case 1 — Straightforward approval

Parsed input: `CLM-APP-001`, `POL-APP-001`, outpatient claim, USD 200.00 submitted, and documents `A-D1` through `A-D4`.

| Step | Call or action | Fictional result |
|---|---|---|
| Documents | `verifyDocument("A-D1")` through `verifyDocument("A-D4")` | Required documents complete; medical report supports diagnosis and treatment. |
| Policy | `lookupPolicy("POL-APP-001")` | Coverage active; outpatient benefit included; waiting period satisfied; USD 20.00 copay; USD 800.00 remaining limit. |
| Medical | `checkMedicalNecessity("Acute bacterial sinusitis", ["Outpatient consultation", "Prescribed treatment"])` | `SUPPORTED` by a fictional clinical rule. |
| Benefit | `calculateBenefit("POL-APP-001", "OUTPATIENT", "200.00")` | USD 200.00 covered; USD 20.00 copay; USD 180.00 payable; USD 20.00 member responsibility; USD 620.00 remaining. |

Expected recommendation: `APPROVE`, subject to human authorization.

### Case 2 — Rejection under an exclusion

Parsed input: `CLM-REJ-001`, `POL-REJ-001`, elective cosmetic rhinoplasty, USD 2,000.00 submitted, and documents `R-D1` through `R-D4`.

| Step | Call or action | Fictional result |
|---|---|---|
| Documents | Verify `R-D1` through `R-D4` | Medical report documents an elective cosmetic procedure with no medical indication. |
| Policy | `lookupPolicy("POL-REJ-001")` | Returns the applicable fictional cosmetic-procedure exclusion. |
| Medical | `checkMedicalNecessity(null, ["Elective cosmetic rhinoplasty"])` | `NOT_SUPPORTED` by the matching fictional rule. The fixture explicitly establishes absence of a medical diagnosis. |
| Benefit | `calculateBenefit("POL-REJ-001", "OUTPATIENT", "2000.00")` | USD 2,000.00 excluded; USD 0.00 payable; USD 2,000.00 member responsibility. |

Expected recommendation: `REJECT`, supported by the medical report and specific exclusion, subject to human denial review. A `null` diagnosis alone does not mean no medical indication; missing evidence yields `INSUFFICIENT_EVIDENCE`.

### Case 3 — Request more information

Parsed input: `CLM-RFI-001`, `POL-RFI-001`, outpatient claim, USD 300.00 submitted, and documents `I-D1` through `I-D4`.

| Step | Call or action | Fictional result |
|---|---|---|
| Documents | Verify `I-D1` through `I-D4` | `I-D4` is an appointment confirmation; the required medical report remains `MISSING`. |
| Policy | `lookupPolicy("POL-RFI-001")` | Active coverage and outpatient terms are found. |
| Medical | Tool not called | Insufficient verified clinical evidence; record `INSUFFICIENT_EVIDENCE`. |
| Benefit | Tool not called | Record `PENDING`; unresolved amounts remain `null`. |

Expected recommendation: `REQUEST_MORE_INFO` for a medical report, with checklist requirement, relevant policy condition, and reassessment trigger recorded.

## 10. Orchestrator pseudocode

```python
def assess_claim(claim_id):
    claim = load_and_validate_claim(claim_id)
    context = create_assessment_context(claim)
    checklist = load_checklist(claim.claim_type, context)
    audit = start_audit(claim.claim_id, context.version)

    documents = []
    for submitted in claim.documents:
        result = safe_tool_call(
            audit, "verifyDocument", {"documentId": submitted.document_id},
            lambda: verifyDocument(submitted.document_id, context),
        )
        documents.append(result)
    document_review = compare_to_checklist(checklist, documents)

    policy = safe_tool_call(
        audit, "lookupPolicy", {"policyId": claim.policy_id},
        lambda: lookupPolicy(claim.policy_id, context),
    )
    facts = extract_verified_clinical_facts(document_review)
    if facts.are_sufficient:
        medical = safe_tool_call(
            audit, "checkMedicalNecessity",
            {"diagnosis": facts.diagnosis, "procedures": facts.procedures},
            lambda: checkMedicalNecessity(facts.diagnosis, facts.procedures, context),
        )
    else:
        medical = insufficient_evidence_result()
        audit.record_skipped_step("checkMedicalNecessity", medical.reason)

    if calculation_inputs_are_sufficient(claim, document_review, policy, medical):
        benefit = safe_tool_call(
            audit, "calculateBenefit",
            {"policyId": claim.policy_id, "claimType": claim.claim_type,
             "amount": claim.submitted_amount.amount},
            lambda: calculateBenefit(claim.policy_id, claim.claim_type,
                                     claim.submitted_amount.amount, context),
        )
    else:
        benefit = pending_calculation()
        audit.record_skipped_step("calculateBenefit", "Required inputs are unresolved.")

    recommendation = apply_decision_guardrails(document_review, policy, medical, benefit)
    report = build_report_from_verified_results(
        claim, document_review, policy, medical, benefit, recommendation
    )
    report.explanations = draft_explanations_with_openrouter(report)
    validate_report_and_citations(report)
    report.audit_reference = audit.reference
    report.human_review.authorization_status = "PENDING"
    return report
```

`safe_tool_call` records calls and converts errors into unresolved results. Context is an implementation dependency; the public tool parameters remain the four agreed signatures.

## 11. Validation and audit requirements

Before presenting a report:

- Validate structure and allowed status values.
- Ensure each material recommendation reason has supporting evidence and an applicable policy citation; citation IDs must exist and match the policy version returned by `lookupPolicy`.
- Reconcile submitted charges, adjustments, payable amount, and member responsibility according to the applicable rules; confirm payment does not exceed the applicable remaining limit.
- Ensure each document finding refers to a submitted document or explicitly missing checklist requirement.
- Ensure `REQUEST_MORE_INFO` includes an open request.
- Keep final authorization `PENDING` until an authorized human acts.

The audit trail records every tool call's input, output or secure output reference, status, timestamp, tool version, and context version, plus skipped steps and reasons. An override records the reviewer, decision, reason, and time.

## 12. Implementation and test sequence

1. Define fixture schemas and create the three sample cases.
2. Implement the four deterministic tools and server-controlled context.
3. Implement the orchestrator, decision rules, report builder, and validation.
4. Integrate OpenRouter for reviewer-facing explanations.
5. Run the three expected scenarios and verify their reports.
6. Test missing or mismatched documents, unknown policy, missing balance, unmatched clinical rule, tool error, invalid citation, and malformed model response.
7. Compare OpenRouter models on quality, latency, and cost; select one based on results.
8. Add a human-review mechanism that records approval or override.

The prototype is ready for demonstration when the three cases produce the expected recommendations, failures remain unresolved, and a reviewer can trace every material recommendation reason to evidence and policy terms.
