# Test case matrix

This matrix lists every claim scenario the agent handles: the three sample cases and the edge cases around them, grouped by outcome. Each row was run end-to-end through `assess_claim` on 2026-10-29. The **Actual** column is what the code returned on that run.

Each edge case starts from one of the three sample claims (`CLM-APP-001`, `CLM-REJ-001` or `CLM-RFI-001`) and changes one fact. The agent can reach four outcomes:

| Outcome | Status | Meaning |
|---|---|---|
| **Approve** | Ready for authorization | Every check passed; an approver authorizes payment. |
| **Reject** | Ready for authorization | A failed check is proven by evidence and backed by a policy clause or rule; a senior assessor does a denial review. |
| **Request more information** | Waiting for information | A required document is missing or doesn't match; the claim is held until it arrives. |
| **Pending review** (no outcome) | Escalated | Something can't be resolved by asking for a document, such as a missing policy record or a clinical question; a specialist decides. |

Symbols: ✅ the actual result is correct. ⚠️ the actual result is a defect (see [Known defects](#known-defects)).

## Approve

| ID | Scenario | Change from sample claim | Expected | Actual | Payable | Test |
|---|---|---|---|---|---|---|
| A1 | Sample approval: outpatient sinusitis | None (`CLM-APP-001`) | Approve | ✅ Approve | 180.00 | `test_case_1_straightforward_approval` |
| A2 | Submitted on the deadline day | Submission date 2026-11-14, day 60 after treatment | Approve | ✅ Approve | 180.00 | `test_submission_on_deadline_day_passes` (tool level) |
| A3 | Payable capped by the remaining limit | Remaining limit 100.00 instead of 800.00 | Approve, payable capped | ✅ Approve | 100.00 | `test_payable_is_capped_at_remaining_limit` (tool level) |
| A4 | Direct billing claim (deadline doesn't apply) | Claim mode `DIRECT_BILLING` | Approve | ⚠️ Approve with status Escalated, validation Fail | 180.00 | `test_deadline_does_not_apply_to_direct_billing` (tool level) |
| A5 | LLM returns invalid output twice | Model replies with malformed JSON | Approve; explanations Failed | ✅ Approve | 180.00 | `test_malformed_model_response_never_changes_decision` |

## Reject

| ID | Scenario | Change from sample claim | Expected | Actual | Payable | Test |
|---|---|---|---|---|---|---|
| R1 | Sample rejection: cosmetic rhinoplasty, no medical indication | None (`CLM-REJ-001`) | Reject (exclusion REJ-6.4) | ✅ Reject | 0.00 | `test_case_2_rejection_under_exclusion` |
| R2 | Waiting period not met | Member cover starts 2026-09-01, treatment 2026-09-15 (30-day wait) | Reject (APP-4.1), payable 0.00 | ⚠️ Reject | 180.00 | `test_waiting_period_failure_rejects_with_clause` |
| R3 | Submitted after the 60-day deadline | Submission date 2026-11-15, day 61 | Reject (rule CSR-2.1), payable 0.00 | ⚠️ Reject | 180.00 | `test_late_reimbursement_claim_rejects_with_deadline_clause` |
| R4 | Policy not active | Policy status `LAPSED` | Reject (APP-2.1), payable 0.00 | ⚠️ Reject | 180.00 | None (script only) |
| R5 | Treatment after the policy expired | Policy ends 2026-08-31, treatment 2026-09-15 | Reject (APP-2.1), payable 0.00 | ⚠️ Reject | 180.00 | `test_policy_not_active_on_treatment_date` (tool level) |
| R6 | Member's cover ended before treatment | Member cover ends 2026-08-31 | Reject (APP-2.2), payable 0.00 | ⚠️ Reject | 180.00 | None (script only) |
| R7 | Member not named on the policy | Claim member isn't in the policy's member list | Reject (APP-2.2), payable 0.00 | ⚠️ Reject | 180.00 | `test_member_not_on_policy` (tool level) |
| R8 | Benefit not covered by the policy | Outpatient benefit `covered: false` | Reject (APP-3.1), payable 0.00 | ⚠️ Reject | 180.00 | None (script only) |
| R9 | Annual limit used up | Remaining limit 0.00 | Reject (APP-5.1) | ✅ Reject | 0.00 | None (script only) |

## Request more information

| ID | Scenario | Change from sample claim | Expected | Actual | Payable | Test |
|---|---|---|---|---|---|---|
| I1 | Sample RFI: "medical report" is an appointment confirmation | None (`CLM-RFI-001`) | Request medical report from provider | ✅ Request more information | Pending (`null`) | `test_case_3_request_more_information` |
| I2 | Payment receipt not submitted | Remove `A-D3` from the claim | Request payment receipt | ✅ Request more information | Pending | None (script only) |
| I3 | Itemized invoice not submitted | Remove `A-D2` from the claim | Request invoice | ✅ Request more information | Pending | None (script only) |
| I4 | Document service fails on the medical report | `verifyDocument(A-D4)` times out | Medical report Missing; request it | ✅ Request more information | Pending | `test_document_tool_error_leaves_requirement_missing` |
| I5 | Claim form names a different member | Claim form member ID `MEM-SOMEONE-ELSE` | Claim form Missing; never Approve | ✅ Request more information | Pending | `test_identity_mismatch_is_not_accepted` |
| I6 | Claimed amount doesn't match the invoice | Claimed 250.00, invoice 200.00 | Never Approve; amount unresolved | ✅ Request more information | Pending | `test_amount_not_matching_verified_invoice_is_pending` (tool level) |

## Pending review (escalated)

| ID | Scenario | Change from sample claim | Expected | Actual | Payable | Test |
|---|---|---|---|---|---|---|
| E1 | Policy record not found | Remove `POL-APP-001` | Pending review | ✅ Escalated | Pending | `test_unknown_policy_is_escalated_not_decided` |
| E2 | Benefit balance record not found | Remove all balances | Pending review | ✅ Escalated | Pending | `test_missing_balance_is_escalated` |
| E3 | Procedure matches no clinical rule | Procedures include "MRI scan" | Refer to medical review | ✅ Escalated | Pending | `test_unmatched_clinical_rule_is_referred` |
| E4 | Mixed functional and cosmetic surgery | Septorhinoplasty for airway obstruction (rule CR-003) | Refer to medical review | ✅ Escalated | Pending | `test_combined_functional_and_cosmetic_surgery_is_referred` (tool level) |
| E5 | Medical necessity tool fails | `checkMedicalNecessity` raises an error | Refer to medical review | ✅ Escalated | Pending | `test_tool_error_becomes_unresolved_result` |
| E6 | Claim mode not stated | `claim_mode` empty | Deadline Uncertain; pending review | ✅ Escalated | Pending | `test_missing_claim_mode_is_escalated` |
| E7 | Diagnosis empty, but no explicit "no medical indication" finding | `medical_indication_present` empty on `R-D4` | Never Reject; pending review | ✅ Escalated | Pending | `test_null_diagnosis_without_explicit_finding_never_rejects` |
| E8 | Policy has no entry for the claim type | No outpatient benefit on the policy | Benefit Uncertain; pending review | ✅ Escalated | Pending | `test_benefit_missing_from_policy_is_uncertain_not_fail` (tool level) |
| E9 | No submission rules for the policy | Policy not in any rule set | Deadline Uncertain; pending review | ✅ Escalated | Pending | `test_policy_without_submission_rules_is_uncertain` (tool level) |

## Claim not accepted for assessment

These claims stop at intake with a validation error, before any tool runs.

| ID | Scenario | Change | Actual | Test |
|---|---|---|---|---|
| X1 | Unknown claim ID | `CLM-NOPE-001` | ✅ Error: claim not found | `test_unknown_claim_raises` |
| X2 | Treatment ends before it starts | End date before start date | ✅ Error | `test_rejects_treatment_end_before_start` |
| X3 | Submitted before treatment | Submission date before treatment start | ✅ Error | `test_rejects_submission_before_treatment` |
| X4 | Invalid amount, missing currency, malformed date, no documents | Each changed separately | ✅ Error | `tests/test_context.py` |

## Known defects

1. **A Reject recommends paying the claim (R2–R8).** When the denial is for eligibility (waiting period, late submission, inactive policy, member not covered, benefit not covered), the benefit calculator still computes 180.00. The Reject recommendation carries that amount, and the report validator doesn't catch the contradiction. Only exclusion-based denials (R1) and an exhausted limit (R9) show 0.00. The decision itself is correct and still goes to human denial review.
2. **A direct-billing claim can never be approved (A4).** The submission deadline correctly doesn't apply, so it has no rule to cite. The Approve reason "Submitted on time" is still added without a citation, so validation fails and the claim is escalated. This fails safe (a human reviews it), but a valid claim never reaches Approve.

"Tool level" means the test checks the tool's result but not the final recommendation. "Script only" means the row was verified with a one-off script and has no automated test yet.
