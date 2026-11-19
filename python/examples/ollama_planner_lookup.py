"""Experimental pure request/validation helpers; not a live planner command."""
import copy
import hashlib
import json

import ollama_planner as adapter


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def context_fingerprint(context):
    return hashlib.sha256(_canonical(context).encode("utf-8")).hexdigest()


def _body(context, model, tokens, options, verified=False):
    if "reason_first" in options or "verify_comparisons" in options:
        raise ValueError("Lookup stages specify their own response profile")
    return adapter.request_body(context, model, tokens, verify_comparisons=verified, **options)


def _system_prefix(body):
    suffix = "Return required JSON only. Keep the reason under eight words."
    if not body["system"].endswith(suffix):
        raise ValueError("Unexpected base adapter instruction")
    return body["system"][:-len(suffix)]


def lookup_request_body(context, model, tokens, **options):
    reference = adapter.comparison_reference(context)
    body = _body(context, model, tokens, options)
    count = min(2, len(reference))
    body["format"] = {"type": "object", "properties": {
        "decision_id": {"type": "integer", "enum": [context["decision_id"]]},
        "candidate_ids": {"type": "array", "items": {"type": "string", "enum": list(reference)},
                          "minItems": count, "maxItems": count, "uniqueItems": True}},
        "required": ["decision_id", "candidate_ids"], "additionalProperties": False}
    body["system"] = _system_prefix(body) + (
        "Request native facts for two distinct listed alternatives of your own choice "
        "(one if only wait exists). Return decision_id and candidate_ids only. "
        "This is a lookup request, not a final action choice. Every listed alternative may be requested.")
    return body


def validate_lookup(context, value):
    reference = adapter.comparison_reference(context)
    if (type(value) is not dict or set(value) != {"decision_id", "candidate_ids"}
            or type(value["decision_id"]) is not int or value["decision_id"] != context["decision_id"]
            or type(value["candidate_ids"]) is not list
            or len(value["candidate_ids"]) != min(2, len(reference))):
        raise ValueError("Lookup must match the current decision and exact query schema")
    ids = value["candidate_ids"]
    if any(type(key) is not str or key not in reference for key in ids) or len(set(ids)) != len(ids):
        raise ValueError("Lookup must request distinct legal candidate IDs")
    return list(ids)


def materialize_lookup(context, query):
    ids = validate_lookup(context, query)
    reference = adapter.comparison_reference(context)
    # Reuse the production normalization to expand all twenty fields, including unknowns.
    packed = json.loads(adapter.request_body(context, "native-lookup", 1, forecast_format="objects")["prompt"])
    index = packed["candidate_columns"].index("forecast")
    forecasts = {row[0]: row[index] for row in packed["candidates"]}
    native = {c["id"]: c for c in context["candidates"]}
    return {"decision_id": context["decision_id"], "context_sha256": context_fingerprint(context),
            "candidate_ids": ids, "wait_forecast": copy.deepcopy(forecasts["wait"]),
            "alternatives": [{"candidate_id": key, "macro_execution_ticks": native[key].get("ticks"),
                              "net_treasury_outlay": native[key].get("net_treasury_outlay"),
                              "forecast": copy.deepcopy(forecasts[key]),
                              "comparison_facts": copy.deepcopy(reference[key])} for key in ids]}


def _validate_materialized(context, lookup):
    if type(lookup) is not dict:
        raise ValueError("Native lookup must be a provenance-bearing object")
    expected = materialize_lookup(context, {"decision_id": lookup.get("decision_id"),
                                            "candidate_ids": lookup.get("candidate_ids")})
    try:
        same = _canonical(lookup) == _canonical(expected)
    except (ValueError, TypeError):
        same = False
    if not same:
        raise ValueError("Native lookup is stale or differs from the original context")


def lookup_choice_request_body(context, lookup, model, tokens, **options):
    _validate_materialized(context, lookup)
    base = _body(context, model, tokens, options)
    body = _body(context, model, tokens, options, verified=True)
    compact = json.loads(base["prompt"])
    for key in ("candidate_columns", "candidates", "forecast_columns", "forecast_baseline", "forecast_semantics"):
        compact.pop(key, None)
    compact["lookup"] = copy.deepcopy(lookup)
    body["prompt"] = json.dumps(compact)
    ids = lookup["candidate_ids"]
    props = body["format"]["properties"]
    props["candidate_id"]["enum"] = list(ids)
    props["comparisons"]["items"]["properties"]["candidate_id"]["enum"] = list(ids)
    body["system"] = _system_prefix(base) + (
        "You requested the alternatives in lookup.candidate_ids. Native lookup supplies their fully materialized "
        "forecast endpoints, macro durations/outlay and comparison_facts, plus the actual wait forecast. "
        "Return comparisons quoting those comparison_facts exactly, then decision_id and your final candidate_id. "
        "Compare every requested alternative and select one of them. Known zero is zero, not null; unknown is null. "
        "All quotes will be independently checked against the original native context. "
        "Do not invent benefits or write a free-text reason. Return required JSON only.")
    return body


def verified_lookup_choice(context, lookup, value):
    _validate_materialized(context, lookup)
    choice = adapter.verified_comparison_choice(context, value)
    if {row["candidate_id"] for row in value["comparisons"]} != set(lookup["candidate_ids"]):
        raise ValueError("Final comparisons must match the model's own requested alternatives")
    return choice
