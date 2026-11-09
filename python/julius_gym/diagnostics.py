"""Read-only summaries and bounded observations, not a strategy or reward function."""


def food_totals(supply):
    if supply["schema_version"] != 1 or supply["units_per_load"] != 100:
        raise ValueError("Unsupported food diagnostics schema or units")
    totals = {"granary_food_units": 0, "market_food_units": 0, "granary_free_units": 0}
    for row in supply["buildings"]:
        if row["kind"] == "granary":
            totals["granary_food_units"] += sum(row["food_units"])
            totals["granary_free_units"] += row["free_space_units"]
        elif row["kind"] == "market":
            totals["market_food_units"] += sum(row["food_units"])
        elif row["kind"] != "farm":
            raise ValueError("Unknown food diagnostics building kind")
    return totals


def food_summary(supply, buildings):
    result = {**food_totals(supply), "units_per_load": supply["units_per_load"],
              "house_food_units": sum(b["food"] for b in buildings),
              "scope": "granary/market/house inventories; excludes cargo/warehouses; farm progress is work",
              "row_columns": ["id", "kind", "x", "y", "workers", "workers_required", "road_access",
                              "food_units", "free_space_units", "progress_points", "progress_max"],
              "rows": [], "building_counts": {}}
    for kind in ("farm", "granary", "market"):
        rows = sorted((r for r in supply["buildings"] if r["kind"] == kind), key=lambda r: r["id"])
        result["building_counts"][kind] = len(rows)
        for row in rows[:4]:
            result["rows"].append([row["id"], kind, row["x"], row["y"], row["workers"],
                row["workers_required"], row["road_access"],
                sum(row["food_units"]) if kind != "farm" else None,
                row["free_space_units"] if kind == "granary" else None,
                row["progress_points"] if kind == "farm" else None,
                row["progress_max"] if kind == "farm" else None])
    result["rows_total"] = len(supply["buildings"])
    result["rows_omitted"] = result["rows_total"] - len(result["rows"])
    return result


def capture_outcome(env, observation):
    totals = food_totals(env.get_food_supply())
    buildings = env.get_buildings()
    return {"population": int(observation["population_total"].item()),
            "culture": int(observation["ratings_culture"].item()),
            "treasury": int(observation["finance_treasury"].item()),
            "health": env.get_population_info()["health"],
            "residents_with_food": sum(b["population"] for b in buildings if b["food"] > 0),
            "house_food_units": sum(b["food"] for b in buildings),
            "granary_food_units": totals["granary_food_units"],
            "market_food_units": totals["market_food_units"]}


def record_outcome(history, candidate_id, status, ticks, before, after):
    entry = {"candidate_id": candidate_id, "status": status, "ticks": ticks,
             "delta": {key: after[key] - value for key, value in before.items()}}
    return (history + [entry])[-4:]
