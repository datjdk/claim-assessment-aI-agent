"""Terminal and Markdown rendering: readable report, one log line per tool call."""

import re
import unittest

from claim_agent.labels import label
from claim_agent.orchestrator import assess_claim
from claim_agent.render import audit_lines, render_audit, render_report, render_text
from helpers import STORE

CASES = ("CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001")


def tool_call_block(text):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("Tool calls"))
    return [line for line in lines[start + 1:] if line.strip() and not line.startswith("─")]


class AuditLinesTest(unittest.TestCase):
    def test_one_line_per_audit_event(self):
        for claim_id in CASES:
            a = assess_claim(claim_id, STORE)
            with self.subTest(claim=claim_id):
                block = tool_call_block(render_text(a.report, a.audit, width=110))
                self.assertEqual(len(block), len(a.audit.events))
                for line, event in zip(block, a.audit.events):
                    self.assertTrue(line.strip().startswith(f"{event.sequence} {event.status}"), line)
                    self.assertIn(event.name, line)

    def test_key_results_fit_at_110_columns(self):
        expected = {
            "CLM-APP-001": ["SUPPORTED rule=CR-001", "payable=180.00 member=20.00 remaining=620.00"],
            "CLM-REJ-001": ["exclusions=FAIL", "NOT_SUPPORTED rule=CR-002", "payable=0.00 member=2000.00"],
            "CLM-RFI-001": ["issues=TYPE_MISMATCH", "exclusions=UNCERTAIN remaining=1200.00", "SKIPPED calculateBenefit"],
        }
        for claim_id, snippets in expected.items():
            a = assess_claim(claim_id, STORE)
            block = "\n".join(tool_call_block(render_text(a.report, a.audit, width=110)))
            for snippet in snippets:
                with self.subTest(claim=claim_id, snippet=snippet):
                    self.assertIn(snippet, block)

    def test_lines_respect_width_and_never_cut_an_argument_value(self):
        for width in (80, 100, 120):
            for claim_id in CASES:
                a = assess_claim(claim_id, STORE)
                for line in audit_lines(a.audit, max_width=width, show_time=False):
                    with self.subTest(width=width, line=line):
                        self.assertLessEqual(len(line), width)
                        call = line.split(" -> ")[0]
                        self.assertIsNone(re.search(r"[^ ,(]…", call), "argument value cut mid-way")

    def test_markdown_log_keeps_full_lines_with_times(self):
        a = assess_claim("CLM-APP-001", STORE)
        md = render_audit(a.audit)
        self.assertIn('checkMedicalNecessity("Acute bacterial sinusitis", ["Outpatient consultation", "Prescribed treatment"])', md)
        self.assertRegex(md, r"\n 1 \d\d:\d\d:\d\d OK")
        self.assertNotIn("…", md)


class RenderTextTest(unittest.TestCase):
    def test_sections_and_summary_present(self):
        a = assess_claim("CLM-RFI-001", STORE)
        text = render_text(a.report, a.audit, width=100)
        for heading in ("1. Document review", "2. Policy verification", "3. Medical necessity",
                        "4. Benefit calculation", "5. Recommendation", "6. Citations", "Tool calls"):
            self.assertIn(heading, text)
        self.assertIn("Recommendation  Request more information", text)
        self.assertIn("✗ OP-REQ-4  Missing", text)

    def test_no_color_codes_unless_requested(self):
        a = assess_claim("CLM-APP-001", STORE)
        self.assertNotIn("\033[", render_text(a.report, a.audit, color=False))
        self.assertIn("\033[", render_text(a.report, a.audit, color=True))

    def test_text_lines_fit_terminal_width(self):
        a = assess_claim("CLM-APP-001", STORE)
        for line in render_text(a.report, a.audit, width=100).splitlines():
            with self.subTest(line=line[:40]):
                self.assertLessEqual(len(line), 100)



class SectionHeadingTest(unittest.TestCase):
    EXPECTED = {
        "CLM-APP-001": ["COMPLETE", "ELIGIBLE", "SUPPORTED", "COMPLETE", "APPROVE", "PASS"],
        "CLM-REJ-001": ["COMPLETE", "INELIGIBLE", "NOT_SUPPORTED", "COMPLETE", "REJECT", "PASS"],
        "CLM-RFI-001": ["UNRESOLVED_ITEMS", "UNDETERMINED", "INSUFFICIENT_EVIDENCE", "PENDING", "REQUEST_MORE_INFO", "PASS"],
    }
    MD_TITLES = ["Document Review", "Policy Verification", "Medical Necessity", "Benefit Calculation", "Recommendation", "Policy Citations"]
    TEXT_TITLES = ["Document review", "Policy verification", "Medical necessity", "Benefit calculation", "Recommendation", "Citations"]

    def test_every_heading_shows_its_result(self):
        for claim_id, results in self.EXPECTED.items():
            a = assess_claim(claim_id, STORE)
            md = render_report(a.report)
            text = render_text(a.report, a.audit)
            for n, result in enumerate(results, 1):
                with self.subTest(claim=claim_id, section=n):
                    self.assertIn(f"\n## {n}. {self.MD_TITLES[n - 1]} ({label(result)})\n", md)
                    self.assertIn(f"\n{n}. {self.TEXT_TITLES[n - 1]} ({label(result)})", text)

    def test_escalated_assessment_heading_says_pending_review(self):
        import dataclasses
        a = assess_claim("CLM-APP-001", dataclasses.replace(STORE, balances=[]))
        self.assertIn("## 5. Recommendation (Pending review (no recommendation))", render_report(a.report))


class PlainTextLabelTest(unittest.TestCase):
    def test_label_maps_codes_and_falls_back_to_sentence_case(self):
        self.assertEqual(label("REQUEST_MORE_INFO"), "Request more information")
        self.assertEqual(label("INSUFFICIENT_EVIDENCE"), "Insufficient evidence")
        self.assertEqual(label("SOME_NEW_CODE"), "Some new code")
        self.assertEqual(label(None), "—")

    def test_reports_show_no_result_codes(self):
        codes = ["UNRESOLVED_ITEMS", "INSUFFICIENT_EVIDENCE", "REQUEST_MORE_INFO", "PENDING_INFORMATION", "UNDETERMINED"]
        a = assess_claim("CLM-RFI-001", STORE)
        md_without_log = render_report(a.report)
        text = render_text(a.report, a.audit)
        text_without_log = text[: text.index("Tool calls")]
        for code in codes:
            with self.subTest(code=code):
                self.assertNotIn(f"({code})", md_without_log)
                self.assertNotIn(f"**{code}**", md_without_log)
                self.assertNotIn(f"({code})", text_without_log)

    def test_json_keeps_codes(self):
        a = assess_claim("CLM-RFI-001", STORE)
        self.assertEqual(a.report["recommendation"]["outcome"], "REQUEST_MORE_INFO")
        self.assertEqual(a.report["document_review"]["conclusion"], "UNRESOLVED_ITEMS")


def llm_call(assessment):
    return next(e for e in assessment.audit.events if e.event == "LLM_CALL")


class LlmPayloadTest(unittest.TestCase):
    def assessed_with_llm(self, *contents):
        from claim_agent.llm import LLMConfig, OpenRouterClient

        bodies = [
            {"id": f"gen-{i}", "model": "test/model", "provider": "TestProvider",
             "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": c}}],
             "usage": {"prompt_tokens": 100, "completion_tokens": 20}}
            for i, c in enumerate(contents, 1)
        ]
        client = OpenRouterClient(LLMConfig(api_key="secret-test-key", retry_delay_s=0), lambda *a: bodies.pop(0))
        return assess_claim("CLM-APP-001", STORE, client)

    def test_text_shows_full_request_and_response_messages(self):
        a = self.assessed_with_llm("not json", '{"document_review": "x"}')
        text = render_text(a.report, a.audit, width=100)
        body = llm_call(a).input["request_body"]
        self.assertIn("LLM request and response (OpenRouter)", text)
        self.assertIn("Request: POST https://openrouter.ai/api/v1/chat/completions", text)
        self.assertIn("--- request message 1: system", text)
        self.assertIn("--- request message 2: user", text)
        for message in body["messages"]:
            for line in message["content"].splitlines():
                self.assertIn("  │ " + line, text)
        self.assertIn("--- response attempt 1: id=gen-1", text)
        self.assertIn("finish_reason=stop", text)
        self.assertIn("  │ not json", text)
        self.assertIn("--- response attempt 2: id=gen-2", text)
        self.assertIn("validation problem:", text)

    def test_markdown_shows_payload_in_code_blocks(self):
        a = self.assessed_with_llm('{"document_review": "x"}', "y")
        md = render_audit(a.audit)
        self.assertIn("### LLM request and response (OpenRouter)", md)
        self.assertIn("**--- request message 1: system", md)
        self.assertIn('```\n{"document_review": "x"}\n```', md)

    def test_api_key_never_rendered(self):
        a = self.assessed_with_llm("not json", "still not")
        self.assertNotIn("secret-test-key", render_text(a.report, a.audit) + render_audit(a.audit))

    def test_payload_can_be_hidden(self):
        a = self.assessed_with_llm("not json", "still not")
        self.assertNotIn("LLM request and response", render_text(a.report, a.audit, show_llm_payload=False))
        self.assertNotIn("LLM request and response", render_audit(a.audit, show_llm_payload=False))

    def test_tool_call_log_includes_raw_request_and_response_bodies(self):
        import json
        a = self.assessed_with_llm("not json", '{"document_review": "x"}')
        event = llm_call(a)
        sent = json.dumps(event.input["request_body"])
        for output in (render_audit(a.audit, show_llm_raw=True), render_text(a.report, a.audit, width=100, show_llm_raw=True)):
            log = output[output.index("Tool call"):]
            self.assertIn("↳ request body (POST https://openrouter.ai/api/v1/chat/completions): " + sent, log)
            for x in event.output["exchanges"]:
                self.assertIn(f"↳ response body (attempt {x['attempt']}): " + x["response_raw"], log)
            self.assertNotIn("secret-test-key", log)

    def test_raw_response_text_is_kept_exactly(self):
        from claim_agent.llm import LLMConfig, OpenRouterClient, RawJSON
        text = '{"id":"gen-raw",  "model":"m","choices":[{"message":{"role":"assistant","content":"hi"}}]}'
        import json
        client = OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=0), lambda *a: RawJSON(json.loads(text), text))
        self.assertEqual(client.chat([]).raw_text, text)

    def test_padded_raw_response_stays_on_one_log_line(self):
        from claim_agent.llm import LLMConfig, OpenRouterClient, RawJSON
        import json
        sections = ["document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation"]
        body = {"id": "gen-pad", "model": "m", "choices": [{"message": {"role": "assistant",
                "content": json.dumps({s: "Consistent with the verified facts." for s in sections})}}]}
        text = "\n         \n" + json.dumps(body)
        client = OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=0), lambda *a: RawJSON(body, text))
        a = assess_claim("CLM-APP-001", STORE, client)
        self.assertEqual(llm_call(a).output["exchanges"][0]["response_raw"], text)
        line = next(l for l in render_audit(a.audit, show_llm_raw=True).splitlines() if "↳ response body" in l)
        self.assertTrue(line.endswith(json.dumps(body)))

    def test_raw_bodies_only_with_raw_flag(self):
        a = self.assessed_with_llm("not json", "still not")
        self.assertNotIn("↳ request body", render_audit(a.audit))
        self.assertNotIn("↳ request body", render_text(a.report, a.audit))
        self.assertIn("↳ request body", render_audit(a.audit, show_llm_raw=True))

    def test_every_openrouter_call_is_logged_with_short_request_and_response(self):
        a = self.assessed_with_llm("not json", '{"document_review": "x"}')
        calls = [e for e in a.audit.events if e.event == "LLM_REQUEST"]
        self.assertEqual([c.input["attempt"] for c in calls], [1, 2])
        self.assertLess(calls[0].sequence, llm_call(a).sequence)
        lines = audit_lines(a.audit, max_width=110, show_time=False)
        call_line = next(i for i, l in enumerate(lines) if "openrouter.chat(attempt 1)" in l)
        self.assertIn("validation=FAIL (1 problem) tokens=100/20 test/model id=gen-1", lines[call_line])
        self.assertTrue(lines[call_line + 1].startswith("   ↳ request system (603 chars): You draft explanations"))
        self.assertTrue(lines[call_line + 2].startswith('   ↳ request user ('))
        self.assertIn('{"claim_id":"CLM-APP-001"', lines[call_line + 2])
        self.assertEqual(lines[call_line + 3], "   ↳ response (8 chars): not json")
        self.assertIn("openrouter.chat(attempt 2)", lines[call_line + 4])
        for line in lines:
            self.assertLessEqual(len(line), 110)
            self.assertNotIn("secret-test-key", line)

    def test_failed_openrouter_call_is_logged_as_error(self):
        from claim_agent.llm import LLMConfig, LLMError, OpenRouterClient

        def fail(*a):
            raise LLMError("OpenRouter returned HTTP 402: insufficient credits")

        a = assess_claim("CLM-APP-001", STORE, OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=0, max_attempts=1), fail))
        call = next(e for e in a.audit.events if e.event == "LLM_REQUEST")
        self.assertEqual(call.status, "ERROR")
        self.assertIn("error: OpenRouter returned HTTP 402", "\n".join(audit_lines(a.audit)))

    def test_no_section_without_llm_call(self):
        a = assess_claim("CLM-APP-001", STORE)
        self.assertNotIn("LLM request and response", render_text(a.report, a.audit))


if __name__ == "__main__":
    unittest.main()
