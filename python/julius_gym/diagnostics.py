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


def water_summary(supply, buildings):
    rows = supply["buildings"]
    result = {"reservoir_radius": supply["reservoir_radius"], "fountain_radius": supply["fountain_radius"],
              "scope": "cached native supply; staffing and supply are separate observations",
              "aqueduct_tiles": len(supply["aqueducts"]),
              "wet_aqueduct_tiles": sum(bool(r["water"]) for r in supply["aqueducts"]),
              "residents_with_fountain": sum(b["population"] for b in buildings if b["fountain"]),
              "max_house_level": max((b["level"] for b in buildings), default=-1),
              "row_columns": ["id", "kind", "x", "y", "workers", "water_access", "near_water", "in_reservoir_range"],
              "rows": [], "rows_total": len(rows)}
    for kind in ("reservoir", "fountain", "well"):
        group = sorted((r for r in rows if r["kind"] == kind), key=lambda r: r["id"])
        result[kind + "s"] = len(group)
        if kind != "well":
            result["supplied_" + kind + "s"] = sum(bool(r["water_access"]) for r in group)
        if kind == "fountain":
            result["staffed_fountains"] = sum(r["workers"] > 0 for r in group)
        result["rows"].extend([[r.get(key) for key in result["row_columns"]] for r in group[:4]])
    result["rows_omitted"] = len(rows) - len(result["rows"])
    return result


def housing_totals(state):
    houses = state["houses"]
    occupied = [r for r in houses if r["population"] > 0]
    with_next = [r for r in occupied if r["next_level"] is not None]
    return {"occupied_houses": len(occupied),
            "desirability_blocked_houses": sum(not r["desirability_allows_upgrade"] for r in with_next),
            "current_goods_services_failed_houses": sum(not r["current_goods_services_pass"] for r in occupied),
            "next_goods_services_failed_houses": sum(not r["next_goods_services_pass"] for r in with_next),
            "native_cached_prosperity_cap": state["native_cached_prosperity_cap"],
            "max_house_level": max((r["level"] for r in houses), default=-1)}


def housing_summary(state):
    houses = state["houses"]
    levels = {level for r in houses for level in (r["level"], r["next_level"]) if level is not None}
    columns = ["id", "x", "y", "population", "level", "next_level", "size", "house_size", "merged",
               "desirability_cached", "tile_desirability_cached",
               "desirability_allows_upgrade", "current_goods_services_pass", "next_goods_services_pass",
               "no_space_to_expand_cached", "devolve_delay_cached",
               "well", "fountain", "food_types_checked", "entertainment", "education", "num_gods",
               "barber", "bathhouse", "health"]
    result = {**housing_totals(state), "scope": "independent cached conditions, not guaranteed upgrades; space/merging/timing also apply",
              "garden_model": state["garden_model"], "multiple_wine_available": state["multiple_wine_available"],
              "models": [m for m in state["models"] if m["level"] in levels],
              "level_counts": {level: sum(r["level"] == level for r in houses)
                               for level in sorted({r["level"] for r in houses})},
              "row_columns": columns + ["goods_inventory_units"],
              "goods_inventory_order": ["pottery", "oil", "furniture", "wine"], "rows": [],
              "rows_total": len(houses)}
    for row in sorted(houses, key=lambda r: r["id"])[:8]:
        result["rows"].append([row.get(key) for key in columns] + [[row["inventory_units"][i] for i in (7, 5, 6, 4)]])
    result["rows_omitted"] = len(houses) - len(result["rows"])
    return result


def finance_summary(state):
    """Keep native accounting scopes; bound collector detail without dropping totals."""
    result = {key: value for key, value in state.items() if key not in ("houses", "collectors")}
    collectors = sorted(state["collectors"], key=lambda row: row["id"])
    result.update(collectors=collectors[:8], collectors_total=len(collectors),
                  collectors_omitted=max(0, len(collectors) - 8))
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
