"""Paid Tarraco taxation capability; no injected money, staffing or coverage.

This is an integration fixture, not a planner policy. All committed actions
are logged for examples/replay_run.py; snapshot previews are rolled back.
"""

import argparse
import ctypes
import json
import sys

from julius_gym import JuliusEnv
from julius_gym.baseline import building_plan, connected_roads, exclude_hazard, starter_plan
from julius_gym.env import ActionType as A
from julius_gym.planner import (
    Candidate, decision_context, execute, fingerprint, food_supply_plan,
    preview_candidate, proposals,
)
from julius_gym.run_artifacts import RunArtifacts


MAX_TICKS = 12000
FORUM_TYPE = 86


def check_finance(state):
    """Check current coverage independently of cached native overview totals."""
    for key in ("treasury", "tax_percentage", "wages", "wages_rome",
                "yearly_collected_denarii", "wages_so_far", "interest_so_far",
                "salary_so_far", "covered_population", "occupied_population"):
        assert type(state[key]) is int, (key, state[key])
    assert 0 <= state["tax_percentage"] <= 25, state
    assert 0 <= state["wages"] <= 50, state
    for key in ("yearly_collected_denarii", "wages_so_far", "interest_so_far", "salary_so_far"):
        assert state[key] >= 0, (key, state[key])
    houses = state["houses"]
    assert len({h["id"] for h in houses}) == len(houses), houses
    assert state["occupied_population"] == sum(h["population"] for h in houses if h["population"] > 0), state
    assert state["covered_population"] == sum(
        h["population"] for h in houses if h["population"] > 0 and h["tax_coverage"] > 0), state
    for collector in state["collectors"]:
        for key in ("id", "type", "x", "y", "workers", "road_access_cached",
                    "road_access_native", "houses_covered_activity_cached"):
            assert key in collector, (key, collector)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    artifacts = RunArtifacts("finance-capability", configuration={"max_ticks": MAX_TICKS})
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path,
                    campaign_rank=3, max_ticks=MAX_TICKS)
    try:
        observation, info = env.reset()
        artifacts.ready = True
        mission = info["mission"]
        artifacts.metadata["mission"] = mission
        assert A.COUNT == 61 and A.BUILD_FORUM == 31
        assert (A.ADJUST_TAX_UP, A.ADJUST_TAX_DOWN, A.ADJUST_WAGES_UP, A.ADJUST_WAGES_DOWN) == (1, 2, 3, 4)
        initial = env.get_finance_state()
        check_finance(initial)
        initial_fingerprint = fingerprint(env, observation)
        assert env.get_finance_state() == initial
        assert fingerprint(env, observation) == initial_fingerprint

        # get_finance_state() establishes the ctypes signature before raw calls.
        query = env.lib.julius_env_get_finance_state
        tiny = ctypes.create_string_buffer(b"X" * 16)
        assert query(env.env_handle, tiny, 4) == -1
        assert tiny.raw[4:] == b"X" * 12 + b"\0", tiny.raw
        assert query(None, tiny, len(tiny)) == -1
        assert query(env.env_handle, None, len(tiny)) == -1
        assert query(env.env_handle, tiny, 0) == -1
        assert query(env.env_handle, tiny, -1) == -1
        assert env.get_finance_state() == initial
        assert fingerprint(env, observation) == initial_fingerprint
        assert initial["yearly_collected_denarii"] == 0, initial
        assert not initial["collectors"], initial

        ticks = 0
        with artifacts.log.open("w", encoding="utf-8") as log:
            def apply(name, actions):
                nonlocal observation, ticks
                assert actions and len(actions) < MAX_TICKS - ticks, (name, ticks)
                candidate = Candidate(name, actions, fingerprint(env, observation), {})
                observation, result, terminated, truncated = execute(
                    env, candidate, observation, MAX_TICKS - ticks)
                for step in result["steps"]:
                    ticks += 1
                    log.write(json.dumps({**step, "tick": ticks, "phase": name}) + "\n")
                log.flush()
                assert result["status"] == "completed" and not terminated and not truncated, result
                return result

            def pure_state():
                before = fingerprint(env, observation)
                buildings = env.get_buildings()
                state = env.get_finance_state()
                check_finance(state)
                assert env.get_finance_state() == state
                assert env.get_buildings() == buildings
                assert fingerprint(env, observation) == before
                return state

            def preview_exact(candidate):
                before = pure_state()
                before_buildings = env.get_buildings()
                before_fingerprint = fingerprint(env, observation)
                result, _, forecast = preview_candidate(
                    env, candidate, observation, MAX_TICKS - ticks, forecast_ticks=800)
                assert result["status"] == "completed", result
                assert forecast is not None
                assert env.get_finance_state() == before
                assert env.get_buildings() == before_buildings
                assert fingerprint(env, observation) == before_fingerprint

            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, mission["earthquake"], 14)
            apply("housing", starter_plan(terrain, buildings, width, height, mission["entry"]))
            apply("food", food_supply_plan(env, mission, 14))
            home = next((b["x"], b["y"]) for b in env.get_buildings() if b["level"] >= 0)
            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, mission["earthquake"], 14)
            apply("religion", building_plan(terrain, buildings, width, height,
                                           mission["entry"], A.BUILD_TEMPLE_SMALL, 2, anchor=home))
            apply("observe_without_collectors", [(A.NONE, 0, 0)] * 1600)
            before_forum = pure_state()
            assert before_forum["occupied_population"] > 0, before_forum
            assert not before_forum["collectors"], before_forum
            assert before_forum["covered_population"] == 0, before_forum
            assert before_forum["yearly_collected_denarii"] == 0, before_forum
            assert before_forum["tax_percentage"] > 0, before_forum

            # Validate ordinary optional candidates, not a mandatory build policy.
            before_context = fingerprint(env, observation)
            context, candidates = decision_context(env, observation, mission, 0, MAX_TICKS - ticks)
            assert "finance" in context, context.keys()
            assert env.get_finance_state() == before_forum
            assert fingerprint(env, observation) == before_context
            controls = (("adjust_tax_up", A.ADJUST_TAX_UP, "tax_percentage", 1),
                        ("adjust_tax_down", A.ADJUST_TAX_DOWN, "tax_percentage", -1),
                        ("adjust_wages_up", A.ADJUST_WAGES_UP, "wages", 1),
                        ("adjust_wages_down", A.ADJUST_WAGES_DOWN, "wages", -1))
            assert all(name in candidates for name, _, _, _ in controls), candidates.keys()
            forums = [c for name, c in candidates.items() if name.startswith("add_forum_district_")]
            assert forums, context["unavailable"]
            forum = forums[0]
            assert sum(kind == A.BUILD_FORUM for kind, _, _ in forum.actions) == 1, forum
            assert forum.actions[-1][0] == A.BUILD_FORUM, forum
            preview_exact(forum)
            apply(forum.id, forum.actions)
            # New buildings enter the active query only at the native state-update tick.
            apply("activate_forum", [(A.NONE, 0, 0)] * 50)
            target = forum.actions[-1][1:]
            placed = next(b for b in env.get_buildings()
                          if b["type"] == FORUM_TYPE and (b["x"], b["y"]) == tuple(target))
            assert placed["size"] == 2, placed
            forum_id = placed["id"]

            def check_forum_connection():
                terrain, _, width, height = env.get_map_data()
                roads = connected_roads(terrain, width, height, mission["entry"])
                x, y, size = placed["x"], placed["y"], placed["size"]
                perimeter = ([(x + i, y - 1) for i in range(size)]
                             + [(x + i, y + size) for i in range(size)]
                             + [(x - 1, y + i) for i in range(size)]
                             + [(x + size, y + i) for i in range(size)])
                assert any(tile in roads for tile in perimeter), (placed, perimeter)

            check_forum_connection()

            while True:
                collected = pure_state()
                staffed = any(c["id"] == forum_id and c["type"] == FORUM_TYPE
                              and c["workers"] > 0 and c["road_access_native"]
                              for c in collected["collectors"])
                if staffed and collected["covered_population"] > 0 and collected["yearly_collected_denarii"] > 0:
                    break
                remaining = MAX_TICKS - ticks - 1
                assert remaining > 0, {"ticks": ticks, "finance": collected}
                apply("observe_native_collection", [(A.NONE, 0, 0)] * min(400, remaining))
            collection_ticks = ticks
            check_forum_connection()
            assert any(h["population"] > 0 and h["tax_coverage"] > 0 for h in collected["houses"]), collected

            # Check each native +/-1 effect, then restore the original rates via
            # ordinary actions. Do not infer profit from these ticking ledgers.
            for name, kind, field, delta in controls:
                actions = dict(proposals(env, mission, 14))[name]()
                assert actions == [(kind, 0, 0)], (name, actions)
                candidate = Candidate(name, actions, fingerprint(env, observation), {})
                preview_exact(candidate)
                before = pure_state()
                apply(name, actions)
                after = pure_state()
                assert after[field] == before[field] + delta, (name, before, after)
                unchanged = "wages" if field == "tax_percentage" else "tax_percentage"
                assert after[unchanged] == before[unchanged], (name, before, after)
            final = pure_state()
            assert final["tax_percentage"] == collected["tax_percentage"], final
            assert final["wages"] == collected["wages"], final
            assert final["wages_so_far"] > 0, final

        summary = {"ticks": ticks, "population": int(observation["population_total"].item()),
                   "won": env.get_victory_state() == 1, "verified_native_taxes": True,
                   "verified_finance_preview_rollback": True, "forum_id": forum_id,
                   "collection_observed_tick": collection_ticks,
                   "pre_forum_occupied_population": before_forum["occupied_population"],
                   "pre_forum_collected_denarii": before_forum["yearly_collected_denarii"],
                   "covered_population_at_collection": collected["covered_population"],
                   "yearly_collected_denarii_at_collection": collected["yearly_collected_denarii"],
                   "tax_percentage": final["tax_percentage"], "wages": final["wages"],
                   "wages_rome": final["wages_rome"], "treasury": final["treasury"],
                   "wages_so_far": final["wages_so_far"], "interest_so_far": final["interest_so_far"],
                   "salary_so_far": final["salary_so_far"],
                   "ledger_scope": "native current-year counters; wages and governor salary are separate expenses; not net profit"}
        print(json.dumps(summary))
    finally:
        error = sys.exc_info()[1]
        try:
            artifacts.finish(env, locals().get("summary"), error)
        finally:
            env.close()


if __name__ == "__main__":
    main()
