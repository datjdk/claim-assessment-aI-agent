# CLAUDE.md

This file guides Claude Code when working in this repository.

## Project

A prototype **claim assessment AI agent**. It does the first-pass assessment of a health insurance claim and produces an evidence-backed report for a human assessor, which cuts turnaround from days to minutes. It **recommends** `APPROVE`, `REJECT`, or `REQUEST_MORE_INFO`. A human always authorizes or overrides.

Source specs (read these before making design decisions):
- [get-started/claim_assessment_implementation_plan.md](get-started/claim_assessment_implementation_plan.md): architecture, tools, workflow, decision rules, three test cases, orchestrator pseudocode.
- [get-started/insurance_claim_assessment_agent_guideline.md](get-started/insurance_claim_assessment_agent_guideline.md): operating guideline (SOP), guardrails, full report template, validation checklist, status lifecycle.

Status: plan steps 1–6 and 8 are implemented; step 7 (comparing models) is not. All three acceptance cases produce the expected recommendations.

Layout of `src/claim_agent/`:
- `context.py`: intake validation and `AssessmentContext`. `verified_facts` holds only facts from verified documents.
- `tools/`: the four deterministic tools. Each has a `TOOL_VERSION`.
- `document_review.py`: compares documents with the checklist, cross-checks identity, amounts and dates, promotes verified facts, and builds information requests.
- `orchestrator.py`: `assess_claim()` runs docs → review → policy → medical → benefit → decision → report → LLM → validation, and records every call through `safe_tool_call`.
- `decision.py`: guardrails in order: REJECT, then REQUEST_MORE_INFO, then ESCALATED (outcome `None`), then APPROVE.
- `report.py`: builds the report dict. `CitationRegistry` assigns `PC-nn` IDs.
- `validator.py`, `human_review.py`, `audit.py`, `render.py` (Markdown), `cli.py`.

Stack: Python, compatible with 3.9 (`from __future__ import annotations`), stdlib only. Money values in fixtures are strings and are parsed with `Decimal`.

Run the agent: `PYTHONPATH=src python3 -m claim_agent.cli CLM-RFI-001` (or `--all`) `[--llm] [--format text|md|json | --md | --json] [--no-color] [--out reports]`. The default `text` format is for terminals (`render.render_text`): it wraps to the terminal width, adds color only on a TTY without `NO_COLOR`, and prints the tool call log one line per call as `seq STATUS tool(args) -> result`. Arguments are shortened at whole-argument boundaries before anything else, and the full input and output stay in the JSON audit trail. `md` (also written by `--out`) keeps the six-section template, with a full untruncated log that includes times. `--llm` needs `OPENROUTER_API_KEY`. `reports/` is gitignored.

The unit tests for `create_assessment_context` and the four tools were written first, as the behavior contract. Make the code satisfy them; don't weaken them. `tests/helpers.py::verified_context` copies the orchestrator's fact promotion so each tool can be tested on its own.

Known limitation: the LLM validator checks that the IDs, amounts and outcomes in an explanation exist in the facts. It does not check that the model used them correctly (for example, citing a real clause for the wrong point).

Open issue (not fixed): in the live CLM-RFI-001 run, gpt-4o's explanation said the information request "has been sent" (it is only `OPEN`, waiting for a human) and said the medical report is required under RFI-3.2 (the requirement comes from RFI-7.2). The proposed fix is to tighten the system prompt (no describing actions as done; cite a clause only for what it states). (Compact JSON is now sent; see below.)

Decisions:
- The `LLM_CALL` audit event stores the exact request body sent (`input.request_body`: model, messages, temperature, max_tokens) and, for each attempt, the reply text, the full response body and any validation problems (`output.exchanges[].raw_content`, `.response_body`, `.validation_problems`). The API key lives only in the HTTP header and is never stored. The text and `--md` output show the full request messages and response message for every LLM call (section "LLM request and response (OpenRouter)"); `--no-llm-payload` hides it. Tool call log events, in order: `verifyDocument` ×n, `STEP documentReview` (checklist result and gaps), `lookupPolicy`, `checkMedicalNecessity` and `calculateBenefit` (or `SKIPPED` with a specific reason naming the missing requirement or blocker, e.g. `Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.`; the report's medical concern and pending reason use the same text), `STEP decide`, then one `LLM_REQUEST openrouter.chat(attempt n)` per HTTP call to OpenRouter, recorded when it happens through `draft_explanations(on_exchange=...)`. Each of those is followed by short `↳ request <role> (N chars): …` and `↳ response (N chars): …` lines (72-character previews). Then the `LLM_CALL draftExplanations` summary and `STEP validateReport` (final status). `--llm-raw` adds the full raw request body (exact JSON sent) and raw response bodies under the summary, one line each and never truncated. OpenRouter pads its responses with keep-alive whitespace; the log trims it, but `exchanges[].response_raw` keeps the exact text (the transport returns `llm.RawJSON`, a dict that carries `raw_text`).
- Rendered output (terminal and `--md`) shows plain-text labels for result codes through `labels.label()` (e.g. `REQUEST_MORE_INFO` is shown as "Request more information"; unknown codes fall back to sentence case). Report data, JSON output, the validator and the tool call log keep the codes. Section headings show their result as `## 1. Document Review (Unresolved items)`, from `render.section_results`.
- An SLF4J-style log format was proposed and the user rejected it. Don't reintroduce it.
- The facts are sent to the LLM as compact JSON (`separators=(",", ":")`), about 27% fewer characters than indented JSON. OpenRouter key limits can reject a prompt as too large (HTTP 402 "Prompt tokens limit exceeded").
- Current model (set in `.env`): `recursive/flint-v1.0:free`. It's a free reasoning model, and its upstream capacity is shared, so it often returns HTTP 429. Settings: `OPENROUTER_MAX_TOKENS` (default 1000; Flint needs about 4000, because reasoning used 972 of 1000 tokens and left `content: null`) and `OPENROUTER_REASONING_EFFORT` (minimal|low|medium|high, sent as `{"reasoning":{"effort":…}}`; currently `low`). An empty answer with `finish_reason: length` raises a non-retryable error that names the reasoning tokens and says to raise `OPENROUTER_MAX_TOKENS`. Live run on 2026-10-28: all three cases were drafted and passed validation, at about 3.4–4.3K prompt and 1.9–2.4K completion tokens, with 429s on some first attempts.
- Retry backoff: before a retry, wait `retry_delay_s` × 2^(attempt−1) (2s, then 4s), or the server's `Retry-After` when sent. `draft_explanations(sleep=...)` is injectable, and tests use `LLMConfig(retry_delay_s=0)`.
- Retry policy: `LLMError.retryable`. Retry HTTP 429, 5xx, timeouts, network errors and unusable responses; stop after the first attempt on any other 4xx (400, 401, 402, 403, 404, 422). The exchange records `http_status` and `retryable`, and the errors list ends with "Not retried: …". Invalid model output is still retried up to `max_attempts`.

Run tests (no install needed): `PYTHONPATH=src python3 -m unittest discover -s tests -v`. With dev deps installed, `pytest` also works.

## Core principle: deterministic code decides, the LLM only explains

- Tools, the orchestrator, the decision engine, the benefit calculator, and the report builder are **deterministic application code**.
- The LLM (via OpenRouter) **only drafts reviewer-facing explanations** from verified results it is given. It never invents policy clauses, decides payment, picks the recommendation, or authorizes a claim.
- Application code builds the report JSON. Structured-output enforcement depends on the model OpenRouter routes to, so the app never relies on it. If model output should contain JSON, parse and validate it. Invalid output gets a bounded retry or goes to review, and never triggers an automatic decision. Validate model explanations against source facts and citations.
- OpenRouter (`POST https://openrouter.ai/api/v1/chat/completions`, OpenAI-compatible) is called from [src/claim_agent/llm.py](src/claim_agent/llm.py) with stdlib `urllib`, and the HTTP transport can be swapped out in tests. The key comes from `OPENROUTER_API_KEY` and the model from `OPENROUTER_MODEL` (default `openai/gpt-4o`). Never hardcode, log or commit the key. `ignore/` (gitignored) may hold a local copy of the key; never copy, print or commit it. The key is now provided through `.env` in the project root (gitignored, mode 600, template in `.env.example`). With `--llm`, the CLI loads it via `envfile.load_env_file` (or `--env-file PATH`), and variables already exported in the shell take precedence. There is deliberately no `--api-key` flag, because it would leak into shell history and the process list. Record `LLMConfig.describe()`, the served model and the response ID with each assessment.
- All policies, clauses, clinical rules, documents, and amounts are **fictional fixtures**.

## Architecture

| Component | Responsibility |
|---|---|
| Claim loader | Load and validate a sample claim (IDs, dates, doc refs, currency, amounts). |
| Assessment context | Server-controlled state: claim, member, treatment dates, checklist, verified policy/benefit data. |
| 4 tools | Deterministic lookups over `sample_data/`. |
| Orchestrator | Runs tools in order, enforces prerequisites, converts errors to unresolved results, writes the audit trail. |
| Decision engine | Explicit rules → recommendation. |
| Report builder | Six report sections from verified results and citations. |
| OpenRouter client | Drafts explanations only. |
| Report validator | Schema, calculation reconciliation, evidence links, citations, guardrails. |
| Human review | Records authorization/override: reviewer, decision, reason, time. |

### Tools (public signatures are fixed; context is passed as an implementation dependency)

- `verifyDocument(documentId)` returns detected type, completeness, issues, and extracted facts. The orchestrator compares the results with the checklist.
- `lookupPolicy(policyId)` checks period, member, benefits, exclusions, waiting period, cost-sharing, and limits against the context. Returns the version and **exact clauses**.
- `checkMedicalNecessity(diagnosis, procedures)` returns `SUPPORTED | NOT_SUPPORTED | INSUFFICIENT_EVIDENCE | REFER_TO_MEDICAL_REVIEW`.
- `calculateBenefit(policyId, claimType, amount)` uses **decimal arithmetic** (never float). Returns a full calculation, or `PENDING` when an input is unresolved.

Unknown documents, policies, rules, or balances return **explicit unresolved results** and never become assumptions. Diagnosis and procedures reported by the claimant are unverified until a document supports them. Only document-verified clinical facts go to `checkMedicalNecessity`.

### Sample data (`sample_data/`)

`claims.json`, `policies.json`, `documents.json`, `document_checklists.json`, `clinical_rules.json`, `benefit_balances.json`, `submission_deadlines.json` (claim submission rule sets, mapped to policies by `applies_to_policy_ids`; one rule set per policy)

Each policy has a `policyholder` (`policyholder_id`, `type` `INDIVIDUAL`|`ORGANIZATION`, `name`, `member_id`). The policyholder is whoever signed the contract, which can differ from the insured `members`. `member_id` is set only when the policyholder is also insured on that policy: APP is a self-insured individual, REJ a non-insured individual payer, RFI an employer group plan. `lookupPolicy` returns it and the report shows it in `metadata.policyholder`. It is informational only: it never affects a check or decision, and it is not sent to the LLM (`explanation_facts` excludes metadata). There is no person-to-policies index yet.

## Workflow

1. Load and validate the claim → 2. create the context → 3. verify each document and compare with the checklist → 4. look up the policy and check coverage on the treatment date → 5. check medical necessity (only when verified clinical evidence is sufficient, otherwise record `INSUFFICIENT_EVIDENCE` as a skipped step) → 6. calculate the benefit (only when inputs are established, otherwise `PENDING` as a skipped step) → 7. decision rules → 8. build the report, draft explanations with OpenRouter, validate → 9. submit for human review with final authorization `PENDING`.

Tool errors and skipped steps are recorded as explicit unresolved results in the audit trail.

## Decision guardrails (must hold)

- `APPROVE` requires all of the following: evidence is sufficient, coverage is established, medical necessity and reviews are resolved, the calculation is complete, payment is within the remaining limit, and citations are valid.
- `REJECT` requires a specific denial basis that evidence proves and an **applicable policy clause** supports. Route to human denial review. Never reject only because a document is missing. Never cite a generic exclusion without showing that it applies to the facts.
- `REQUEST_MORE_INFO` requires at least one open request: the item, why it is needed, who provides it, and the reassessment trigger.
- Some issues can't be resolved by an information request, such as a missing policy record or a required clinical review. Keep those pending review. Never force an approval or a rejection.
- A `null` diagnosis alone is **not** "no medical indication". Missing evidence gives `INSUFFICIENT_EVIDENCE`.
- Unresolved amounts are `null`, **never 0**.
- **Claim submission deadline (reimbursement claims):** within 60 days of the last treatment or discharge date for inpatient and outpatient claims, and 180 days from childbirth or completion of treatment for maternity. The terms live in their own data source, `sample_data/submission_deadlines.json` (rule set CSR-2026 v2026.1: `CSR-2.1` is 60 days for inpatient and outpatient, `CSR-2.2` is 180 days for maternity), not in the policy. `lookupPolicy` check `submission_deadline` looks up the policy's rule set, returns `rule_ids` on the check and the rule text in `PolicyResult.rules`, and compares `claim.submission_date` with `treatment_end` + N days, counting the deadline day itself as on time. Late gives `FAIL`, which leads to `REJECT` with denial review. If the claim is not a reimbursement claim (`claim_mode` ≠ `REIMBURSEMENT`) the check is `PASS` because the deadline doesn't apply. A missing `claim_mode`, or a claim type with no deadline, gives `UNCERTAIN` and escalation. A policy with no rule set also gives `UNCERTAIN`. Reports cite these rules as kind `RULE` (separate from `POLICY` clauses and `PROCEDURAL` checklist entries). The validator checks a `RULE` citation's text and version against the rule source, and accepts `POLICY` or `RULE` as the contractual basis for `REJECT`. For maternity, the anchor is `treatment_end` (completion of treatment or the childbirth/discharge date); there is no separate childbirth-date fact yet.
- Never invent a clause. If no applicable clause can be established, mark the point `UNVERIFIED` and route it for review.
- Document requirements cite the **checklist** as their procedural source.
- A document declared as a medical report that is actually an appointment confirmation stays visible as submitted with the mismatch shown. The required medical report stays `MISSING`.

## Report (six sections, plus metadata)

1. Document Review: per expected document, `COMPLETE | INCOMPLETE | MISSING`, submitted vs detected type, issues, evidence refs.
2. Policy Verification: active on the treatment date, member covered, claim type covered, waiting periods, exclusions, limits. Each is `PASS | FAIL | UNCERTAIN`.
3. Medical Necessity: diagnosis, treatment, result, rationale, clinical source, evidence, concerns.
4. Benefit Calculation: submitted, covered, excluded, deductible, copay, coinsurance, payable, member responsibility, remaining limit.
5. Recommendation: outcome, reasons (each linked to evidence **and** a citation), payment, requests or escalations, next action.
6. Policy Citations: exact clause text, document, version, clause ID, location.

Also include: claim IDs, assessment metadata (including the LLM model and config), audit reference, citation-validation status, and the human-review record. The full markdown template is in section 4 of the guideline.

## Validation (before a report is presented)

- Structure and allowed enum values are valid.
- Every material reason has evidence plus a citation. Citation IDs exist and match the policy version returned by `lookupPolicy`.
- `submitted = excluded + eligible`, `eligible = payable + member share`, and payable ≤ remaining limit.
- Every document finding refers to a submitted document or a checklist requirement that is explicitly missing.
- `REQUEST_MORE_INFO` has an open request. Final authorization stays `PENDING` until a human acts.

Audit trail: each tool call's input, output (or a secure reference), status, timestamp, tool version, and context version. Also skipped steps with reasons, and overrides (reviewer, decision, reason, time).

## Acceptance cases (must produce these results)

These are the verified outputs of the current code, checked by `tests/test_assessment.py::AcceptanceCasesTest`. Any change that alters them is a behavior change: update this section and the tests together, and only on purpose. Rendered reports are in `reports/<claim>.md` / `.json`, which `--out reports` regenerates.

| Case | Claim / Policy | Docs | Expected |
|---|---|---|---|
| Approval | `CLM-APP-001` / `POL-APP-001` v2026-A, outpatient, USD 200.00 | `A-D1`–`A-D4` | `APPROVE`: sinusitis `SUPPORTED`; USD 20.00 copay → USD 180.00 payable, USD 20.00 member, USD 620.00 remaining of USD 800.00 |
| Rejection | `CLM-REJ-001` / `POL-REJ-001` v2026-B, elective cosmetic rhinoplasty, USD 2,000.00 | `R-D1`–`R-D4` | `REJECT`: `NOT_SUPPORTED` (fixture explicitly establishes no medical indication); cosmetic exclusion; USD 0.00 payable, USD 2,000.00 member |
| More info | `CLM-RFI-001` / `POL-RFI-001` v2026-C, outpatient, USD 300.00 | `I-D1`–`I-D4` | `REQUEST_MORE_INFO`: `I-D4` is an appointment confirmation, medical report `MISSING`; medical step skipped (`INSUFFICIENT_EVIDENCE`); benefit `PENDING` with `null` amounts |

### Case details (current verified output)

**CLM-APP-001: APPROVE**
- Tool calls: `verifyDocument` ×4 (A-D1 to A-D4, all FOUND and COMPLETE), then `lookupPolicy`, `checkMedicalNecessity`, `calculateBenefit`, all OK. With `--llm`, the 8th event is `draftExplanations`.
- Document review: OP-REQ-1 to OP-REQ-4 `COMPLETE`; OP-REQ-5 (referral letter) `NOT_APPLICABLE`. Conclusion `COMPLETE`.
- Policy checks: all 7 `PASS` (clauses APP-2.1, APP-2.2, APP-3.1, APP-4.1, APP-6.1, APP-5.1, plus rule CSR-2.1 for the submission deadline). Submission deadline: submitted 2026-09-18, 3 days after treatment, within 60 days (deadline 2026-11-14). Conclusion `ELIGIBLE`.
- Medical: `SUPPORTED` by rule CR-001, evidence A-D4, policy clause APP-3.2.
- Benefit `COMPLETE`, applied in the order exclusions → deductible → copay → coinsurance → annual limit: submitted 200.00, excluded 0.00, eligible 200.00, deductible 0.00, copay 20.00, coinsurance 0.00, limit adjustment 0.00, **payable 180.00**, member 20.00, remaining 800.00 → 620.00. Clauses APP-5.2, APP-5.3, APP-5.1.
- Recommendation: 5 reasons (coverage, submitted on time, benefit, medical necessity, calculation), each with evidence and citations. Status `READY_FOR_AUTHORIZATION`. Owner: claims approver.

**CLM-REJ-001: REJECT**
- Tool calls: same 7 as approval, all OK.
- Document review: OP-REQ-1 to OP-REQ-4 `COMPLETE`. Conclusion `COMPLETE`.
- Policy checks: exclusions `FAIL` under REJ-6.4 (classification `COSMETIC_ELECTIVE` with `medical_indication_present: false`, from R-D4); the other 6 `PASS` (submission deadline: 7 days after treatment, within 60). Conclusion `INELIGIBLE`.
- Medical: `NOT_SUPPORTED` by rule CR-002 (diagnosis is an explicit `null` plus an explicit no-indication finding), policy clause REJ-3.2.
- Benefit `COMPLETE`: submitted 2000.00, **excluded 2000.00**, eligible 0.00, copay 0.00, **payable 0.00**, member 2000.00, remaining 1500.00 → 1500.00.
- Recommendation: reasons are exclusion failed (REJ-6.4), medical `NOT_SUPPORTED` (REJ-3.2), and the calculation. Status `READY_FOR_AUTHORIZATION`. Next action: human denial review. Owner: senior claims assessor.

**CLM-RFI-001: REQUEST_MORE_INFO**
- Tool calls: `verifyDocument` ×4 (I-D4 FOUND with detected type `APPOINTMENT_CONFIRMATION` and issue `TYPE_MISMATCH`), then `lookupPolicy` OK. Then **`SKIPPED_STEP` checkMedicalNecessity** (insufficient verified clinical evidence) and **`SKIPPED_STEP` calculateBenefit** (inputs unresolved).
- Document review: OP-REQ-1 to OP-REQ-3 `COMPLETE`; **OP-REQ-4 MEDICAL_REPORT `MISSING`** (issue: "Submitted I-D4 declared MEDICAL_REPORT but detected APPOINTMENT_CONFIRMATION", evidence I-D4). I-D4 also gets its own row with `required: N`. Conclusion `UNRESOLVED_ITEMS`.
- Policy checks: exclusions `UNCERTAIN` (no verified procedure classification); the other 6 `PASS` (submission deadline: 4 days after treatment, within 60). Conclusion `UNDETERMINED`.
- Medical: `INSUFFICIENT_EVIDENCE` (tool not called).
- Benefit `PENDING`: submitted 300.00; every computed amount is `null`.
- Information request `REQ-CLM-RFI-001-1`: MEDICAL_REPORT from the PROVIDER. Requirement OP-REQ-4 (CPM-2026 v1.2 §4.1), policy condition RFI-7.2, status `OPEN`. Reassess when a medical report is received and verified.
- Escalations listed as reservations: exclusions uncertain, medical insufficient, benefit pending. Status `PENDING_INFORMATION`. Recommended payable `null`. Owner: claims assessor.

All three cases: validation `PASS`, citation check `PASS`, final authorization `PENDING`.

### Failure-mode tests (must stay unresolved, never a forced decision)

| Scenario | Expected | Test |
|---|---|---|
| Policy record missing | Policy `UNRESOLVED`, benefit `PENDING`, outcome `None`, `ESCALATED` | `test_unknown_policy_is_escalated_not_decided` |
| Benefit balance missing | Limit `UNCERTAIN`, benefit `PENDING`, payable `null`, `ESCALATED` | `test_missing_balance_is_escalated` |
| Procedures match no clinical rule | `REFER_TO_MEDICAL_REVIEW`, `ESCALATED` | `test_unmatched_clinical_rule_is_referred` |
| `checkMedicalNecessity` raises | Audit `ERROR`, result `REFER_TO_MEDICAL_REVIEW`, `ESCALATED` | `test_tool_error_becomes_unresolved_result` |
| `verifyDocument` raises for the medical report | Requirement `MISSING`, `REQUEST_MORE_INFO` | `test_document_tool_error_leaves_requirement_missing` |
| Claim form member ID mismatch | Claim form `MISSING`, consistency issue recorded, never `APPROVE` | `test_identity_mismatch_is_not_accepted` |
| Waiting period not met | `REJECT` citing APP-4.1 | `test_waiting_period_failure_rejects_with_clause` |
| Reimbursement submitted after 60 days | `submission_deadline` `FAIL`, `REJECT` citing rule CSR-2.1 (`RULE` citation), validation `PASS` | `test_late_reimbursement_claim_rejects_with_deadline_clause` |
| Claim mode not stated | Deadline `UNCERTAIN`, `ESCALATED` | `test_missing_claim_mode_is_escalated` |
| Null diagnosis without an explicit no-indication finding | Never `REJECT` | `test_null_diagnosis_without_explicit_finding_never_rejects` |
| Malformed LLM reply (both attempts) | Explanations `FAILED`; recommendation and validation unchanged | `test_malformed_model_response_never_changes_decision` |
| Tampered citation text, version, ID or unknown clause | Validation `FAIL` | `tests/test_validator.py` |
| Amounts don't reconcile, or a pending amount is 0 instead of null | Validation `FAIL` | `tests/test_validator.py` |

## Implementation order

1. Fixture schemas and the three cases → 2. four tools and the context → 3. orchestrator, decision rules, report builder, validator → 4. OpenRouter explanations → 5. run the three scenarios → 6. failure tests → 7. compare OpenRouter models (quality, latency, cost) → 8. human-review mechanism.

Done when the three cases produce the expected recommendations, failures stay unresolved, and a reviewer can trace every material reason to evidence and policy terms.
