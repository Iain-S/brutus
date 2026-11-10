#!/usr/bin/env python3
"""Local Ollama API adapter for run_planner.py's JSON command protocol."""

import argparse
import json
import sys
import urllib.request


def request_body(context, model, tokens, temperature=0.0, top_p=None, top_k=None, min_p=None,
                 forecast_format="rows", context_tokens=4096):
    schema = {"type": "object", "properties": {
        "decision_id": {"type": "integer", "enum": [context["decision_id"]]},
        "candidate_id": {"type": "string", "enum": [c["id"] for c in context["candidates"]]},
        "reason": {"type": "string"}},
        "required": ["decision_id", "candidate_id", "reason"], "additionalProperties": False}
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
    if "forecast_policy" in context:
        columns = ["ticks", "status", "population", "food_stocks", "residents_with_food",
                   "health", "farm_workers", "treasury", "culture", "granary_food_units", "market_food_units"]
        compact["forecast_policy"] = context["forecast_policy"]
        if forecast_format == "rows":
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
                      "Return required JSON only. Keep the reason under eight words.",
            "prompt": json.dumps(compact),
            "options": options}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="An already installed Ollama model")
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--timeout", type=int, default=110)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--min-p", type=float)
    parser.add_argument("--forecast-format", choices=("rows", "objects"), default="rows",
                        help="Candidate forecast representation; objects use more context tokens")
    parser.add_argument("--context-tokens", type=int, default=4096,
                        help="Ollama context capacity (2048..16384); larger budgets may use more memory/time")
    args = parser.parse_args()
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
                        forecast_format=args.forecast_format, context_tokens=args.context_tokens)
    request = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                     json.dumps(body).encode("utf-8"),
                                     {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=args.timeout) as response:
        result = json.load(response)
    if result.get("error") or not result.get("done") or result.get("done_reason") == "length":
        raise RuntimeError("Local inference failed or exhausted its token budget")
    choice = json.loads(result["response"])
    print(json.dumps(choice))
    print(json.dumps({**{key: result.get(key) for key in ("model", "total_duration", "load_duration",
                                                        "prompt_eval_count", "eval_count")},
                      "options": body["options"], "forecast_format": args.forecast_format}), file=sys.stderr)


if __name__ == "__main__":
    main()
