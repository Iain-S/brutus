"""Additive frozen presentation transform; no live planner changes."""

import copy
import json

IDS = ("compound", "single", "wait")
SEED = 20261122


def ordered_request(base, ids, seed=SEED):
    if (not isinstance(ids, (tuple, list)) or len(ids) != 3
            or any(type(name) is not str for name in ids) or set(ids) != set(IDS)
            or type(seed) is not int or not 0 <= seed < 2**31):
        raise ValueError("Require an exact permutation of the three IDs and a bounded integer seed")
    result = copy.deepcopy(base)
    prompt = json.loads(result["prompt"])
    rows = prompt["native_comparison"]["alternatives"]
    if ([row["id"] for row in rows] != list(IDS)
            or result["format"]["properties"]["candidate_id"]["enum"] != list(IDS)
            or "seed" in result["options"]):
        raise ValueError("Source must retain the complete original unseeded comparison and response domain")
    by_id = {row["id"]: row for row in rows}
    prompt["native_comparison"]["alternatives"] = [by_id[name] for name in ids]
    result["prompt"] = json.dumps(prompt, allow_nan=False)
    result["format"]["properties"]["candidate_id"]["enum"] = list(ids)
    result["options"]["seed"] = seed
    return result


def schedule():
    permutations = (IDS, ("single", "wait", "compound"), ("wait", "compound", "single"),
                    ("compound", "wait", "single"), ("wait", "single", "compound"),
                    ("single", "compound", "wait"))
    conditions = []
    for index, ids in enumerate(permutations):
        for state in ((2, 3) if index % 2 == 0 else (3, 2)):
            conditions.append({"decision_id": state, "order": list(ids), "repeat_control": False})
    for state in (3, 2):
        conditions.append({"decision_id": state, "order": list(IDS), "repeat_control": True})
    return conditions
