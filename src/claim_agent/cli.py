"""Command-line entry point: assess sample claims and print the report and tool call log.

    python -m claim_agent.cli CLM-APP-001 [CLM-REJ-001 ...] [--all] [--no-llm] [--format text|md|json | --md | --json] [--no-color] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from claim_agent import llm
from claim_agent.envfile import load_env_file
from claim_agent.fixtures import FixtureStore
from claim_agent.orchestrator import assess_claim
from claim_agent.render import render_audit, render_report, render_text


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Initial claim assessment (fictional sample data).")
    parser.add_argument("claim_ids", nargs="*", help="Claim IDs to assess.")
    parser.add_argument("--all", action="store_true", help="Assess every sample claim.")
    parser.add_argument("--no-llm", action="store_true", help="Skip the OpenRouter explanations (offline runs and tests). By default every assessment calls OpenRouter.")
    parser.add_argument("--llm", action="store_true", help=argparse.SUPPRESS)  # kept for old commands; the LLM call is now the default
    parser.add_argument("--format", choices=("text", "md", "json"), default="text", help="Output format (default: text, for terminals).")
    shortcut = parser.add_mutually_exclusive_group()
    shortcut.add_argument("--md", action="store_true", help="Same as --format md: the six-section Markdown report.")
    shortcut.add_argument("--json", action="store_true", help="Same as --format json.")
    parser.add_argument("--no-llm-payload", action="store_true", help="Hide the full OpenRouter request/response messages (shown by default).")
    parser.add_argument("--llm-raw", action="store_true", help="Also print the full raw OpenRouter request and response bodies in the tool call log.")
    parser.add_argument("--no-color", action="store_true", help="Disable colors (also disabled when piped or NO_COLOR is set).")
    parser.add_argument("--out", type=Path, help="Also write <claim>.md and <claim>.json files to this directory.")
    parser.add_argument("--env-file", type=Path, help="Read OPENROUTER_API_KEY / OPENROUTER_MODEL from this file (default: .env in the project root).")
    args = parser.parse_args(argv)

    store = FixtureStore.load()
    claim_ids = sorted(store.claims) if args.all else args.claim_ids
    if not claim_ids:
        parser.error("give claim IDs or --all")

    client = None
    if not args.no_llm:
        load_env_file(args.env_file)
        try:
            client = llm.OpenRouterClient(llm.LLMConfig.from_env())
        except llm.LLMError as e:
            sys.exit(f"Cannot call OpenRouter: {e} Put it in .env (see .env.example) or export it in your shell, or run with --no-llm.")

    fmt = "json" if args.json else "md" if args.md else args.format
    color = sys.stdout.isatty() and not args.no_color and "NO_COLOR" not in os.environ
    width = shutil.get_terminal_size((100, 24)).columns

    for claim_id in claim_ids:
        assessment = assess_claim(claim_id, store, client)
        payload = {"report": assessment.report, "audit": assessment.audit.to_dict()}
        markdown = render_report(assessment.report) + "\n" + render_audit(assessment.audit, show_llm_payload=not args.no_llm_payload, show_llm_raw=args.llm_raw)
        if fmt == "json":
            print(json.dumps(payload, indent=2))
        elif fmt == "md":
            print(markdown)
        else:
            print(render_text(assessment.report, assessment.audit, color=color, width=width, show_llm_payload=not args.no_llm_payload, show_llm_raw=args.llm_raw))
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / f"{claim_id}.md").write_text(markdown)
            (args.out / f"{claim_id}.json").write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
