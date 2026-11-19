"""Check that planner previews preserve replay and actual macros attract residents."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute, fingerprint
from test_snapshot_restore import run_suffix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=2000)
    try:
        observation, info = env.reset()
        first_reset_token = env.get_state_token()
        wait_token = fingerprint(env, observation)
        observation, _, _, _, _ = env.step(0)
        assert wait_token != fingerprint(env, observation), "Time-only state change was not detected"
        observation, info = env.reset()
        assert env.get_state_token() != first_reset_token, "Reset reused a state identity"
        token = env.get_state_token()
        with env.snapshot() as branch:
            env.step(0)
            first_branch_token = env.get_state_token()
            branch.restore()
            assert env.get_state_token() == token, "Restore did not recover saved identity"
            env.step(0)
            assert env.get_state_token() != first_branch_token, "Divergent branches reused an identity"
            branch.restore()
        initial = fingerprint(env, observation)
        with env.snapshot() as start:
            expected = run_suffix(env, 100)
            start.restore()
            context, candidates = decision_context(env, observation, info["mission"], 0, 1800)
            assert initial == fingerprint(env, observation), "Preview changed exported map state"
            actual = run_suffix(env, 100)
            assert expected == actual, "Preview changed simulation replay"
            start.restore()
        assert context["unavailable"], "Unreachable macros must have explicit diagnostics"
        housing = candidates["expand_housing"]
        observation, result, terminated, truncated = execute(env, housing, observation, 1800)
        assert result["status"] == "completed" and not terminated and not truncated
        try:
            execute(env, housing, observation, 1800)
        except ValueError:
            pass
        else:
            raise AssertionError("Stale macro executed twice")
        for _ in range(1600):
            observation, _, terminated, truncated, _ = env.step(0)
            assert not terminated and not truncated
        assert int(observation["population_total"].item()) > 0
    finally:
        env.close()
    print("Preview replay, stale-candidate rejection, execution and immigration passed.")


if __name__ == "__main__":
    main()
