#!/usr/bin/env python3
"""Local Ollama API adapter for run_planner.py's JSON command protocol."""

import argparse
import json
import sys
import urllib.request


def comparison_reference(context):
    """Build evidence independently of its packed prompt representation."""
    candidates = context.get("candidates")
    if ("forecast_policy" not in context or type(context.get("decision_id")) is not int
            or type(candidates) is not list or not candidates):
        raise ValueError("Verified comparisons require forecasts and a current decision")
    ids = [c.get("id") if type(c) is dict else None for c in candidates]
    if any(type(key) is not str or not key for key in ids) or len(set(ids)) != len(ids):
        raise ValueError("Verified comparisons require unique legal candidate IDs")
    wait = next((c for c in candidates if c["id"] == "wait"), None)
    if wait is None or type(wait.get("forecast")) is not dict:
        raise ValueError("Verified comparisons require a real wait forecast")
    wait_blocked = wait["forecast"].get("desirability_blocked_houses")
    reference = {}
    for candidate in candidates:
        forecast = candidate.get("forecast", {})
        if type(forecast) is not dict:
            raise ValueError("Verified comparisons require forecast objects")
        row = {"candidate_id": candidate["id"], "macro_ticks": candidate.get("ticks"),
               "forecast_ticks": forecast.get("ticks"), "population": forecast.get("population"),
               "culture": forecast.get("culture"), "prosperity": forecast.get("prosperity"),
               "food_stocks": forecast.get("food_stocks"),
               "blocked_houses": forecast.get("desirability_blocked_houses")}
        if any(value is not None and type(value) is not int for key, value in row.items() if key != "candidate_id"):
            raise ValueError("Verified forecast facts must be integers or unknown (null)")
        blocked = row["blocked_houses"]
        row["blocked_vs_wait"] = blocked - wait_blocked if type(blocked) is type(wait_blocked) is int else None
        reference[candidate["id"]] = row
    return reference


def verified_comparison_choice(context, value):
    reference = comparison_reference(context)
    if (type(value) is not dict or set(value) != {"comparisons", "decision_id", "candidate_id"}
            or type(value["decision_id"]) is not int or value["decision_id"] != context["decision_id"]
            or type(value["candidate_id"]) is not str or value["candidate_id"] not in reference):
        raise ValueError("Verified choice must match the current decision and exact response schema")
    rows = value["comparisons"]
    if type(rows) is not list or len(rows) != min(2, len(reference)):
        raise ValueError("Verified choice must compare two distinct legal alternatives (one if only wait exists)")
    compared = set()
    for row in rows:
        if (type(row) is not dict or type(row.get("candidate_id")) is not str
                or row["candidate_id"] not in reference or row["candidate_id"] in compared):
            raise ValueError("Comparisons must quote distinct listed candidate IDs")
        expected = reference[row["candidate_id"]]
        if set(row) != set(expected):
            raise ValueError("Comparison must contain exactly the required factual fields")
        for key, fact in expected.items():
            if type(row[key]) is not type(fact) or row[key] != fact:
                raise ValueError(f"Comparison {row['candidate_id']} {key}: expected {fact!r}, got {row[key]!r}")
        compared.add(row["candidate_id"])
    if value["candidate_id"] not in compared:
        raise ValueError("Selected candidate must be among the verified comparisons")
    reason = json.dumps({"verified_comparisons": rows})
    if len(reason) > 2000:
        raise ValueError("Verified comparison record exceeds the command reason limit")
    return {"decision_id": value["decision_id"], "candidate_id": value["candidate_id"], "reason": reason}


def unique_response_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate response key: " + key)
        result[key] = value
    return result


def request_body(context, model, tokens, temperature=0.0, top_p=None, top_k=None, min_p=None,
                 forecast_format="rows", context_tokens=4096, reason_first=False, verify_comparisons=False):
    schema = {"type": "object", "properties": {
        "decision_id": {"type": "integer", "enum": [context["decision_id"]]},
        "candidate_id": {"type": "string", "enum": [c["id"] for c in context["candidates"]]},
        "reason": {"type": "string"}},
        "required": ["decision_id", "candidate_id", "reason"], "additionalProperties": False}
    instruction = "Return required JSON only. Keep the reason under eight words."
    if reason_first:
        keys = ["reason", "decision_id", "candidate_id"]
        schema["properties"] = {key: schema["properties"][key] for key in keys}
        schema["required"] = keys
        instruction = ("In reason, briefly compare at least two listed candidates using the reported forecast values. "
                       "Give this comparison before selecting candidate_id. Return required JSON only; "
                       "keep the reason under 100 words.")
    if verify_comparisons:
        if reason_first:
            raise ValueError("Verified comparisons and reason-first are mutually exclusive profiles")
        reference = comparison_reference(context)
        fields = {key: {"type": ["integer", "null"]} for key in next(iter(reference.values())) if key != "candidate_id"}
        props = {"candidate_id": schema["properties"]["candidate_id"], **fields}
        count = min(2, len(reference))
        schema["properties"] = {"comparisons": {"type": "array", "minItems": count, "maxItems": count,
            "items": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}},
            "decision_id": schema["properties"]["decision_id"], "candidate_id": schema["properties"]["candidate_id"]}
        schema["required"] = list(schema["properties"])
        instruction = (
            "Before selecting candidate_id, quote comparisons for two distinct listed alternatives of your choice "
            "(one if only wait exists). Select one of those compared. Return required JSON only, no free-text reason. "
            "macro_ticks quotes candidate ticks, not execution cadence; forecast_ticks quotes forecast ticks. "
            "population, culture, prosperity and food_stocks are absolute forecast endpoints; blocked_houses quotes "
            "forecast desirability_blocked_houses. blocked_vs_wait is that count minus wait's forecast count. "
            "Omitted forecast overrides equal the baseline, not zero. Quote null for unknown facts or differences. "
            "Every quoted fact will be checked against the native forecast; do not invent improvements.")
    state = context.get("state", {})
    aliases = {"population": "population_total", "housing_capacity": "buildings_housing_capacity",
               "treasury": "finance_treasury", "sentiment": "population_sentiment",
               "unemployed_workers": "labor_workers_available", "job_vacancies": "labor_workers_needed",
               "employed_workers": "labor_workers_employed",
               "food_stocks": "resources_food_stocks"}
    compact = {"decision_id": context["decision_id"], "objective": context.get("objective"),
               "remaining_ticks": context.get("remaining_ticks"),
               "elapsed_ticks": context.get("elapsed_ticks"), "ticks_per_month": 800,
               "minimum_decision_interval": context.get("minimum_decision_interval", 0),
               "state": {short: state[key] for short, key in aliases.items() if key in state},
               "ratings": {key.removeprefix("ratings_"): value for key, value in state.items() if key.startswith("ratings_")},
               "goals": {key.removeprefix("victory_"): value for key, value in state.items() if key.endswith("_goal")},
               "services": context.get("services"),
               "food_supply": context.get("food_supply"),
               "candidate_columns": ["candidate_id", "ticks", "net_outlay", "benefit"],
               "candidates": [[c["id"], c.get("ticks"), c.get("net_treasury_outlay", 0), c.get("benefit", "")]
                              for c in context["candidates"]],
               "last_status": (context.get("last_result") or {}).get("status"),
               "last_action": (context.get("last_result") or {}).get("candidate_id"),
               "validation_errors": context.get("validation_errors", [])}
    if "imperial" in context:
        compact["imperial"] = context["imperial"]
        compact["candidate_columns"].append("personal_savings_cost")
        for row, candidate in zip(compact["candidates"], context["candidates"]):
            row.append(candidate.get("personal_savings_cost", 0))
    if "water_supply" in context:
        compact["water_supply"] = context["water_supply"]
    if "housing" in context:
        compact["housing"] = context["housing"]
    if "finance" in context:
        compact["finance"] = context["finance"]
    if "forecast_policy" in context:
        columns = ["ticks", "status", "population", "food_stocks", "residents_with_food",
                   "health", "farm_workers", "treasury", "culture", "granary_food_units", "market_food_units",
                   "favor", "personal_savings", "prosperity", "residents_with_fountain",
                   "desirability_blocked_houses", "native_cached_prosperity_cap", "max_house_level",
                   "covered_population", "yearly_collected_denarii"]
        compact["forecast_policy"] = context["forecast_policy"]
        if forecast_format in ("rows", "overrides"):
            compact["forecast_columns"] = columns
        compact["candidate_columns"].append("forecast")
        for row, candidate in zip(compact["candidates"], context["candidates"]):
            forecast = candidate.get("forecast", {})
            values = {key: forecast.get(key) for key in columns}
            row.append(values if forecast_format == "objects" else list(values.values()))
    if "recent_outcomes" in context:
        metrics = ["population", "residents_with_food", "health", "culture", "granary_food_units",
                   "market_food_units", "house_food_units", "treasury"]
        compact["recent_columns"] = ["candidate_id", "ticks", "status"] + [key + "_delta" for key in metrics]
        compact["recent_outcomes"] = [[r["candidate_id"], r["ticks"], r["status"],
                                       *[r["delta"][key] for key in metrics]]
                                      for r in context["recent_outcomes"][-4:]]
    if forecast_format == "overrides" and "forecast_columns" in compact:
        columns = compact.pop("forecast_columns")
        index = compact["candidate_columns"].index("forecast")
        wait = next((row for row in compact["candidates"] if row[0] == "wait"), None)
        baseline = dict(zip(columns, wait[index])) if wait is not None else {}
        compact["forecast_baseline"] = {"candidate_id": "wait" if wait is not None else None,
                                        "forecast": baseline}
        compact["forecast_semantics"] = (
            "Absolute values override forecast_baseline.forecast; omitted fields equal baseline, "
            "not zero. Null means unknown. Each candidate keeps its own ticks and status.")
        for row in compact["candidates"]:
            values = dict(zip(columns, row[index]))
            # Preserve scalar type and JSON representation, including signed float zero.
            row[index] = {key: value for key, value in values.items() if key not in baseline
                          or type(value) is not type(baseline[key])
                          or json.dumps(value) != json.dumps(baseline[key])}
    options = {"num_predict": tokens, "num_ctx": context_tokens, "temperature": temperature}
    for name, value in (("top_p", top_p), ("top_k", top_k), ("min_p", min_p)):
        if value is not None:
            options[name] = value
    return {"model": model, "stream": False, "think": False, "format": schema,
            "system": "You run Caesar III. Choose a candidate to advance goals without overspending. "
                      "Immigrants cannot arrive without houses. Workers come from residents, not empty lots. "
                      "Building takes only a few ticks; waiting after housing lets immigrants and services act. "
                      "Farms produce food, granaries store it, markets deliver it. Temples are buildings, not housing districts. "
                      "Theaters need performers from actor colonies; schools and libraries provide education. "
                      "Reported food_stocks is filtered granary stock, not another inventory to add. "
                      "Recent deltas include all activity during each cycle, not just construction. "
                      "Imperial gifts spend personal savings, not city treasury; repeated gifts have diminishing returns. "
                      "Reservoirs need nearby water or midpoint-connected aqueducts. Fountains need reservoir range and staff. "
                      "Housing desirability uses the current model threshold; upgrade goods/services use the next model. "
                      "Passing these checks does not guarantee evolution: population, space, merging and timing also apply. "
                      "Gardens affect desirability through normal engine updates. "
                      "Tax income requires collector coverage from staffed road-connected forums or senate. "
                      "Monthly tax bases are not denarii; yearly collected denarii reset each year. "
                      "Finance overviews/estimates are cached, not guaranteed future income. " + instruction,
            "prompt": json.dumps(compact),
            "options": options}


def validate_inference_result(result, options):
    if result.get("error") or not result.get("done") or result.get("done_reason") == "length":
        raise RuntimeError("Local inference failed or exhausted its token budget")
    prompt_tokens = result.get("prompt_eval_count")
    if type(prompt_tokens) is not int or prompt_tokens <= 0:
        raise RuntimeError("Local inference lacks valid prompt-token telemetry")
    if prompt_tokens + options["num_predict"] + 128 > options["num_ctx"]:
        raise RuntimeError("Local inference lacks context headroom; possible input truncation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="An already installed Ollama model")
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--timeout", type=int, default=110)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--min-p", type=float)
    parser.add_argument("--forecast-format", choices=("rows", "objects", "overrides"), default="rows",
                        help="Forecast representation; overrides losslessly factor out the wait projection")
    parser.add_argument("--context-tokens", type=int, default=4096,
                        help="Ollama context capacity (2048..16384); larger budgets may use more memory/time")
    parser.add_argument("--reason-first", action="store_true",
                        help="Opt in to a brief forecast comparison before choosing; reasons remain unverified")
    parser.add_argument("--verify-comparisons", action="store_true",
                        help="Require exact quoted forecast evidence before accepting a model choice")
    args = parser.parse_args()
    if args.verify_comparisons and args.reason_first:
        parser.error("--verify-comparisons and --reason-first are mutually exclusive")
    if not 32 <= args.max_tokens <= 1024 or not 1 <= args.timeout <= 290:
        parser.error("max-tokens must be 32..1024 and timeout 1..290")
    if not 2048 <= args.context_tokens <= 16384:
        parser.error("context-tokens must be 2048..16384")
    if (not 0 <= args.temperature <= 2 or (args.top_p is not None and not 0 < args.top_p <= 1)
            or (args.top_k is not None and not 0 <= args.top_k <= 1000)
            or (args.min_p is not None and not 0 <= args.min_p <= 1)):
        parser.error("Invalid sampling parameters: temperature 0..2, top-p (0,1], top-k 0..1000, min-p 0..1")
    tag = args.model.rsplit("/", 1)[-1].lower()
    if tag.startswith("qwen3:") and "-thinking" in tag:
        parser.error("Explicit Qwen3 thinking-only tags are incompatible with this non-thinking adapter; use an instruct variant")
    context = json.load(sys.stdin)
    body = request_body(context, args.model, args.max_tokens, args.temperature, args.top_p, args.top_k, args.min_p,
                        forecast_format=args.forecast_format, context_tokens=args.context_tokens,
                        reason_first=args.reason_first, verify_comparisons=args.verify_comparisons)
    request = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                     json.dumps(body).encode("utf-8"),
                                     {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=args.timeout) as response:
        result = json.load(response)
    metadata = {**{key: result.get(key) for key in ("model", "total_duration", "load_duration",
                                                  "prompt_eval_count", "eval_count")},
                "options": body["options"], "forecast_format": args.forecast_format,
                "reason_first": args.reason_first}
    if args.verify_comparisons:
        metadata.update(verify_comparisons=True, comparison_validation="not_run")
        try:
            validate_inference_result(result, body["options"])
            metadata["comparison_validation"] = "rejected"
            if type(result.get("response")) is not str:
                raise ValueError("Local inference response must be a JSON string")
            value = json.loads(result["response"], object_pairs_hook=unique_response_object)
            choice = verified_comparison_choice(context, value)
            metadata.update(comparison_validation="accepted", comparisons=value["comparisons"])
        except (ValueError, RuntimeError) as error:
            metadata["validation_error"] = str(error)[:300]
            raise
        finally:
            print(json.dumps(metadata), file=sys.stderr)
    else:
        print(json.dumps(metadata), file=sys.stderr)
        validate_inference_result(result, body["options"])
        choice = json.loads(result["response"])
    print(json.dumps(choice))


if __name__ == "__main__":
    main()
