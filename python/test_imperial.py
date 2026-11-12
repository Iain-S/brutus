"""Native imperial actions funded through ordinary salary; no injected money/favor."""

import argparse
import ctypes
import json
import sys

from julius_gym import JuliusEnv
from julius_gym.env import ActionType as A
from julius_gym.planner import Candidate, decision_context, fingerprint, preview_candidate
from julius_gym.run_artifacts import RunArtifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    artifacts = RunArtifacts("imperial-capability", configuration={"max_ticks": 40000})
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=40000)
    try:
        observation, info = env.reset()
        artifacts.ready = True
        artifacts.metadata["mission"] = info["mission"]
        initial = env.get_imperial_state()
        assert initial["payment_source"] == "personal_savings"
        assert A.BUILD_LOW_BRIDGE == 55 and A.SEND_MODEST_GIFT == 56 and A.COUNT >= 59
        before = fingerprint(env, observation)
        assert env.get_imperial_state() == initial and fingerprint(env, observation) == before
        query = env.lib.julius_env_get_imperial_state
        tiny = ctypes.create_string_buffer(b"X" * 16)
        assert query(env.env_handle, tiny, 4) == -1 and tiny.raw[4:5] == b"X"
        assert query(None, tiny, len(tiny)) == -1
        assert query(env.env_handle, None, 20) == -1
        ticks = 0
        with artifacts.log.open("w", encoding="utf-8") as log:
            def step(action):
                nonlocal ticks, observation
                observation, reward, terminated, truncated, result = env.step_at(*action)
                ticks += 1
                log.write(json.dumps({"tick": ticks, "action": action, "reward": reward, **result}) + "\n")
                assert not terminated and not truncated, result
                return result

            while env.get_imperial_state()["personal_savings"] < 200:
                step((A.NONE, 0, 0))
            funded = env.get_imperial_state()
            context, candidates = decision_context(env, observation, info["mission"], 0, 40000 - ticks)
            assert all("send_" + name + "_gift" in candidates for name in ("modest", "generous", "lavish"))
            assert context["imperial"] == funded and env.get_imperial_state() == funded
            gift = Candidate("send_modest_gift", [(A.SEND_MODEST_GIFT, 0, 0)], fingerprint(env, observation), {})
            result, _, _ = preview_candidate(env, gift, observation, 40000 - ticks)
            assert result["status"] == "completed" and env.get_imperial_state() == funded
            for gain in (3, 1):
                before = env.get_imperial_state()
                cost = before["gifts"][0]["cost"]
                assert "personal denarii" in step((A.SEND_MODEST_GIFT, 0, 0))["message"]
                after = env.get_imperial_state()
                assert after["personal_savings"] == before["personal_savings"] - cost
                assert after["favor"] == before["favor"] + gain
            while env.get_imperial_state()["months_since_gift"] < 12:
                step((A.NONE, 0, 0))
            before = env.get_imperial_state()
            assert before["gift_overdose_penalty"] == 0
            cost = before["gifts"][0]["cost"]
            step((A.SEND_MODEST_GIFT, 0, 0))
            after = env.get_imperial_state()
            assert after["personal_savings"] == before["personal_savings"] - cost
            assert after["favor"] == before["favor"] + 3
        summary = {"ticks": ticks, "population": int(observation["population_total"].item()),
                   "won": False, "verified_native_gifts": True}
        print(json.dumps(summary))
    finally:
        error = sys.exc_info()[1]
        try:
            artifacts.finish(env, locals().get("summary"), error)
        finally:
            env.close()


if __name__ == "__main__":
    main()
