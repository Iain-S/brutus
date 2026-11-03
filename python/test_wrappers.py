#!/usr/bin/env python3
import gymnasium as gym
import numpy as np
from gymnasium import spaces

from julius_gym.wrappers import (
    FlattenObservation,
    NormalizeObservation,
    PopulationYearReward,
    RewardShaping,
    SimplifyObservation,
)


class DummyFlatEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(1)
        self.observation_space = spaces.Dict(
            {
                "ratings_culture": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "ratings_prosperity": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "ratings_peace": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "ratings_favor": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "finance_treasury": spaces.Box(-10000, 1000000, shape=(), dtype=np.int32),
                "finance_tax_percentage": spaces.Box(0, 25, shape=(), dtype=np.int32),
                "population_total": spaces.Box(0, 100000, shape=(), dtype=np.int32),
                "population_sentiment": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "labor_unemployment_pct": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "resources_food_stocks": spaces.Box(0, 10000, shape=(), dtype=np.int32),
                "time_total_months": spaces.Box(0, 12000, shape=(), dtype=np.int32),
            }
        )
        self._months = 0
        self._population = 100

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._months = 0
        self._population = 100
        return self._obs(), {}

    def step(self, action):
        self._months += 1
        self._population += 10
        return self._obs(), 0.0, False, False, {}

    def _obs(self):
        return {
            "ratings_culture": 50,
            "ratings_prosperity": 50,
            "ratings_peace": 50,
            "ratings_favor": 50,
            "finance_treasury": 2000,
            "finance_tax_percentage": 10,
            "population_total": self._population,
            "population_sentiment": 60,
            "labor_unemployment_pct": 10,
            "resources_food_stocks": 500,
            "time_total_months": self._months,
        }


class DummyNestedEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(1)
        self.observation_space = spaces.Dict(
            {
                "ratings": spaces.Dict(
                    {
                        "culture": spaces.Box(0, 100, shape=(), dtype=np.int32),
                        "prosperity": spaces.Box(0, 100, shape=(), dtype=np.int32),
                        "peace": spaces.Box(0, 100, shape=(), dtype=np.int32),
                        "favor": spaces.Box(0, 100, shape=(), dtype=np.int32),
                    }
                ),
                "finance": spaces.Dict(
                    {
                        "treasury": spaces.Box(-10000, 1000000, shape=(), dtype=np.int32),
                        "tax_percentage": spaces.Box(0, 25, shape=(), dtype=np.int32),
                    }
                ),
                "population": spaces.Dict(
                    {
                        "total": spaces.Box(0, 100000, shape=(), dtype=np.int32),
                        "sentiment": spaces.Box(0, 100, shape=(), dtype=np.int32),
                    }
                ),
                "labor": spaces.Dict(
                    {
                        "unemployment_percentage": spaces.Box(0, 100, shape=(), dtype=np.int32),
                    }
                ),
                "resources": spaces.Dict(
                    {
                        "food_stocks": spaces.Box(0, 10000, shape=(), dtype=np.int32),
                    }
                ),
                "time": spaces.Dict(
                    {
                        "total_months": spaces.Box(0, 12000, shape=(), dtype=np.int32),
                    }
                ),
            }
        )
        self._months = 0
        self._population = 100

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._months = 0
        self._population = 100
        return self._obs(), {}

    def step(self, action):
        self._months += 1
        self._population += 10
        return self._obs(), 0.0, False, False, {}

    def _obs(self):
        return {
            "ratings": {"culture": 50, "prosperity": 50, "peace": 50, "favor": 50},
            "finance": {"treasury": 2000, "tax_percentage": 10},
            "population": {"total": self._population, "sentiment": 60},
            "labor": {"unemployment_percentage": 10},
            "resources": {"food_stocks": 500},
            "time": {"total_months": self._months},
        }


def test_simplify_observation_from_flat():
    env = SimplifyObservation(DummyFlatEnv())
    obs, _ = env.reset()
    assert "ratings" in obs
    assert obs["finance"]["treasury"] == 2000


def test_normalize_observation_values():
    env = NormalizeObservation(DummyNestedEnv())
    obs, _ = env.reset()
    assert np.isclose(obs["finance"]["treasury"], 2000 / 10000)
    assert np.isclose(obs["population"]["sentiment"], 60 / 100)


def test_flatten_observation_length():
    env = FlattenObservation(DummyNestedEnv())
    obs, _ = env.reset()
    assert obs.shape[0] == len(env._keys)


def test_reward_shaping_adds_signal():
    base_env = DummyNestedEnv()
    env = RewardShaping(base_env, population_weight=1.0, rating_weight=1.0, treasury_weight=1.0)
    obs, _ = env.reset()
    _, reward, _, _, _ = env.step(0)
    assert reward > 0.0


def test_population_year_reward_delta():
    env = PopulationYearReward(DummyFlatEnv(), months=12, use_delta=True)
    env.reset()
    for _ in range(11):
        _, reward, done, _, _ = env.step(0)
        assert reward == 0.0
        assert not done
    _, reward, done, _, info = env.step(0)
    assert done
    assert reward == 120
    assert info["population_end"] == 220
    assert info["population_year_complete"] is True


def test_population_year_reward_absolute():
    env = PopulationYearReward(DummyFlatEnv(), months=12, use_delta=False)
    env.reset()
    reward = None
    done = False
    for _ in range(12):
        _, reward, done, _, _ = env.step(0)
    assert done
    assert reward == 220
