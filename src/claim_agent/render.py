"""Render a report and its audit trail: Markdown (guideline template, for files) or plain text (for terminals)."""

from __future__ import annotations

import json
import textwrap
from typing import Any, Dict, Iterable, List

from claim_agent.audit import AuditTrail
from claim_agent.labels import label


def _cell(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, (list, tuple)):
        return "; ".join(_cell(v) for v in value) or "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: List[str], rows: Iterable[Iterable[Any]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return lines


def _amount(value: Any) -> str:
    return "PENDING" if value is None else str(value)


def _explanation(report: Dict[str, Any], section: str) -> List[str]:
    text = report["explanations"]["sections"].get(section)
    return [f"> **Assessor note (LLM draft, validated against report facts):** {text}", ""] if text else []


def _policyholder(holder: Any) -> str:
    if not holder:
        return "NOT RECORDED"
    insured = f", insured as {holder['member_id']}" if holder.get("member_id") else ", not an insured member"
    return f"{holder['name']} ({holder['type']}, {holder['policyholder_id']}{insured})"


def section_results(report: Dict[str, Any]) -> Dict[int, str]:
    """The result code shown (as a label) next to each section heading, e.g. "1. Document Review (Unresolved items)"."""
    return {
        1: report["document_review"]["conclusion"],
        2: report["policy_verification"]["conclusion"],
        3: report["medical_necessity"]["result"],
        4: report["benefit_calculation"]["status"],
        5: report["recommendation"]["outcome"] or "PENDING_REVIEW",
        6: report["validation"]["citation_check"],
    }


def render_report(report: Dict[str, Any]) -> str:
    results = {n: label(code) for n, code in section_results(report).items()}
    m = report["metadata"]
    dr, pv, mn, bc, rec = (report[k] for k in ("document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation"))
    dx, px = m["verified_diagnosis"], m["verified_procedures"]
    v, hr = report["validation"], report["human_review"]
    out = [
        f"# Claim Assessment Report — {m['claim_id']}",
        f"_{report['notice']}_",
        "",
        f"- Claim ID: {m['claim_id']}",
        f"- Assessment ID: {m['assessment_id']}",
        f"- Assessor: {m['assessor']}",
        f"- Assessment Date: {m['assessment_date']}",
        f"- Policy ID / Version: {m['policy_id']} / {_cell(m['policy_version'])}",
        f"- Policyholder: {_policyholder(m['policyholder'])}",
        f"- Claim Type: {m['claim_type']}",
        f"- Patient / Member: {m['member_id']}",
        f"- Treatment / Event Dates: {m['treatment_dates']['start']} to {m['treatment_dates']['end']}",
        f"- Diagnosis / Treatment (verified): {_cell(dx['value']) if dx['verified'] else 'Not verified'} / "
        f"{_cell(px['value']) if px['verified'] else 'Not verified'}",
        f"- Diagnosis / Treatment (claimant-reported): {_cell(m['reported_diagnosis'])} / {_cell(m['reported_procedures'])}",
        f"- Submitted Amount / Currency: {m['submitted_amount']} {m['currency']}",
        f"- Audit reference: {report['audit_reference']}",
        "",
        f"## 1. Document Review ({results[1]})",
        *_table(
            ["Requirement", "Document ID", "Document Type", "Required", "Status", "Submitted / Detected", "Verification", "Issues", "Evidence", "Citation"],
            ([r["requirement_id"], r["document_id"], r["document_type"], {"Y": "Yes", "N": "No"}.get(r["required"], "Conditional"), label(r["status"]),
              f"{_cell(r['submitted_type'])} / {_cell(r['detected_type'])}", label(r["verification"]), r["issues"], r["evidence"], r["citation_ids"]]
             for r in dr["rows"]),
        ),
        "",
        f"Document-review conclusion: **{label(dr['conclusion'])}**",
        "Outstanding requests: " + ("; ".join(
            f"{q['request_id']}: {q['required_item']} from {q['request_to']} — {q['why_needed']}" for q in dr["outstanding_requests"]
        ) or "None"),
        "",
        *_explanation(report, "document_review"),
        f"## 2. Policy Verification ({results[2]})",
    ]
    if pv["status"] != "FOUND":
        out += [f"Policy record unresolved: {pv['reason']}", ""]
    out += [
        *_table(
            ["Check", "Result", "Verified Fact", "Policy Clause", "Citation", "Evidence"],
            ([c["label"], label(c["result"]), c["verified_fact"], c["clause_ids"] + c["rule_ids"], c["citation_ids"], c["evidence"]] for c in pv["checks"]),
        ),
        "",
        f"Policy-verification conclusion: **{label(pv['conclusion'])}**",
        "",
        *_explanation(report, "policy_verification"),
        f"## 3. Medical Necessity ({results[3]})",
        f"- Diagnosis: {_cell(mn['diagnosis']) if mn['diagnosis'] or mn['rule_id'] else 'Not verified'}",
        f"- Treatment / procedure: {_cell(mn['procedures'])}",
        f"- Clinical rationale: {_cell(mn['rationale'])}",
        f"- Policy medical-necessity clause: {_cell(mn['policy_clause_ids'])} ({_cell(mn['citation_ids'])})",
        f"- Clinical rule reference: {_cell(mn['rule_id'])} — {_cell(mn['clinical_source'])}",
        f"- Supporting evidence: {_cell([e['document_id'] + ' ' + e['location'] for e in mn['evidence']])}",
        f"- Result: **{label(mn['result'])}**",
        f"- Outstanding concerns: {_cell(mn['outstanding_concerns']) if mn['outstanding_concerns'] else 'None'}",
        "",
        *_explanation(report, "medical_necessity"),
        f"## 4. Benefit Calculation ({results[4]})",
        f"Status: **{label(bc['status'])}** ({bc['currency']})",
        "",
        *_table(
            ["Component", "Amount", "Evidence / Policy Clause"],
            [
                ["Submitted amount", _amount(bc["submitted"]), bc["evidence"][:1]],
                ["Excluded amount", _amount(bc["excluded"]), bc["clause_ids"]],
                ["Eligible / covered amount", _amount(bc["eligible"]), "Calculation"],
                ["Deductible", _amount(bc["deductible"]), "Policy cost-sharing clause"],
                ["Copay", _amount(bc["copay"]), "Policy cost-sharing clause"],
                ["Coinsurance", _amount(bc["coinsurance"]), "Policy cost-sharing clause"],
                ["Limit adjustment", _amount(bc["limit_adjustment"]), "Annual limit clause / ledger"],
                ["**Insurer payable**", f"**{_amount(bc['insurer_payable'])}**", "Calculation"],
                ["**Member responsibility**", f"**{_amount(bc['member_responsibility'])}**", "Calculation"],
                ["Remaining limit before → after", f"{_amount(bc['remaining_limit_before'])} → {_amount(bc['remaining_limit_after'])}", "Benefit ledger"],
            ],
        ),
        "",
        "- Calculation order: " + (" → ".join(f"{s['step']} ({s['amount']})" for s in bc["steps"]) or "not run"),
        f"- Clauses applied: {_cell(bc['clause_ids'])} ({_cell(bc['citation_ids'])})",
        f"- Reconciliation: {label(v['reconciliation'])}",
    ]
    if bc["pending_reasons"]:
        out.append(f"- Pending because: {_cell(bc['pending_reasons'])}")
    out += [
        "",
        *_explanation(report, "benefit_calculation"),
        f"## 5. Recommendation ({results[5]})",
        f"- Recommendation: **{label(rec['outcome'] or 'PENDING_REVIEW')}**",
        f"- Recommended payable amount: {_amount(rec['recommended_payable'])}",
        "- Specific reasons:",
        *[f"  {i}. {r['finding']} — Evidence: {_cell(r['evidence'])}; Citations: {_cell(r['citation_ids'])}" for i, r in enumerate(rec["reasons"], 1)],
    ]
    for q in rec["information_requests"]:
        out.append(
            f"- Information request {q['request_id']}: {q['required_item']} from {q['request_to']}. Why: {q['why_needed']} "
            f"Requirement: {q['requirement_id']} ({q['checklist_source']}); policy condition: {_cell(q['policy_clause_id'])}. "
            f"Reassessment trigger: {q['reassessment_trigger']}"
        )
    out += [
        f"- Escalations or reservations: {_cell(rec['escalations']) if rec['escalations'] else 'None'}",
        f"- Next action / authorization owner: {rec['next_action']} — {rec['authorization_owner']}",
        "",
        *_explanation(report, "recommendation"),
        f"## 6. Policy Citations ({results[6]})",
        *_table(
            ["Citation", "Kind", "Source Document", "Version / Effective", "Clause / Location", "Relevant Wording", "Supported Finding", "Evidence"],
            ([c["citation_id"], c["kind"].capitalize(), c["source_document"], f"{_cell(c['version'])} / {_cell(c['effective_date'])}",
              f"{c['clause_id']} — {_cell(c['location'])}", c["text"], c["supported_findings"], c["evidence_ids"]]
             for c in report["policy_citations"]["citations"]),
        ),
        "",
        f"- Citation coverage check: {label(v['citation_check'])}",
        f"- Report validation: {label(v['status'])}" + (f" — {_cell(v['errors'])}" if v["errors"] else ""),
        f"- Explanations: {label(report['explanations']['status'])}"
        + (f" (model {report['explanations']['llm']['served_model']})" if report["explanations"].get("llm", {}).get("served_model") else ""),
        "",
        f"Assessment Status: **{label(report['assessment_status'])}**",
        f"Final Authorization Status: **{label(hr['authorization_status'])}**",
    ]
    if hr["reviewer"]:
        out.append(
            f"Human review: {label(hr['decision'])} by {hr['reviewer']} at {hr['reviewed_at']} — final {label(hr['final_outcome'])}. "
            f"Reason: {_cell(hr['reason'])}"
        )
    return "\n".join(out) + "\n"


CHECK_SHORT = {
    "policy_active": "active", "member_covered": "member", "benefit_covered": "benefit", "waiting_period": "waiting",
    "submission_deadline": "deadline", "exclusions": "exclusions", "limit": "limit",
}


def _flat(value: Any, sep: str = ",") -> str:
    if isinstance(value, (list, tuple)):
        return sep.join(_flat(v) for v in value) or "[]"
    return "null" if value is None else str(value).replace("\n", " ")


def _arg(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_arg(v) for v in value) + "]"
    if value is None:
        return "null"
    text = str(value)
    return json.dumps(text) if " " in text else text


def _call_args(e) -> str:
    data = e.input or {}
    if e.event == "LLM_CALL":
        return str(data.get("config", {}).get("model"))
    if e.event == "HUMAN_REVIEW":
        return str(data.get("reviewer"))
    if e.event == "LLM_REQUEST":
        return f"attempt {data.get('attempt')}"
    if e.event == "SKIPPED_STEP":
        return ""
    if e.event == "STEP":
        return ", ".join(str(v) for v in data.values())
    return ", ".join(_arg(v) for v in data.values())


def _summarize_output(e) -> str:
    out = e.output
    if e.status == "SKIPPED":
        return str(e.reason)
    if e.status == "ERROR" and e.event == "TOOL_CALL":
        return f"error: {e.reason}"
    if e.event == "HUMAN_REVIEW":
        return f"final={(e.input or {}).get('final_outcome')}" + (f": {e.reason}" if e.reason else "")
    if e.event == "LLM_REQUEST":
        if e.status == "ERROR":
            return f"error: {e.reason}"
        n = len(out.get("validation_problems") or [])
        verdict = "PASS" if not n else f"FAIL ({n} problem{'s' if n > 1 else ''})"
        return f"validation={verdict} tokens={out.get('tokens_in')}/{out.get('tokens_out')} {out.get('served_model')} id={out.get('response_id')}"
    if not isinstance(out, dict):
        return _flat(out)
    if e.name == "documentReview":
        rows = [r for r in out["rows"] if r["required"] != "N" and r["status"] != "NOT_APPLICABLE"]
        complete = sum(1 for r in rows if r["status"] == "COMPLETE")
        gaps = [f"{r['requirement_id']} {r['document_type']} {r['status']}" for r in rows if r["status"] != "COMPLETE"]
        text = f"{out['conclusion']}: {complete}/{len(rows)} COMPLETE" + "".join(f"; {g}" for g in gaps)
        if out["consistency_issues"]:
            text += f"; {len(out['consistency_issues'])} consistency issue(s)"
        return text
    if e.name == "decide":
        payable = out["recommended_payable"] if out["recommended_payable"] is not None else "null"
        text = f"{out['outcome'] or 'PENDING_REVIEW'} payable={payable}"
        if out["information_requests"]:
            text += " requests=" + ",".join(out["information_requests"])
        return text + (f" escalations={out['escalations']}" if out["escalations"] else "")
    if e.name == "validateReport":
        text = f"{out['status']} citations={out['citation_check']} reconciliation={out['reconciliation']} final_status={out['assessment_status']}"
        return text + (f" errors={len(out['errors'])}" if out["errors"] else "")
    if e.event == "LLM_CALL":
        last = (out.get("exchanges") or [{}])[-1]
        usage = last.get("usage") or {}
        tokens = f" tokens={usage.get('prompt_tokens')}/{usage.get('completion_tokens')}" if usage else ""
        served = f" served={out['served_model']}" if out.get("served_model") else ""
        return f"{out['status']} attempts={out['attempts']}{served}{tokens}"
    if e.name == "verifyDocument":
        if out["status"] != "FOUND":
            return f"UNRESOLVED: {out['reason']}"
        issues = [i["code"] for i in out.get("issues", [])]
        return f"FOUND {out['detected_type']} {out['completeness_status']}" + (f" issues={_flat(issues)}" if issues else "")
    if e.name == "lookupPolicy":
        if out["status"] != "FOUND":
            return f"UNRESOLVED: {out['reason']}"
        passed = sum(1 for v in out["checks"].values() if v["result"] == "PASS")
        others = " ".join(f"{CHECK_SHORT.get(k, k)}={v['result']}" for k, v in out["checks"].items() if v["result"] != "PASS")
        return f"FOUND v{out['version']} {passed}/{len(out['checks'])} PASS" + (f" {others}" if others else "") + f" remaining={out['remaining_limit']}"
    if e.name == "checkMedicalNecessity":
        return f"{out['result']} rule={out['rule_id']}" if out["rule_id"] else f"{out['result']}: {out['reason']}"
    if e.name == "calculateBenefit":
        if out["status"] != "COMPLETE":
            return f"PENDING: {'; '.join(out['pending_reasons'])}"
        return f"payable={out['insurer_payable']} member={out['member_responsibility']} remaining={out['remaining_limit_after']}"
    return json.dumps(out)


def audit_lines(audit: AuditTrail, max_width: int = 0, show_time: bool = True, show_llm_raw: bool = False) -> List[str]:
    """One line per audit event: `seq [time] STATUS tool(args) -> result`.

    With max_width > 0, an over-long line first has its arguments shortened, then is cut with an ellipsis;
    the full input and output stay in the JSON audit trail. With show_llm_raw, each LLM call line is followed by
    the raw request body (exactly as sent; the API key is only in the HTTP header) and each raw response body,
    one line each and never truncated.
    """
    lines = []
    for e in audit.events:
        time = (e.timestamp[11:19] + " ") if show_time and len(e.timestamp) >= 19 else ""
        args = _call_args(e)
        result = _summarize_output(e)

        def build(a: str) -> str:
            call = f"{e.name}({a})" if e.event != "SKIPPED_STEP" else e.name
            return f"{e.sequence:>2} {time}{e.status:<7} {call} -> {result}"

        line = build(args)
        # Shorten arguments at whole-argument boundaries so no value is shown cut in half.
        parts = args.split(", ") if args else []
        while max_width and len(line) > max_width and len(parts) > 1:
            parts.pop()
            line = build(", ".join(parts) + ", …")
        if max_width and len(line) > max_width:
            line = line[: max_width - 1] + "…"
        lines.append(line)
        if e.event == "LLM_REQUEST":
            details = [f"   ↳ request {m['role']} ({m['chars']} chars): {m['text']}" for m in (e.input or {}).get("request_preview") or []]
            reply = (e.output or {}).get("response_preview")
            if reply:
                details.append(f"   ↳ response ({reply['chars']} chars): {reply['text']}")
            lines += [d[: max_width - 1] + "…" if max_width and len(d) > max_width else d for d in details]
        if show_llm_raw and e.event == "LLM_CALL":
            lines += _llm_raw_lines(e)
    return lines


def _llm_raw_lines(e) -> List[str]:
    data, result = e.input or {}, e.output or {}
    lines = [f"   ↳ request body (POST {data.get('url')}): " + json.dumps(data.get("request_body") or {})]
    for x in result.get("exchanges", []):
        raw = x.get("response_raw") or (json.dumps(x["response_body"]) if x.get("response_body") else None)
        lines.append(f"   ↳ response body (attempt {x['attempt']}): " + (_one_line(raw) if raw else f"ERROR {x.get('error')}"))
    return lines


def _one_line(raw: str) -> str:
    # OpenRouter pads responses with keep-alive whitespace before the JSON. Trim it and escape any inner newline so
    # the body stays on one log line; the exact text is kept in the audit trail (exchanges[].response_raw).
    return raw.strip().replace("\r", "\\r").replace("\n", "\\n")


def llm_payload_lines(audit: AuditTrail, markdown: bool = False) -> List[str]:
    """Full OpenRouter request and response messages for each LLM call in the audit trail.

    The request body is shown exactly as sent; the Authorization header (API key) is never stored, so never shown.
    """
    out: List[str] = []

    def head(text: str) -> str:
        return f"**{text}**" if markdown else text

    for e in audit.events:
        if e.event != "LLM_CALL":
            continue
        data, result = e.input or {}, e.output or {}
        body = data.get("request_body") or {}
        params = "  ".join(f"{k}={body[k]}" for k in ("model", "temperature", "max_tokens") if k in body)
        out.append(head(f"LLM call #{e.sequence} {e.name} -> {result.get('status')} (attempts={result.get('attempts')})"))
        out.append(f"Request: POST {data.get('url')}  {params}  (Authorization header not shown)")
        for i, message in enumerate(body.get("messages", []), 1):
            out.append(head(f"--- request message {i}: {message['role']} ({len(message['content'])} chars)"))
            out += _payload(message["content"], markdown)
        for x in result.get("exchanges", []):
            if "error" in x:
                out.append(head(f"--- response attempt {x['attempt']}: ERROR {x['error']}"))
                continue
            raw = x.get("response_body") or {}
            choice = (raw.get("choices") or [{}])[0]
            usage = x.get("usage") or {}
            problems = x.get("validation_problems") or []
            out.append(head(
                f"--- response attempt {x['attempt']}: id={x.get('response_id')}  model={x.get('served_model')}"
                f"  provider={raw.get('provider', '—')}  finish_reason={choice.get('finish_reason', '—')}"
                f"  tokens={usage.get('prompt_tokens')} in / {usage.get('completion_tokens')} out"
                f"  validation={'PASS' if not problems else 'FAIL'}"
            ))
            out.append(f"response message: {(choice.get('message') or {}).get('role', 'assistant')}")
            out += _payload(x.get("raw_content") or "", markdown)
            out += [f"validation problem: {p}" for p in problems]
    return out


def _payload(text: str, markdown: bool) -> List[str]:
    lines = text.splitlines() or [""]
    if markdown:
        fence = "````" if "```" in text else "```"
        return [fence] + lines + [fence]
    return ["  │ " + line for line in lines]


def render_audit(audit: AuditTrail, show_llm_payload: bool = True, show_llm_raw: bool = False) -> str:
    out = [f"### Tool call log — {audit.reference}", f"Context version: {audit.context_version}", "", "```"]
    out += audit_lines(audit, show_llm_raw=show_llm_raw) + ["```"]
    payload = llm_payload_lines(audit, markdown=True) if show_llm_payload else []
    if payload:
        out += ["", "### LLM request and response (OpenRouter)", ""]
        fence = None
        for line in payload:
            if fence is None and line.startswith("```"):
                fence = line
            elif fence is not None and line == fence:
                fence = None
            elif fence is None:
                line += "  "  # Markdown hard line break for heading/metadata lines
            out.append(line)
    return "\n".join(out) + "\n"


# --- Terminal rendering -----------------------------------------------------------------------

GOOD = {"PASS", "COMPLETE", "SUPPORTED", "APPROVE", "ELIGIBLE", "OK", "DRAFTED", "FOUND", "READY_FOR_AUTHORIZATION"}
BAD = {"FAIL", "MISSING", "NOT_SUPPORTED", "REJECT", "INELIGIBLE", "ERROR", "FAILED", "UNRESOLVED", "ESCALATED"}
WARN = {"UNCERTAIN", "INCOMPLETE", "PENDING", "SKIPPED", "INSUFFICIENT_EVIDENCE", "REFER_TO_MEDICAL_REVIEW",
        "REQUEST_MORE_INFO", "UNDETERMINED", "UNRESOLVED_ITEMS", "PENDING_INFORMATION", "PENDING_REVIEW"}
MARK = {"PASS": "✓", "COMPLETE": "✓", "FAIL": "✗", "MISSING": "✗", "INCOMPLETE": "!", "UNCERTAIN": "?", "NOT_APPLICABLE": "–"}


class _Term:
    def __init__(self, color: bool, width: int):
        self.color = color
        self.width = max(60, min(width, 120))

    def paint(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color and text else text

    def status(self, value: Any, pad: int = 0) -> str:
        """Color a status word; padding is applied before coloring so columns stay aligned."""
        raw = "" if value is None else str(value)
        code = "32" if raw in GOOD else "31" if raw in BAD else "33" if raw in WARN else ""
        padded = label(value).ljust(pad)
        return self.paint(padded, code) if code else padded

    def bold(self, text: str) -> str:
        return self.paint(text, "1")

    def dim(self, text: str) -> str:
        return self.paint(text, "2")

    def wrap(self, text: str, indent: int, first: str = "") -> List[str]:
        """Wrap plain text; `first` is a pre-rendered (possibly colored) prefix for the first line."""
        avail = max(20, self.width - indent)
        lines = textwrap.wrap(str(text), avail) or [""]
        pad = " " * indent
        return [first + lines[0]] + [pad + line for line in lines[1:]]

    def field(self, label: str, value: Any, indent: int = 2, label_width: int = 14) -> List[str]:
        prefix = " " * indent + f"{label:<{label_width}}"
        return self.wrap("—" if value is None else value, indent + label_width, prefix)


def render_text(
    report: Dict[str, Any], audit: AuditTrail, color: bool = False, width: int = 100,
    show_llm_payload: bool = True, show_llm_raw: bool = False,
) -> str:
    t = _Term(color, width)
    results = section_results(report)

    def heading(number: int, title: str) -> str:
        return t.bold(f"{number}. {title}") + " (" + t.status(results[number]) + ")"

    m = report["metadata"]
    dr, pv, mn, bc, rec = (report[k] for k in ("document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation"))
    rule = "─" * t.width
    dx, px = m["verified_diagnosis"], m["verified_procedures"]
    out = [
        rule,
        t.bold(f"CLAIM ASSESSMENT  {m['claim_id']}") + "   " + t.dim("fictional data · recommendation only"),
        rule,
        "  " + f"{'Recommendation':<16}" + t.bold(t.status(rec["outcome"] or "PENDING_REVIEW")),
        *t.field("Payable", f"{_amount(rec['recommended_payable'])} {m['currency']}" if rec["recommended_payable"] else "PENDING", label_width=16),
        "  " + f"{'Status':<16}" + t.status(report["assessment_status"]) + "   authorization " + t.status(report["human_review"]["authorization_status"]),
        *t.field("Next action", f"{rec['next_action']} ({rec['authorization_owner']})", label_width=16),
        "",
        t.bold("Claim"),
        *t.field("Policy", f"{m['policy_id']} v{m['policy_version'] or '—'}"),
        *t.field("Policyholder", _policyholder(m["policyholder"])),
        *t.field("Member", m["member_id"]),
        *t.field("Type", m["claim_type"]),
        *t.field("Treatment", f"{m['treatment_dates']['start']} to {m['treatment_dates']['end']}"),
        *t.field("Amount", f"{m['submitted_amount']} {m['currency']}"),
        *t.field("Diagnosis", (f"{dx['value']} ({dx['source']})" if dx["verified"] else f"Not verified (reported: {m['reported_diagnosis']})")),
        *t.field("Procedures", (f"{_flat(px['value'], ', ')} ({px['source']})" if px["verified"] else f"Not verified (reported: {_flat(m['reported_procedures'], ', ')})")),
        *t.field("Assessment", f"{m['assessment_id']} at {m['assessment_date']}"),
        "",
        heading(1, "Document review"),
    ]
    for r in dr["rows"]:
        req = r["requirement_id"] or "extra"
        detail = r["document_id"] or ""
        if r["submitted_type"] and r["detected_type"] and r["submitted_type"] != r["detected_type"]:
            detail += f" submitted as {r['submitted_type']}"
        issues = "; ".join(r["issues"])
        text = f"{r['document_type']:<24} " + " — ".join(x for x in (detail.strip(), issues) if x)
        head = f"  {MARK.get(r['status'], '·')} {req:<9} {t.status(r['status'], 15)} "
        out += t.wrap(text, 2 + 2 + 10 + 16, head)

    out += ["", heading(2, "Policy verification")]
    if pv["status"] != "FOUND":
        out += t.wrap(f"Policy record unresolved: {pv['reason']}", 4, "    ")
    for c in pv["checks"]:
        refs = _flat(c["clause_ids"] + c.get("rule_ids", []))
        head = f"  {MARK.get(c['result'], '·')} {t.status(c['result'], 10)} {c['label']:<32} "
        out += t.wrap(f"{c['verified_fact']} [{refs if refs != '[]' else 'no clause'}]", 2 + 2 + 11 + 33, head)

    out += ["", heading(3, "Medical necessity")]
    if mn["rule_id"]:
        out += t.field("Rule", f"{mn['rule_id']} — {mn['clinical_source']}", 4)
        out += t.field("Rationale", mn["rationale"], 4)
    out += t.field("Evidence", "; ".join(f"{e['document_id']} {e['location']}" for e in mn["evidence"]) or "none", 4)
    out += t.field("Policy clause", _flat(mn["policy_clause_ids"]), 4)
    for concern in mn["outstanding_concerns"]:
        out += t.field("Concern", concern, 4)

    out += ["", heading(4, "Benefit calculation") + f"  {bc['currency']}"]
    for name, key in (("Submitted", "submitted"), ("Excluded", "excluded"), ("Eligible", "eligible"), ("Deductible", "deductible"),
                       ("Copay", "copay"), ("Coinsurance", "coinsurance"), ("Limit adjust", "limit_adjustment")):
        out.append(f"    {name:<22}{_amount(bc[key]):>12}")
    out.append("    " + t.bold(f"{'Insurer payable':<22}{_amount(bc['insurer_payable']):>12}"))
    out.append("    " + t.bold(f"{'Member responsibility':<22}{_amount(bc['member_responsibility']):>12}"))
    out.append(f"    {'Remaining limit':<22}{_amount(bc['remaining_limit_before']):>12} -> {_amount(bc['remaining_limit_after'])}")
    if bc["clause_ids"]:
        out += t.field("Clauses", _flat(bc["clause_ids"], ", "), 4, 22)
    for reason in bc["pending_reasons"]:
        out += t.field("Pending because", reason, 4, 22)

    out += ["", heading(5, "Recommendation")]
    for i, r in enumerate(rec["reasons"], 1):
        out += t.wrap(f"{r['finding']} [evidence {_flat(r['evidence'], ', ')}; cites {_flat(r['citation_ids'], ', ')}]", 12, f"  {f'{i}.':<10}")
    for q in rec["information_requests"]:
        out += t.wrap(
            f"{q['required_item']} from {q['request_to']} ({q['request_id']}, {q['status']}). {q['why_needed']} "
            f"Requirement {q['requirement_id']}; policy condition {q['policy_clause_id'] or '—'}. {q['reassessment_trigger']}",
            12, "  " + t.paint(f"{'request':<10}", "33"),
        )
    for esc in rec["escalations"]:
        out += t.wrap(esc, 12, "  " + t.dim(f"{'note':<10}"))

    out += ["", heading(6, "Citations")]
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for c in report["policy_citations"]["citations"]:
        groups.setdefault(f"{c['kind'].capitalize()} · {c['source_document']} v{c['version']}", []).append(c)
    for source, citations in groups.items():
        out.append("  " + t.dim(source))
        for c in citations:
            head = f"    {c['citation_id']} {c['clause_id']:<9} "
            out += t.wrap(c["location"] or "", len(head), head)
            out += [t.dim(line) for line in t.wrap(f"“{c['text']}”", len(head), " " * len(head))]

    v = report["validation"]
    out += ["", t.bold("Validation") + "  " + t.status(v["status"]) + f"   citations {t.status(v['citation_check'])}   reconciliation {label(v['reconciliation'])}"]
    for err in v["errors"]:
        out += t.wrap(err, 4, "  - ")
    ex = report["explanations"]
    out += [t.bold("Explanations") + "  " + t.status(ex["status"]) + (f"   model {ex['llm']['served_model']}" if ex.get("llm", {}).get("served_model") else "")]
    for section, text in ex["sections"].items():
        out += t.wrap(text, 4 + 22, f"    {section:<22}")

    payload = llm_payload_lines(audit) if show_llm_payload else []
    if payload:
        out += ["", t.bold("LLM request and response (OpenRouter)")]
        for line in payload:
            if line.startswith("  │ "):
                out.append(t.dim("  │ ") + line[4:])
            elif line.startswith(("LLM call", "---")):
                out.append(t.bold(line))
            else:
                out.append(line)

    out += ["", t.bold("Tool calls") + "  " + t.dim(f"{audit.reference} · {audit.context_version}")]
    out += ["  " + line for line in audit_lines(audit, max_width=t.width - 2, show_time=False, show_llm_raw=show_llm_raw)]
    out.append(rule)
    return "\n".join(out) + "\n"
