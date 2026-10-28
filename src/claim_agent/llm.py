"""OpenRouter client: drafts reviewer-facing explanations from supplied results only. Never decides, never invents clauses.

Calls the OpenAI-compatible Chat Completions endpoint with stdlib urllib. The API key is read
from OPENROUTER_API_KEY and is never logged or included in recorded configuration.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o"
REASONING_EFFORTS = ("minimal", "low", "medium", "high")
OUTCOMES = ("APPROVE", "REJECT", "REQUEST_MORE_INFO")

# url, headers, payload, timeout -> parsed JSON response
Transport = Callable[[str, Dict[str, str], Dict[str, Any], float], Dict[str, Any]]

_AMOUNT = re.compile(r"\b\d{1,3}(?:,\d{3})*\.\d{2}\b|\b\d+\.\d{2}\b")
# Hyphenated codes containing a digit: clause, document, claim, rule and requirement IDs.
_IDENTIFIER = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+(?:\.\d+)*)+\b")
_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)

SYSTEM_PROMPT = """You draft explanations for a human insurance claim assessor.
Rules:
- Use only the facts in the supplied JSON. Do not add clinical, policy or financial information.
- Do not make, change or question the recommendation. The application decided it; you explain it.
- Mention only clause IDs, document IDs and amounts that appear in the facts. Write amounts with two decimals exactly as given.
- Reply with one JSON object and nothing else. Its keys must be exactly: {sections}. Each value is a short plain-text explanation."""


class RawJSON(dict):
    """A parsed JSON response that also keeps the exact response text, for audit logging."""

    def __init__(self, data: Dict[str, Any], raw_text: str):
        super().__init__(data)
        self.raw_text = raw_text


class LLMError(Exception):
    """The model call failed or returned an unusable response.

    retryable is False for errors another attempt cannot fix (e.g. HTTP 401 bad key, 402 no credits, 400 bad request).
    """

    def __init__(self, message: str, retryable: bool = True, status: Optional[int] = None, retry_after_s: Optional[float] = None):
        super().__init__(message)
        self.retryable = retryable
        self.status = status
        self.retry_after_s = retry_after_s  # from a Retry-After header, when the server sends one


def is_retryable_status(status: Optional[int]) -> bool:
    """Retry rate limits and server errors; other 4xx responses will fail the same way again."""
    return status is None or status == 429 or status >= 500


@dataclass(frozen=True)
class LLMConfig:
    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    url: str = OPENROUTER_URL
    temperature: float = 0.0
    max_tokens: int = 1000
    timeout_s: float = 60.0
    max_attempts: int = 2
    reasoning_effort: Optional[str] = None  # sent as OpenRouter's {"reasoning": {"effort": ...}} when set
    retry_delay_s: float = 2.0  # wait before a retry, doubled each attempt; a Retry-After header wins

    @classmethod
    def from_env(cls, env: Optional[Dict[str, str]] = None) -> "LLMConfig":
        env = os.environ if env is None else env
        api_key = env.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise LLMError("OPENROUTER_API_KEY is not set.")
        max_tokens = env.get("OPENROUTER_MAX_TOKENS", "").strip()
        effort = env.get("OPENROUTER_REASONING_EFFORT", "").strip().lower()
        if effort and effort not in REASONING_EFFORTS:
            raise LLMError(f"OPENROUTER_REASONING_EFFORT must be one of {', '.join(REASONING_EFFORTS)}.")
        if max_tokens and not max_tokens.isdigit():
            raise LLMError("OPENROUTER_MAX_TOKENS must be a positive integer.")
        return cls(
            api_key=api_key,
            model=env.get("OPENROUTER_MODEL", "").strip() or DEFAULT_MODEL,
            max_tokens=int(max_tokens) if max_tokens else cls.max_tokens,
            reasoning_effort=effort or None,
        )

    def describe(self) -> Dict[str, Any]:
        """Configuration to record with each assessment. Excludes the API key."""
        return {
            "provider": "openrouter",
            "url": self.url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "reasoning_effort": self.reasoning_effort,
            "max_attempts": self.max_attempts,
        }


@dataclass(frozen=True)
class ChatResponse:
    content: str
    model: Optional[str]
    response_id: Optional[str]
    usage: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict)  # full response body as returned by OpenRouter
    raw_text: str = ""  # the response body text exactly as received


@dataclass
class ExplanationResult:
    status: str  # DRAFTED | FAILED
    explanations: Dict[str, str]
    attempts: int
    errors: List[str]
    config: Dict[str, Any]
    served_model: Optional[str] = None
    response_id: Optional[str] = None
    request_messages: List[Dict[str, str]] = field(default_factory=list)
    request_body: Dict[str, Any] = field(default_factory=dict)  # exact JSON body sent (the key is only in the header)
    exchanges: List[Dict[str, Any]] = field(default_factory=list)  # one per attempt: raw reply or error


def urllib_transport(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            return RawJSON(json.loads(text), text)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        retry_after = e.headers.get("Retry-After") if e.headers else None
        wait = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else None
        raise LLMError(f"OpenRouter returned HTTP {e.code}: {body}", is_retryable_status(e.code), e.code, wait) from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise LLMError(f"OpenRouter request failed: {e}") from e
    except json.JSONDecodeError as e:
        raise LLMError("OpenRouter returned a non-JSON response.") from e


class OpenRouterClient:
    def __init__(self, config: LLMConfig, transport: Transport = urllib_transport):
        self.config = config
        self._transport = transport

    def request_body(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if self.config.reasoning_effort:
            body["reasoning"] = {"effort": self.config.reasoning_effort}
        return body

    def chat(self, messages: List[Dict[str, str]]) -> ChatResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        data = self._transport(self.config.url, headers, self.request_body(messages), self.config.timeout_s)
        if "error" in data:
            error = data["error"]
            code = error.get("code") if isinstance(error, dict) else None
            status = code if isinstance(code, int) else None
            raise LLMError(f"OpenRouter error: {error}", is_retryable_status(status), status)
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError("OpenRouter response has no choices[0].message.content.") from e
        if not isinstance(content, str) or not content.strip():
            usage = data.get("usage") or {}
            reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
            if choice.get("finish_reason") == "length":
                # Same budget fails the same way, so do not retry.
                raise LLMError(
                    f"Model used all max_tokens={self.config.max_tokens} without an answer"
                    + (f" ({reasoning} tokens spent on reasoning)" if reasoning else "")
                    + "; raise OPENROUTER_MAX_TOKENS or lower OPENROUTER_REASONING_EFFORT.",
                    retryable=False,
                )
            raise LLMError("OpenRouter response has no text content.")
        raw_text = getattr(data, "raw_text", None) or json.dumps(data)
        return ChatResponse(content, data.get("model"), data.get("id"), data.get("usage") or {}, dict(data), raw_text)


def _normalize_amount(text: str) -> str:
    return text.replace(",", "")


def validate_explanations(
    content: str, sections: Sequence[str], facts: Dict[str, Any]
) -> Tuple[Dict[str, str], List[str]]:
    """Parse model output and check it against the supplied facts. Returns (explanations, problems)."""
    match = _FENCE.match(content.strip())
    try:
        parsed = json.loads(match.group(1) if match else content)
    except json.JSONDecodeError:
        return {}, ["Model output is not valid JSON."]
    if not isinstance(parsed, dict):
        return {}, ["Model output is not a JSON object."]

    problems = []
    if set(parsed) != set(sections):
        problems.append(f"Expected keys {sorted(sections)}, got {sorted(parsed)}.")
    facts_text = json.dumps(facts, default=str)
    known_amounts = {_normalize_amount(a) for a in _AMOUNT.findall(facts_text)}
    for key, text in parsed.items():
        if not isinstance(text, str) or not text.strip():
            problems.append(f"Section '{key}' is not a non-empty string.")
            continue
        for amount in _AMOUNT.findall(text):
            if _normalize_amount(amount) not in known_amounts:
                problems.append(f"Section '{key}' mentions amount {amount} not in the facts.")
        for identifier in _IDENTIFIER.findall(text):
            if any(c.isdigit() for c in identifier) and identifier not in facts_text:
                problems.append(f"Section '{key}' mentions identifier {identifier} not in the facts.")
        for outcome in OUTCOMES:
            if re.search(rf"\b{outcome}\b", text) and outcome not in facts_text:
                problems.append(f"Section '{key}' mentions outcome {outcome} not in the facts.")
    return ({k: v for k, v in parsed.items()} if not problems else {}), problems


ExchangeHook = Callable[[Dict[str, Any], List[Dict[str, str]]], None]


def draft_explanations(
    client: OpenRouterClient,
    facts: Dict[str, Any],
    sections: Sequence[str],
    on_exchange: Optional[ExchangeHook] = None,
    sleep: Callable[[float], None] = time.sleep,
) -> ExplanationResult:
    """Ask the model for one explanation per section. Never raises; failure yields status FAILED for review.

    on_exchange(exchange, messages) is called after every OpenRouter request, so callers can log each call as it happens.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(sections=", ".join(sections))},
        # Compact JSON: indentation was most of the prompt's tokens and cost.
        {"role": "user", "content": json.dumps(facts, default=str, separators=(",", ":"))},
    ]
    errors: List[str] = []
    exchanges: List[Dict[str, Any]] = []
    attempts = 0
    for attempts in range(1, client.config.max_attempts + 1):
        try:
            response = client.chat(messages)
        except LLMError as e:
            errors.append(f"Attempt {attempts}: {e}")
            exchanges.append({"attempt": attempts, "error": str(e), "http_status": e.status, "retryable": e.retryable})
            if on_exchange:
                on_exchange(exchanges[-1], messages)
            if not e.retryable:
                errors.append("Not retried: " + (f"HTTP {e.status}" if e.status else "this error") + " cannot succeed on another attempt.")
                break
            if attempts < client.config.max_attempts:
                sleep(e.retry_after_s if e.retry_after_s is not None else client.config.retry_delay_s * 2 ** (attempts - 1))
            continue
        explanations, problems = validate_explanations(response.content, sections, facts)
        exchanges.append({
            "attempt": attempts,
            "response_id": response.response_id,
            "served_model": response.model,
            "usage": response.usage,
            "raw_content": response.content,
            "response_body": response.raw,
            "response_raw": response.raw_text,
            "validation_problems": problems,
        })
        if on_exchange:
            on_exchange(exchanges[-1], messages)
        if not problems:
            return ExplanationResult(
                "DRAFTED", explanations, attempts, errors, client.config.describe(),
                response.model, response.response_id, messages, client.request_body(messages), exchanges,
            )
        errors.extend(f"Attempt {attempts}: {p}" for p in problems)
    return ExplanationResult(
        "FAILED", {}, attempts, errors, client.config.describe(),
        request_messages=messages, request_body=client.request_body(messages), exchanges=exchanges,
    )
