"""OpenRouter client and explanation drafting, using a fake transport (no network)."""

import json
import unittest

from claim_agent.llm import (
    DEFAULT_MODEL,
    OPENROUTER_URL,
    LLMConfig,
    LLMError,
    OpenRouterClient,
    draft_explanations,
    validate_explanations,
)

FACTS = {
    "claim_id": "CLM-APP-001",
    "recommendation": "APPROVE",
    "benefit": {"submitted": "200.00", "copay": "20.00", "insurer_payable": "180.00"},
    "citations": ["APP-5.3"],
    "evidence": ["A-D4"],
}
SECTIONS = ["benefit_calculation", "recommendation"]
GOOD = {
    "benefit_calculation": "USD 200.00 submitted; the USD 20.00 copay under APP-5.3 leaves USD 180.00 payable.",
    "recommendation": "APPROVE, supported by the medical report A-D4, pending human authorization.",
}


def completion(content, model="openai/gpt-4o-2024-08-06", response_id="gen-1"):
    return {"id": response_id, "model": model, "choices": [{"message": {"content": content}}], "usage": {"total_tokens": 42}}


class FakeTransport:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, headers, payload, timeout):
        self.calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def client_with(*responses, max_attempts=2):
    transport = FakeTransport(*responses)
    return OpenRouterClient(LLMConfig(api_key="test-key", retry_delay_s=0, max_attempts=max_attempts), transport), transport


class LLMConfigTest(unittest.TestCase):
    def test_reads_key_and_model_from_env(self):
        config = LLMConfig.from_env({"OPENROUTER_API_KEY": "k", "OPENROUTER_MODEL": "anthropic/claude-x"})
        self.assertEqual(config.api_key, "k")
        self.assertEqual(config.model, "anthropic/claude-x")

    def test_defaults_model(self):
        self.assertEqual(LLMConfig.from_env({"OPENROUTER_API_KEY": "k"}).model, DEFAULT_MODEL)

    def test_missing_key_raises(self):
        with self.assertRaises(LLMError):
            LLMConfig.from_env({})

    def test_key_never_appears_in_recorded_config_or_repr(self):
        config = LLMConfig(api_key="secret-key-value", retry_delay_s=0)
        self.assertNotIn("secret-key-value", json.dumps(config.describe()))
        self.assertNotIn("secret-key-value", repr(config))


class OpenRouterClientTest(unittest.TestCase):
    def test_sends_chat_completion_request(self):
        client, transport = client_with(completion("hi"))
        client.chat([{"role": "user", "content": "hello"}])
        call = transport.calls[0]
        self.assertEqual(call["url"], OPENROUTER_URL)
        self.assertEqual(call["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(call["headers"]["Content-Type"], "application/json")
        self.assertEqual(call["payload"]["model"], DEFAULT_MODEL)
        self.assertEqual(call["payload"]["messages"], [{"role": "user", "content": "hello"}])
        self.assertEqual(call["payload"]["max_tokens"], 1000)

    def test_parses_content_and_metadata(self):
        client, _ = client_with(completion("hi"))
        response = client.chat([{"role": "user", "content": "hello"}])
        self.assertEqual(response.content, "hi")
        self.assertEqual(response.model, "openai/gpt-4o-2024-08-06")
        self.assertEqual(response.response_id, "gen-1")
        self.assertEqual(response.usage, {"total_tokens": 42})

    def test_missing_choices_raises(self):
        client, _ = client_with({"id": "x"})
        with self.assertRaises(LLMError):
            client.chat([])

    def test_error_body_raises(self):
        client, _ = client_with({"error": {"code": 401, "message": "No auth credentials found"}})
        with self.assertRaises(LLMError):
            client.chat([])


class ValidateExplanationsTest(unittest.TestCase):
    def test_accepts_grounded_output(self):
        explanations, problems = validate_explanations(json.dumps(GOOD), SECTIONS, FACTS)
        self.assertEqual(problems, [])
        self.assertEqual(explanations, GOOD)

    def test_accepts_fenced_json(self):
        _, problems = validate_explanations("```json\n" + json.dumps(GOOD) + "\n```", SECTIONS, FACTS)
        self.assertEqual(problems, [])

    def test_rejects_non_json(self):
        explanations, problems = validate_explanations("Sure! Here is the explanation.", SECTIONS, FACTS)
        self.assertEqual(explanations, {})
        self.assertTrue(problems)

    def test_rejects_missing_or_extra_sections(self):
        _, problems = validate_explanations(json.dumps({"recommendation": GOOD["recommendation"]}), SECTIONS, FACTS)
        self.assertTrue(problems)
        _, problems = validate_explanations(json.dumps({**GOOD, "extra": "x"}), SECTIONS, FACTS)
        self.assertTrue(problems)

    def test_rejects_invented_clause(self):
        bad = {**GOOD, "benefit_calculation": "Copay applies under APP-9.9."}
        _, problems = validate_explanations(json.dumps(bad), SECTIONS, FACTS)
        self.assertTrue(any("APP-9.9" in p for p in problems))

    def test_rejects_invented_document(self):
        bad = {**GOOD, "recommendation": "APPROVE based on A-D7."}
        _, problems = validate_explanations(json.dumps(bad), SECTIONS, FACTS)
        self.assertTrue(any("A-D7" in p for p in problems))

    def test_rejects_amount_not_in_facts(self):
        bad = {**GOOD, "benefit_calculation": "Insurer pays USD 190.00."}
        _, problems = validate_explanations(json.dumps(bad), SECTIONS, FACTS)
        self.assertTrue(any("190.00" in p for p in problems))

    def test_rejects_outcome_not_in_facts(self):
        bad = {**GOOD, "recommendation": "This claim should be REJECT instead."}
        _, problems = validate_explanations(json.dumps(bad), SECTIONS, FACTS)
        self.assertTrue(any("REJECT" in p for p in problems))

    def test_rejects_empty_section(self):
        _, problems = validate_explanations(json.dumps({**GOOD, "recommendation": " "}), SECTIONS, FACTS)
        self.assertTrue(problems)


class DraftExplanationsTest(unittest.TestCase):
    def test_drafts_on_first_valid_response(self):
        client, transport = client_with(completion(json.dumps(GOOD)))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual(result.status, "DRAFTED")
        self.assertEqual(result.explanations, GOOD)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.served_model, "openai/gpt-4o-2024-08-06")
        self.assertEqual(result.response_id, "gen-1")
        self.assertEqual(result.config["model"], DEFAULT_MODEL)
        messages = transport.calls[0]["payload"]["messages"]
        self.assertEqual(json.loads(messages[1]["content"]), FACTS)

    def test_retries_after_malformed_output(self):
        client, _ = client_with(completion("not json"), completion(json.dumps(GOOD)))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual(result.status, "DRAFTED")
        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.errors)

    def test_records_prompt_and_raw_reply_for_every_attempt(self):
        client, _ = client_with(completion("not json"), completion(json.dumps(GOOD)))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual([m["role"] for m in result.request_messages], ["system", "user"])
        self.assertEqual([x["raw_content"] for x in result.exchanges], ["not json", json.dumps(GOOD)])
        self.assertTrue(result.exchanges[0]["validation_problems"])
        self.assertEqual(result.exchanges[1]["validation_problems"], [])

    def test_fails_after_bounded_retries_without_raising(self):
        client, transport = client_with(completion("x"), completion("y"), completion(json.dumps(GOOD)))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual(result.status, "FAILED")
        self.assertEqual(result.explanations, {})
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(transport.calls), 2)

    def test_facts_are_sent_as_compact_json(self):
        client, transport = client_with(completion(json.dumps(GOOD)))
        draft_explanations(client, FACTS, SECTIONS)
        user = transport.calls[0]["payload"]["messages"][1]["content"]
        self.assertEqual(user, json.dumps(FACTS, separators=(",", ":")))
        self.assertNotIn("\n", user)
        self.assertNotIn(": ", user)

    def test_non_retryable_http_errors_stop_after_one_attempt(self):
        for status in (400, 401, 402, 403, 404):
            with self.subTest(status=status):
                client, transport = client_with(
                    LLMError(f"OpenRouter returned HTTP {status}", retryable=False, status=status), completion(json.dumps(GOOD)),
                )
                result = draft_explanations(client, FACTS, SECTIONS)
                self.assertEqual(result.status, "FAILED")
                self.assertEqual((result.attempts, len(transport.calls)), (1, 1))
                self.assertEqual(result.exchanges[0]["http_status"], status)
                self.assertFalse(result.exchanges[0]["retryable"])
                self.assertIn("Not retried", result.errors[-1])

    def test_retryable_errors_are_retried(self):
        for error in (LLMError("HTTP 429", retryable=True, status=429), LLMError("HTTP 503", retryable=True, status=503), LLMError("timeout")):
            with self.subTest(error=str(error)):
                client, transport = client_with(error, completion(json.dumps(GOOD)))
                result = draft_explanations(client, FACTS, SECTIONS)
                self.assertEqual((result.status, result.attempts, len(transport.calls)), ("DRAFTED", 2, 2))

    def test_retry_classification(self):
        from claim_agent.llm import is_retryable_status
        self.assertEqual([is_retryable_status(c) for c in (None, 429, 500, 502, 503)], [True] * 5)
        self.assertEqual([is_retryable_status(c) for c in (400, 401, 402, 403, 404, 422)], [False] * 6)

    def test_error_body_with_code_is_classified(self):
        client, _ = client_with({"error": {"code": 402, "message": "Insufficient credits"}})
        with self.assertRaises(LLMError) as raised:
            client.chat([])
        self.assertEqual((raised.exception.status, raised.exception.retryable), (402, False))

    def test_retry_waits_with_backoff_and_honors_retry_after(self):
        waits = []
        transport = FakeTransport(LLMError("HTTP 429", status=429), LLMError("HTTP 503", status=503), completion(json.dumps(GOOD)))
        client = OpenRouterClient(LLMConfig(api_key="k", max_attempts=3, retry_delay_s=2.0), transport)
        self.assertEqual(draft_explanations(client, FACTS, SECTIONS, sleep=waits.append).status, "DRAFTED")
        self.assertEqual(waits, [2.0, 4.0])
        waits.clear()
        transport = FakeTransport(LLMError("HTTP 429", status=429, retry_after_s=7.5), completion(json.dumps(GOOD)))
        client = OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=2.0), transport)
        draft_explanations(client, FACTS, SECTIONS, sleep=waits.append)
        self.assertEqual(waits, [7.5])

    def test_no_wait_after_last_attempt_or_non_retryable_error(self):
        waits = []
        client = OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=2.0), FakeTransport(LLMError("t"), LLMError("t")))
        draft_explanations(client, FACTS, SECTIONS, sleep=waits.append)
        self.assertEqual(waits, [2.0])
        waits.clear()
        client = OpenRouterClient(LLMConfig(api_key="k", retry_delay_s=2.0), FakeTransport(LLMError("402", retryable=False, status=402)))
        draft_explanations(client, FACTS, SECTIONS, sleep=waits.append)
        self.assertEqual(waits, [])

    def test_answer_cut_off_by_reasoning_is_explained_and_not_retried(self):
        body = {"id": "gen-x", "model": "m", "choices": [{"finish_reason": "length", "message": {"role": "assistant", "content": None}}],
                "usage": {"completion_tokens": 1000, "completion_tokens_details": {"reasoning_tokens": 972}}}
        client, transport = client_with(body, completion(json.dumps(GOOD)))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual((result.status, len(transport.calls)), ("FAILED", 1))
        self.assertIn("972 tokens spent on reasoning", result.errors[0])
        self.assertIn("OPENROUTER_MAX_TOKENS", result.errors[0])

    def test_empty_content_without_length_is_retryable(self):
        body = {"id": "gen-x", "model": "m", "choices": [{"finish_reason": "stop", "message": {"content": ""}}]}
        client, transport = client_with(body, completion(json.dumps(GOOD)))
        self.assertEqual(draft_explanations(client, FACTS, SECTIONS).status, "DRAFTED")

    def test_reasoning_effort_and_max_tokens_from_env(self):
        config = LLMConfig.from_env({"OPENROUTER_API_KEY": "k", "OPENROUTER_MAX_TOKENS": "4000", "OPENROUTER_REASONING_EFFORT": "Low"})
        self.assertEqual((config.max_tokens, config.reasoning_effort), (4000, "low"))
        body = OpenRouterClient(config).request_body([])
        self.assertEqual((body["max_tokens"], body["reasoning"]), (4000, {"effort": "low"}))
        self.assertNotIn("reasoning", OpenRouterClient(LLMConfig(api_key="k")).request_body([]))
        for bad in ({"OPENROUTER_MAX_TOKENS": "lots"}, {"OPENROUTER_REASONING_EFFORT": "extreme"}):
            with self.subTest(env=bad), self.assertRaises(LLMError):
                LLMConfig.from_env({"OPENROUTER_API_KEY": "k", **bad})

    def test_transport_error_fails_without_raising(self):
        client, _ = client_with(LLMError("timeout"), LLMError("timeout"))
        result = draft_explanations(client, FACTS, SECTIONS)
        self.assertEqual(result.status, "FAILED")
        self.assertEqual(len(result.errors), 2)


if __name__ == "__main__":
    unittest.main()
