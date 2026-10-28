"""Shared test setup: fixture store, contexts, and store variants for failure cases."""

import copy
import dataclasses

from claim_agent.context import create_assessment_context
from claim_agent.fixtures import FixtureStore

STORE = FixtureStore.load()


def context_for(claim_id, store=STORE):
    """Context with no verified facts: only what the claimant reported."""
    return create_assessment_context(claim_id, store)


def verified_context(claim_id, store=STORE):
    """Context with facts recorded from each submitted document whose detected type matches its declared type.

    Mirrors what the orchestrator does after document review, so each tool can be tested in isolation.
    """
    ctx = context_for(claim_id, store)
    for ref in ctx.claim["documents"]:
        doc = store.document(ref["document_id"])
        if doc is None or doc["detected_type"] != ref["declared_type"]:
            continue
        for f in doc["extracted_facts"]:
            ctx.record_fact(f["fact"], f["value"], doc["document_id"], f["location"])
    return ctx


def store_with_claim_changes(claim_id, **changes):
    claims = copy.deepcopy(STORE.claims)
    claims[claim_id].update(changes)
    return dataclasses.replace(STORE, claims=claims)


def store_with_balance(policy_id, **changes):
    balances = copy.deepcopy(STORE.balances)
    for b in balances:
        if b["policy_id"] == policy_id:
            b.update(changes)
    return dataclasses.replace(STORE, balances=balances)


def store_without_balances():
    return dataclasses.replace(STORE, balances=[])


def store_without_policy(policy_id):
    policies = {k: v for k, v in STORE.policies.items() if k != policy_id}
    return dataclasses.replace(STORE, policies=policies)


def store_with_document_fact(document_id, fact_name, value):
    documents = copy.deepcopy(STORE.documents)
    for f in documents[document_id]["extracted_facts"]:
        if f["fact"] == fact_name:
            f["value"] = value
    return dataclasses.replace(STORE, documents=documents)


def store_with_member_changes(policy_id, **changes):
    policies = copy.deepcopy(STORE.policies)
    policies[policy_id]["members"][0].update(changes)
    return dataclasses.replace(STORE, policies=policies)
