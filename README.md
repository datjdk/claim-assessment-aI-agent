# Claim Assessment AI Agent

A prototype agent that does the **first-pass assessment of a health insurance claim** in minutes instead of days. It checks the documents, the policy, medical necessity and the benefit amount, then writes an evidence-backed report recommending **Approve**, **Reject** or **Request more information**. A human assessor always makes the final decision.

- **Deterministic code decides.** The tools, decision rules, benefit calculation (`Decimal`, never float) and report are ordinary Python.
- **The LLM only explains.** On every run, a model on OpenRouter drafts reviewer-facing explanations from verified facts. The explanations are validated against the report and can never change the recommendation.
- **Every reason is traceable** to a document and a policy clause or rule, and every tool call is logged.

All policies, members, documents and amounts in `sample_data/` are **fictional**.

## How this was built

| Stage | Tool | Output | AI conversation |
|---|---|---|---|
| Planning | ChatGPT Astra | [Agent operating guideline](get-started/insurance_claim_assessment_agent_guideline.md): Defines how claims are assessed, which guardrails apply and what the report must contain.<br>[Implementation plan](get-started/claim_assessment_implementation_plan.md): Specifies the architecture, tools and decision logic, and sets the acceptance test cases. | • [Guideline conversation](ai-conversation/claim_assessment_conversation_export.md)<br>• [Plan conversation](ai-conversation/draft_implementation_plan_conversation_export.md) |
| Implementation | Claude Code (Claude Opus 5.5) | The code, fixtures, tests and docs in this repository, built from that plan. | • [Implementation conversation](ai-conversation/CONVERSATION.md) |
| LLM at runtime | [OpenRouter](https://openrouter.ai) | Reviewer-facing explanations only, called on every run; the model is set in `.env` | Not applicable |

## Requirements

- Python 3.9 or later. Standard library only, so there's nothing to install.
- An [OpenRouter](https://openrouter.ai) API key in `.env` (see below). Use `--no-llm` to run without one.

## How to run

Run every command from the project root.

```bash
# Assess one claim (readable terminal output, with OpenRouter explanations)
PYTHONPATH=src python3 -m claim_agent.cli CLM-APP-001

# Assess all three sample claims
PYTHONPATH=src python3 -m claim_agent.cli --all

# Markdown or JSON instead of terminal text
PYTHONPATH=src python3 -m claim_agent.cli CLM-RFI-001 --md
PYTHONPATH=src python3 -m claim_agent.cli CLM-RFI-001 --json

# Write <claim>.md and <claim>.json files into a folder
PYTHONPATH=src python3 -m claim_agent.cli --all --out output/md
```

| Option | Effect |
|---|---|
| `CLAIM_ID ...` / `--all` | Claims to assess (`CLM-APP-001`, `CLM-REJ-001`, `CLM-RFI-001`). |
| `--format text\|md\|json`, `--md`, `--json` | Output format. The default `text` fits the terminal width. |
| `--out DIR` | Also write `DIR/<claim>.md` and `DIR/<claim>.json` (full audit trail). |
| `--no-color` | Plain text, with no ANSI colors. Color is also off when output isn't a terminal or `NO_COLOR` is set. |
| `--no-llm` | Skip the OpenRouter explanations, for offline runs and tests. By default every run calls OpenRouter and needs an API key. |
| `--no-llm-payload` | Hide the full LLM request/response section. |
| `--llm-raw` | Add the exact raw request and response JSON bodies to the tool call log. |
| `--env-file PATH` | Read settings from this file instead of `./.env`. |

### LLM explanations

Every run calls OpenRouter to draft the explanations. Before the first run, copy `.env.example` to `.env` (it's gitignored) and set your key:

```bash
cp .env.example .env
chmod 600 .env
# edit .env: OPENROUTER_API_KEY=...
PYTHONPATH=src python3 -m claim_agent.cli --all --out output/md
```

| Setting | Default | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | none | Required unless you pass `--no-llm`. The run stops with an error if it's missing. Never logged or written to a report. There is deliberately no `--api-key` flag. |
| `OPENROUTER_MODEL` | `openai/gpt-4o` | The sample runs below used `recursive/flint-v1.0:free`. |
| `OPENROUTER_MAX_TOKENS` | `1000` | Reasoning models need more; Flint needs about `4000`. |
| `OPENROUTER_REASONING_EFFORT` | unset | `minimal`, `low`, `medium` or `high`. |

Variables already exported in your shell take precedence over `.env`. Rate limits (HTTP 429), 5xx errors and timeouts are retried with backoff (2s, then 4s, or the server's `Retry-After`). Other 4xx errors are not retried. If drafting fails, the report still has its recommendation; the explanations are just marked `Failed`.

> Free models may log prompts. Send only fictional data.

### Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## How an assessment works

```
verifyDocument × n → documentReview → lookupPolicy → checkMedicalNecessity → calculateBenefit
  → decide → (draftExplanations via OpenRouter) → validateReport → human review (Pending)
```

1. **Documents.** `verifyDocument` checks each submitted document. The review then compares the results with the claim-type checklist and cross-checks identity, amounts and dates. Only facts from verified documents are used later.
2. **Policy.** `lookupPolicy` runs seven checks: policy active, member covered, benefit covered, waiting period, submission deadline, exclusions and remaining limit. Each check is Pass, Fail or Uncertain, and each cites its clause.
3. **Medical necessity.** This step runs only when a verified medical report exists. Otherwise it's skipped as *Insufficient evidence*, and the log names the reason.
4. **Benefit.** The calculation applies exclusions, then the deductible, copay, coinsurance and annual limit. If an input is unresolved, the step is *Pending* and amounts are `null` (never 0).
5. **Decision rules,** in this order: Reject (with a proven basis and an applicable clause) → Request more information → Escalate → Approve.
6. **Report and validation.** The report has six sections and is validated (citations, amount reconciliation, guardrails) before it's shown. Final authorization is always **Pending** until a human acts.

## The three test cases

| Case | Claim | Policy | Amount | Recommendation | Payable |
|---|---|---|---|---|---|
| Approval | `CLM-APP-001` sinusitis, outpatient | `POL-APP-001` v2026-A | USD 200.00 | **Approve** | **180.00** |
| Rejection | `CLM-REJ-001` elective cosmetic rhinoplasty | `POL-REJ-001` v2026-B | USD 2,000.00 | **Reject** | **0.00** |
| More info | `CLM-RFI-001` back pain, outpatient | `POL-RFI-001` v2026-C | USD 300.00 | **Request more information** | **Pending** (`null`) |

All three pass validation and the citation check. Full reports, generated with `--out output/md` using `recursive/flint-v1.0:free`, are in [output/md/](output/md/):

- [CLM-APP-001.md](output/md/CLM-APP-001.md)
- [CLM-REJ-001.md](output/md/CLM-REJ-001.md)
- [CLM-RFI-001.md](output/md/CLM-RFI-001.md)

The outputs below are excerpts. Times, assessment IDs and audit IDs change on every run.

### Case 1: Approval (`CLM-APP-001`)

All four required documents are complete, all seven policy checks pass, and medical necessity is supported. The calculation is the USD 200.00 claim minus a USD 20.00 copay.

**Agent output** (`PYTHONPATH=src python3 -m claim_agent.cli CLM-APP-001 --no-color`):

```
CLAIM ASSESSMENT  CLM-APP-001   fictional data · recommendation only
  Recommendation  Approve
  Payable         180.00 USD
  Status          Ready for authorization   authorization Pending
  Next action     Send to an authorized approver to authorize payment of USD 180.00. (Claims
                  approver)

1. Document review (Complete)
  ✓ OP-REQ-1  Complete        CLAIM_FORM               A-D1
  ✓ OP-REQ-2  Complete        ITEMIZED_INVOICE         A-D2
  ✓ OP-REQ-3  Complete        PAYMENT_RECEIPT          A-D3
  ✓ OP-REQ-4  Complete        MEDICAL_REPORT           A-D4
  – OP-REQ-5  Not applicable  REFERRAL_LETTER          Condition fact 'specialist_referral_required'
                              not documented; requirement not triggered.

2. Policy verification (Eligible)
  ✓ Pass       Policy active on treatment date  ... [APP-2.1]
  ✓ Pass       Member covered                   ... [APP-2.2]
  ✓ Pass       Claim type / benefit covered     OUTPATIENT benefit included. [APP-3.1]
  ✓ Pass       Waiting period                   ... [APP-4.1]
  ✓ Pass       Claim submitted within deadline  Submitted 2026-09-18, 3 days after last treatment
                                                2026-09-15; OUTPATIENT deadline 60 days
                                                (2026-11-14). [CSR-2.1]
  ✓ Pass       Exclusions                       Verified procedure classification MEDICAL matches no
                                                exclusion. [APP-6.1]
  ✓ Pass       Remaining benefit limit          Remaining OUTPATIENT limit USD 800.00 of 1000.00 as
                                                of 2026-09-17. [APP-5.1]

3. Medical necessity (Supported)
    Rule          CR-001 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 2.3
    Rationale     Outpatient consultation and prescribed treatment are an appropriate response to
                  documented acute bacterial sinusitis.
    Evidence      A-D4 p.1, Assessment; A-D4 p.1, Plan; A-D4 p.1, Assessment
    Policy clause APP-3.2

4. Benefit calculation (Complete)  USD
    Submitted                   200.00
    Excluded                      0.00
    Eligible                    200.00
    Deductible                    0.00
    Copay                        20.00
    Coinsurance                   0.00
    Limit adjust                  0.00
    Insurer payable             180.00
    Member responsibility        20.00
    Remaining limit             800.00 -> 620.00
    Clauses               APP-5.2, APP-5.3, APP-5.1

5. Recommendation (Approve)
  1. Coverage established ... [cites PC-06, PC-07]
  2. Submitted on time ... [cites PC-10]
  3. Benefit applies ... [cites PC-08, PC-09, PC-11]
  4. Medical necessity SUPPORTED (CR-001) ... [cites PC-13]
  5. Calculation: USD 200.00 submitted, 0.00 excluded, 180.00 insurer payable, 20.00 member
     responsibility; remaining limit 800.00 -> 620.00. [cites PC-14, PC-15, PC-12]

Validation  Pass   citations Pass   reconciliation Pass
```

**LLM note on the recommendation** (validated against the report facts):

> Recommendation outcome APPROVE, recommended payable USD 180.00; next action send to an authorized approver to authorize payment of USD 180.00.

**Tool call log** (from [output/md/CLM-APP-001.md](output/md/CLM-APP-001.md)):

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

### Case 2: Rejection (`CLM-REJ-001`)

The medical report (R-D4) records an elective cosmetic rhinoplasty and explicitly states there is no medical indication. Cosmetic exclusion REJ-6.4 applies, so the whole amount is excluded. The claim goes to human denial review.

**Agent output** (`PYTHONPATH=src python3 -m claim_agent.cli CLM-REJ-001 --no-color`):

```
CLAIM ASSESSMENT  CLM-REJ-001   fictional data · recommendation only
  Recommendation  Reject
  Payable         0.00 USD
  Status          Ready for authorization   authorization Pending
  Next action     Route to human denial review; the denial notice must cite the clauses above.
                  (Senior claims assessor (denial review))

1. Document review (Complete)
  ✓ OP-REQ-1 to OP-REQ-4  Complete   R-D1 to R-D4

2. Policy verification (Not eligible)
  ✓ Pass       (6 checks: active, member, benefit, waiting period, deadline 7 days of 60, limit)
  ✗ Fail       Exclusions                       Verified procedure classification COSMETIC_ELECTIVE
                                                with no documented medical indication. [REJ-6.4]

3. Medical necessity (Not supported)
    Rule          CR-002 — Fictional Clinical Necessity Rulebook CNR-2026 v1.0 CNR-2026 Section 7.1
    Rationale     The treating practitioner documents an elective cosmetic procedure and explicitly
                  records no medical indication or functional impairment.
    Policy clause REJ-3.2

4. Benefit calculation (Complete)  USD
    Submitted                  2000.00
    Excluded                   2000.00
    Eligible                      0.00
    Insurer payable               0.00
    Member responsibility      2000.00
    Remaining limit            1500.00 -> 1500.00
    Clauses               REJ-6.4, REJ-5.2, REJ-5.1

5. Recommendation (Reject)
  1. Exclusions failed: Verified procedure classification COSMETIC_ELECTIVE with no
     documented medical indication. [evidence R-D4; cites PC-11]
  2. Medical necessity NOT_SUPPORTED (CR-002) ... [evidence R-D4, clinical_rule:CR-002; cites PC-13]
  3. Calculation: USD 2000.00 submitted, 2000.00 excluded, 0.00 insurer payable, 2000.00
     member responsibility; remaining limit 1500.00 -> 1500.00. [cites PC-11, PC-14, PC-12]

6. Citations (Pass)
    PC-11 REJ-6.4   Page 9, Section 6.4
                    “We will not pay for any cosmetic or aesthetic procedure, including rhinoplasty,
                    performed to change appearance where there is no medical indication documented
                    by the treating practitioner. ...”

Validation  Pass   citations Pass   reconciliation Pass
```

**LLM note on the recommendation:**

> Recommendation outcome was REJECT with recommended payable USD 0.00; reasons included exclusions failed under REJ-6.4, medical necessity NOT_SUPPORTED under CR-002, and calculation showing USD 2000.00 submitted and excluded, USD 0.00 insurer payable, USD 2000.00 member responsibility, and remaining limit USD 1500.00.

**Tool call log** (from [output/md/CLM-REJ-001.md](output/md/CLM-REJ-001.md)):

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

### Case 3: Request more information (`CLM-RFI-001`)

Document I-D4 was submitted as a medical report but is actually an appointment confirmation, so the required medical report is **Missing**. Without it, medical necessity and the benefit can't be assessed. Both steps are skipped with a named reason, all amounts stay `null`, and the agent opens an information request to the provider.

**Agent output** (`PYTHONPATH=src python3 -m claim_agent.cli CLM-RFI-001 --no-color`):

```
CLAIM ASSESSMENT  CLM-RFI-001   fictional data · recommendation only
  Recommendation  Request more information
  Payable         PENDING
  Status          Waiting for information   authorization Pending
  Next action     Send the information requests; hold the claim as PENDING_INFORMATION and reassess
                  on receipt. (Claims assessor)

  Diagnosis     Not verified (reported: Acute lower back pain)
  Procedures    Not verified (reported: Outpatient consultation, Physiotherapy session)

1. Document review (Unresolved items)
  ✓ OP-REQ-1  Complete        CLAIM_FORM               I-D1
  ✓ OP-REQ-2  Complete        ITEMIZED_INVOICE         I-D2
  ✓ OP-REQ-3  Complete        PAYMENT_RECEIPT          I-D3
  ✗ OP-REQ-4  Missing         MEDICAL_REPORT           Submitted I-D4 declared MEDICAL_REPORT but
                              detected APPOINTMENT_CONFIRMATION.
  – OP-REQ-5  Not applicable  REFERRAL_LETTER          ...
  ✓ extra     Complete        APPOINTMENT_CONFIRMATION I-D4 submitted as MEDICAL_REPORT — ...

2. Policy verification (Not yet determined)
  ✓ Pass       (6 checks: active, member, benefit, waiting period, deadline 4 days of 60, limit)
  ? Uncertain  Exclusions                       No verified procedure classification; exclusions
                                                cannot be assessed. [no clause]

3. Medical necessity (Insufficient evidence)
    Evidence      none
    Policy clause RFI-3.2
    Concern       No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).

4. Benefit calculation (Pending)  USD
    Submitted                   300.00
    Excluded ... Member responsibility   PENDING
    Remaining limit            PENDING -> PENDING
    Pending because       Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity
                          INSUFFICIENT_EVIDENCE.

5. Recommendation (Request more information)
  1.        MEDICAL_REPORT needed: Required MEDICAL_REPORT is missing. [evidence I-D4; cites PC-12,
            PC-04]
  request   MEDICAL_REPORT from PROVIDER (REQ-CLM-RFI-001-1, OPEN). Requirement OP-REQ-4; policy
            condition RFI-7.2. Reassess when a MEDICAL_REPORT for CLM-RFI-001 is received and
            verified.
  note      Exclusions uncertain: No verified procedure classification; exclusions cannot be
            assessed.
  note      Medical necessity INSUFFICIENT_EVIDENCE: No verified MEDICAL_REPORT ...
  note      Benefit calculation PENDING: Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; ...

Validation  Pass   citations Pass   reconciliation Not applicable
```

**LLM note on the recommendation:**

> Recommendation REQUEST_MORE_INFO; hold claim as PENDING_INFORMATION and reassess on receipt once MEDICAL_REPORT is received and verified. Information request REQ-CLM-RFI-001-1 open for MEDICAL_REPORT under OP-REQ-4, RFI-7.2; exclusions uncertain; medical necessity INSUFFICIENT_EVIDENCE; benefit calculation PENDING.

**Tool call log** (from [output/md/CLM-RFI-001.md](output/md/CLM-RFI-001.md)). The free model was rate-limited on the first call (HTTP 429), and the automatic retry succeeded:

```
 1 11:35:14 OK      verifyDocument(I-D1) -> FOUND CLAIM_FORM COMPLETE
 2 11:35:14 OK      verifyDocument(I-D2) -> FOUND ITEMIZED_INVOICE COMPLETE
 3 11:35:14 OK      verifyDocument(I-D3) -> FOUND PAYMENT_RECEIPT COMPLETE
 4 11:35:14 OK      verifyDocument(I-D4) -> FOUND APPOINTMENT_CONFIRMATION COMPLETE issues=TYPE_MISMATCH
 5 11:35:14 OK      documentReview(CHK-OUTPATIENT v1.2) -> UNRESOLVED_ITEMS: 3/4 COMPLETE; OP-REQ-4 MEDICAL_REPORT MISSING
 6 11:35:14 OK      lookupPolicy(POL-RFI-001) -> FOUND v2026-C 6/7 PASS exclusions=UNCERTAIN remaining=1200.00
 7 11:35:14 SKIPPED checkMedicalNecessity -> No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).
 8 11:35:14 SKIPPED calculateBenefit -> Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.
 9 11:35:14 OK      decide() -> REQUEST_MORE_INFO payable=null requests=REQ-CLM-RFI-001-1 escalations=3
10 11:35:15 ERROR   openrouter.chat(attempt 1) -> error: OpenRouter returned HTTP 429: {"error":{"message":"Provider returned error","code":429, … "recursive/flint-v1.0:free is temporarily rate-limited upstream. …"}}
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (13513 chars): {"claim_id":"CLM-RFI-001","currency":"USD","document_review":{"checklis…
11 11:35:33 OK      openrouter.chat(attempt 2) -> validation=PASS tokens=3448/2094 recursive/flint-v1.0:free id=gen-1793187318-yVPOm0ZnuZuZKi0G6R5X
   ↳ request system (603 chars): You draft explanations for a human insurance claim assessor. Rules: - U…
   ↳ request user (13513 chars): {"claim_id":"CLM-RFI-001","currency":"USD","document_review":{"checklis…
   ↳ response (1284 chars): { "document_review": "Checklist conclusion UNRESOLVED_ITEMS; required M…
12 11:35:33 OK      draftExplanations(recursive/flint-v1.0:free) -> DRAFTED attempts=2 served=recursive/flint-v1.0:free tokens=3448/2094
13 11:35:33 OK      validateReport() -> PASS citations=PASS reconciliation=NOT_APPLICABLE final_status=PENDING_INFORMATION
```

### Reading the tool call log

Each line is `seq time STATUS tool(args) -> result`.

| Status | Meaning |
|---|---|
| `OK` | The tool or step ran and returned a result. |
| `SKIPPED` | A prerequisite was missing. The reason names the missing requirement or blocker. |
| `ERROR` | The call failed. Tool errors become unresolved results, never assumptions. |

The `↳` lines under each `openrouter.chat` call show short previews of the request messages and the response. With `--no-llm`, the log ends at `decide()` and `validateReport()`, and the explanations show as *Not requested*. The full input and output of every call is in the JSON audit trail (`--json`, or `<claim>.json` written by `--out`).

## Project layout

```
sample_data/            fictional claims, policies, documents, checklists, clinical rules, balances,
                        submission deadline rules
src/claim_agent/
  cli.py                command-line entry point
  context.py            intake validation, assessment context (verified facts only)
  tools/                verifyDocument, lookupPolicy, checkMedicalNecessity, calculateBenefit
  document_review.py    checklist comparison, cross-checks, information requests
  orchestrator.py       runs the workflow and records the audit trail
  decision.py           decision rules and guardrails
  report.py             six-section report and citations
  llm.py                OpenRouter client (explanations only)
  validator.py          report validation
  human_review.py       authorize / override with reviewer, reason and time
  render.py, labels.py  terminal and Markdown output
tests/                  unit and acceptance tests
get-started/            implementation plan and operating guideline (planning docs)
ai-conversation/        exported ChatGPT planning and Claude Code implementation conversations
```

See [CLAUDE.md](CLAUDE.md) for design decisions and the full list of verified case outputs and failure-mode tests.
