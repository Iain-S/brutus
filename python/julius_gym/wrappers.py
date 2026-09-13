"""
Observation wrappers for Julius Gym environment

These wrappers help reduce observation space and normalize values for better RL training.
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .env import ActionType, JuliusEnv


TERRAIN_ROAD = 0x40
TERRAIN_NOT_CLEAR = 0xD77F


class RoadHousingCandidateActions(gym.Wrapper):
    """Masked spatial road-and-house candidate actions for a fixed scenario."""

    def __init__(self, env: JuliusEnv, candidate_count=16):
        super().__init__(env)
        if candidate_count < 1:
            raise ValueError("candidate_count must be positive")
        self.candidate_count = candidate_count
        self.candidates = []
        self.action_space = spaces.Discrete(1 + 2 * candidate_count)
        self.map_width = 162
        self.map_height = 162
        self.observation_space = spaces.Box(
            low=-100.0,
            high=100.0,
            shape=(10 + 4 * candidate_count,),
            dtype=np.float32,
        )

    @staticmethod
    def _is_clear(terrain, x, y):
        return (int(terrain[y, x]) & TERRAIN_NOT_CLEAR) == 0

    def _choose_candidates(self):
        terrain, _, width, height = self.env.get_map_data()
        possible = []
        for y in range(1, height - 1):
            for x in range(1, width - 2):
                if self._is_clear(terrain, x, y) and self._is_clear(terrain, x + 1, y):
                    possible.append(((x, y), (x + 1, y)))
        if len(possible) < self.candidate_count:
            raise RuntimeError(
                f"Map has only {len(possible)} clear road/house pairs; need {self.candidate_count}"
            )
        indexes = np.linspace(0, len(possible) - 1, self.candidate_count, dtype=int)
        self.candidates = [possible[index] for index in indexes]
        self.map_width = width
        self.map_height = height

    @staticmethod
    def _scalar(observation, key):
        return float(np.asarray(observation[key]).item())

    def _observation_vector(self, observation):
        """Combine compact city state with candidate coordinates and status."""
        features = [
            self._scalar(observation, "ratings_culture") / 100.0,
            self._scalar(observation, "ratings_prosperity") / 100.0,
            self._scalar(observation, "ratings_peace") / 100.0,
            self._scalar(observation, "ratings_favor") / 100.0,
            self._scalar(observation, "finance_treasury") / 10000.0,
            self._scalar(observation, "finance_tax_percentage") / 25.0,
            self._scalar(observation, "population_total") / 5000.0,
            self._scalar(observation, "population_sentiment") / 100.0,
            self._scalar(observation, "labor_unemployment_pct") / 100.0,
            self._scalar(observation, "resources_food_stocks") / 1000.0,
        ]
        terrain, _, _, _ = self.env.get_map_data()
        for road, house in self.candidates:
            road_x, road_y = road
            house_x, house_y = house
            features.extend(
                [
                    road_x / max(1, self.map_width - 1),
                    road_y / max(1, self.map_height - 1),
                    float((int(terrain[road_y, road_x]) & TERRAIN_ROAD) != 0),
                    float(self._is_clear(terrain, house_x, house_y)),
                ]
            )
        return np.asarray(features, dtype=np.float32)

    def reset(self, **kwargs):
        observation, info = self.env.reset(**kwargs)
        self._choose_candidates()
        return self._observation_vector(observation), info

    def action_masks(self):
        terrain, _, _, _ = self.env.get_map_data()
        mask = np.zeros(self.action_space.n, dtype=bool)
        mask[0] = True
        for index, (road, house) in enumerate(self.candidates):
            road_x, road_y = road
            house_x, house_y = house
            mask[1 + index] = self._is_clear(terrain, road_x, road_y)
            road_exists = (int(terrain[road_y, road_x]) & TERRAIN_ROAD) != 0
            mask[1 + self.candidate_count + index] = (
                road_exists and self._is_clear(terrain, house_x, house_y)
            )
        return mask

    def step(self, action):
        action = int(action)
        if action == 0:
            observation, reward, terminated, truncated, info = self.env.step(ActionType.NONE)
            info = dict(info)
            info.update({"placement_kind": "wait", "placement_success": False})
            return self._observation_vector(observation), reward, terminated, truncated, info
        if action < 1 or action >= self.action_space.n:
            raise ValueError(f"Invalid candidate action {action}")
        if action <= self.candidate_count:
            candidate_index = action - 1
            action_type = ActionType.BUILD_ROAD
            coordinate = self.candidates[candidate_index][0]
            kind = "road"
        else:
            candidate_index = action - 1 - self.candidate_count
            action_type = ActionType.BUILD_HOUSING
            coordinate = self.candidates[candidate_index][1]
            kind = "housing"
        observation, reward, terminated, truncated, info = self.env.step_at(
            action_type, *coordinate
        )
        info = dict(info)
        message = info.get("message", "")
        info.update(
            {
                "placement_kind": kind,
                "candidate_index": candidate_index,
                "placement_success": message == "Road built" or message.startswith("Built "),
            }
        )
        return self._observation_vector(observation), reward, terminated, truncated, info


class ConnectedHousingReward(gym.Wrapper):
    """Reward valid road-then-housing sequences for the placement curriculum."""

    def __init__(self, env, target_houses=3):
        super().__init__(env)
        self.target_houses = target_houses
        self.houses_built = 0

    def reset(self, **kwargs):
        self.houses_built = 0
        return self.env.reset(**kwargs)

    def step(self, action):
        observation, _, terminated, truncated, info = self.env.step(action)
        reward = -0.01
        if info.get("placement_success"):
            if info.get("placement_kind") == "road":
                reward = 0.1
            elif info.get("placement_kind") == "housing":
                self.houses_built += 1
                reward = 1.0
                if self.houses_built >= self.target_houses:
                    reward += 5.0
                    terminated = True
                    info = dict(info)
                    info["placement_goal_reached"] = True
        return observation, reward, terminated, truncated, info


class ActionMaskForwarder(gym.Wrapper):
    """Expose inner action masks through observation wrappers to SB3-contrib."""

    def action_masks(self):
        return self.env.get_wrapper_attr("action_masks")()


class FlattenObservation(gym.ObservationWrapper):
    """
    Flatten the nested dictionary observation into a single flat array.
    This is useful for algorithms that require Box observation spaces.
    """

    def __init__(self, env):
        super().__init__(env)

        # Extract all numeric values from nested dict
        self._keys = []
        self._extract_keys(self.env.observation_space.spaces)

        # Create flat box space
        self.observation_space = spaces.Box(
            low=-10000,
            high=100000,
            shape=(len(self._keys),),
            dtype=np.float32
        )

    def _extract_keys(self, space_dict, prefix=""):
        """Recursively extract all keys from nested dict space"""
        for key, value in space_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, spaces.Dict):
                self._extract_keys(value.spaces, full_key)
            else:
                self._keys.append(full_key)

    def observation(self, obs):
        """Flatten observation dict to array"""
        values = []
        for key in self._keys:
            # Navigate nested dict
            parts = key.split(".")
            val = obs
            for part in parts:
                val = val[part]
            values.append(float(val))
        return np.array(values, dtype=np.float32)


class NormalizeObservation(gym.ObservationWrapper):
    """
    Normalize observation values to roughly [-1, 1] range.
    This helps with neural network training stability.
    """

    def __init__(self, env):
        super().__init__(env)

        # Define normalization ranges for each metric
        self.ranges = {
            "ratings": {"culture": 100, "prosperity": 100, "peace": 100, "favor": 100},
            "finance": {
                "treasury": 10000,
                "tax_percentage": 25,
                "estimated_tax_income": 1000,
                "last_year_income": 5000,
                "last_year_expenses": 5000,
                "last_year_net": 5000,
            },
            "population": {
                "total": 5000,
                "school_age": 1000,
                "academy_age": 1000,
                "working_age": 3000,
                "sentiment": 100,
            },
            "labor": {
                "workers_needed": 3000,
                "workers_employed": 3000,
                "unemployment_percentage": 100,
                "wages": 50,
            },
            "resources": {"food_stocks": 1000, "food_types_available": 4},
            "buildings": {"housing": 500, "housing_capacity": 5000},
            "migration": {
                "immigration_amount": 100,
                "emigration_amount": 100,
                "immigration_queue_size": 100,
                "emigration_queue_size": 100,
            },
            "culture": {
                "entertainment": 100,
                "average_entertainment": 100,
                "average_education": 100,
                "average_health": 100,
                "religion_coverage": 100,
            },
            "time": {
                "tick": 1000,
                "day": 16,
                "month": 12,
                "year": 100,
                "total_months": 1200,
            },
            "victory": {
                "culture_goal": 100,
                "prosperity_goal": 100,
                "peace_goal": 100,
                "favor_goal": 100,
                "population_goal": 10000,
                "time_limit_years": 100,
            },
        }

    def observation(self, obs):
        """Normalize each value by its expected range"""
        normalized = {}
        for category, metrics in obs.items():
            normalized[category] = {}
            for metric, value in metrics.items():
                if category in self.ranges and metric in self.ranges[category]:
                    scale = self.ranges[category][metric]
                    normalized[category][metric] = value / scale
                else:
                    normalized[category][metric] = value
        return normalized


class SimplifyObservation(gym.ObservationWrapper):
    """
    Reduce observation space to only the most important metrics.
    This significantly reduces the state space for faster learning.
    """

    def __init__(self, env):
        super().__init__(env)

        # Define simplified observation space with only key metrics
        self.observation_space = spaces.Dict({
            "ratings": spaces.Dict({
                "culture": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "prosperity": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "peace": spaces.Box(0, 100, shape=(), dtype=np.int32),
                "favor": spaces.Box(0, 100, shape=(), dtype=np.int32),
            }),
            "finance": spaces.Dict({
                "treasury": spaces.Box(-10000, 1000000, shape=(), dtype=np.int32),
                "tax_percentage": spaces.Box(0, 25, shape=(), dtype=np.int32),
            }),
            "population": spaces.Dict({
                "total": spaces.Box(0, 100000, shape=(), dtype=np.int32),
                "sentiment": spaces.Box(0, 100, shape=(), dtype=np.int32),
            }),
            "labor": spaces.Dict({
                "unemployment_percentage": spaces.Box(0, 100, shape=(), dtype=np.int32),
            }),
            "resources": spaces.Dict({
                "food_stocks": spaces.Box(0, 10000, shape=(), dtype=np.int32),
            }),
        })

    def observation(self, obs):
        """Extract only key metrics"""
        # Handle both flat and nested observation spaces
        if "ratings" in obs:
            # Nested dict format
            return {
                "ratings": obs["ratings"],
                "finance": {
                    "treasury": obs["finance"]["treasury"],
                    "tax_percentage": obs["finance"]["tax_percentage"],
                },
                "population": {
                    "total": obs["population"]["total"],
                    "sentiment": obs["population"]["sentiment"],
                },
                "labor": {
                    "unemployment_percentage": obs["labor"]["unemployment_percentage"],
                },
                "resources": {
                    "food_stocks": obs["resources"]["food_stocks"],
                },
            }
        else:
            # Flat format (from JuliusEnv)
            return {
                "ratings": {
                    "culture": obs["ratings_culture"],
                    "prosperity": obs["ratings_prosperity"],
                    "peace": obs["ratings_peace"],
                    "favor": obs["ratings_favor"],
                },
                "finance": {
                    "treasury": obs["finance_treasury"],
                    "tax_percentage": obs["finance_tax_percentage"],
                },
                "population": {
                    "total": obs["population_total"],
                    "sentiment": obs["population_sentiment"],
                },
                "labor": {
                    "unemployment_percentage": obs["labor_unemployment_pct"],
                },
                "resources": {
                    "food_stocks": obs["resources_food_stocks"],
                },
            }


class RewardShaping(gym.Wrapper):
    """
    Shape rewards to encourage specific behaviors.
    This can help guide learning towards better policies.
    """

    def __init__(self, env, population_weight=1.0, rating_weight=1.0, treasury_weight=0.5):
        super().__init__(env)
        self.population_weight = population_weight
        self.rating_weight = rating_weight
        self.treasury_weight = treasury_weight

        self.prev_population = 0
        self.prev_avg_rating = 0
        self.prev_treasury = 0

    def _to_scalar(self, value):
        if isinstance(value, np.ndarray):
            if value.size == 1:
                return float(value.item())
            return float(value.squeeze()[0])
        if isinstance(value, (int, float)):
            return float(value)
        return float(value)

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)

        # Initialize previous values
        self.prev_population = self._to_scalar(obs["population"]["total"])
        self.prev_avg_rating = (
            sum(self._to_scalar(v) for v in obs["ratings"].values()) / 4
        )
        self.prev_treasury = self._to_scalar(obs["finance"]["treasury"])

        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        # Add shaped rewards
        shaped_reward = float(reward)

        # Reward population growth
        current_population = self._to_scalar(obs["population"]["total"])
        pop_delta = current_population - self.prev_population
        shaped_reward += pop_delta * self.population_weight * 0.01

        # Reward improving average rating
        avg_rating = (
            sum(self._to_scalar(v) for v in obs["ratings"].values()) / 4
        )
        rating_delta = avg_rating - self.prev_avg_rating
        shaped_reward += rating_delta * self.rating_weight * 0.1

        # Small reward for maintaining treasury
        current_treasury = self._to_scalar(obs["finance"]["treasury"])
        if current_treasury > 1000:
            shaped_reward += self.treasury_weight * 0.01

        # Update previous values
        self.prev_population = current_population
        self.prev_avg_rating = avg_rating
        self.prev_treasury = current_treasury

        return obs, shaped_reward, terminated, truncated, info


class RestrictActions(gym.ActionWrapper):
    """
    Restrict the action space to a subset of discrete actions.
    """

    def __init__(self, env, allowed_actions):
        super().__init__(env)
        self.allowed_actions = list(allowed_actions)
        self.action_space = spaces.Discrete(len(self.allowed_actions))

    def action(self, action):
        return self.allowed_actions[int(action)]


class PopulationYearReward(gym.Wrapper):
    """
    Provide a sparse, population-focused reward once per in-game year.

    - Reward is emitted only when the year window completes.
    - Optionally uses delta population relative to episode start.
    """

    def __init__(self, env, months=12, use_delta=True):
        super().__init__(env)
        self.months = months
        self.use_delta = use_delta
        self._start_months = None
        self._start_population = None

    def _get_total_months(self, obs):
        if "time" in obs and "total_months" in obs["time"]:
            return obs["time"]["total_months"]
        return obs.get("time_total_months")

    def _get_population(self, obs):
        if "population" in obs and "total" in obs["population"]:
            return obs["population"]["total"]
        return obs.get("population_total")

    def _to_scalar(self, value):
        if value is None:
            return None
        if isinstance(value, np.ndarray):
            if value.size == 1:
                return float(value.item())
            return float(value.squeeze()[0])
        if isinstance(value, (int, float)):
            return float(value)
        return float(value)

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self._start_months = self._to_scalar(self._get_total_months(obs))
        self._start_population = self._to_scalar(self._get_population(obs))
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        current_months = self._to_scalar(self._get_total_months(obs))
        current_population = self._to_scalar(self._get_population(obs))

        elapsed = None
        if self._start_months is not None and current_months is not None:
            elapsed = current_months - self._start_months

        year_complete = elapsed is not None and elapsed >= self.months
        done = terminated or truncated or year_complete

        if done and current_population is not None and self._start_population is not None:
            reward = (
                current_population - self._start_population
                if self.use_delta
                else current_population
            )
            info = dict(info)
            info["population_end"] = current_population
            info["population_start"] = self._start_population
            info["population_year_complete"] = year_complete
        else:
            reward = 0.0

        return obs, reward, done, truncated, info


def make_efficient_env(data_directory, scenario_file=None, max_ticks=5000,
                       lib_path=None, simplify=True, normalize=True, flatten=True,
                       shape_rewards=True, population_year_reward=False,
                       population_year_months=12, population_year_use_delta=True,
                       restrict_actions=None):
    """
    Create an environment with wrappers optimized for efficient RL training.

    Args:
        data_directory: Path to Caesar III data
        scenario_file: Optional scenario file
        max_ticks: Max ticks per episode
        lib_path: Optional path to libjulius_gym library
        simplify: Use simplified observation space
        normalize: Normalize observations
        flatten: Flatten to Box space (required for some algorithms)
        shape_rewards: Apply reward shaping

    Returns:
        Wrapped environment ready for training
    """
    import julius_gym

    env = julius_gym.JuliusEnv(
        data_directory=data_directory,
        scenario_file=scenario_file,
        max_ticks=max_ticks,
        lib_path=lib_path,
    )

    if population_year_reward:
        env = PopulationYearReward(
            env,
            months=population_year_months,
            use_delta=population_year_use_delta,
        )

    if restrict_actions is not None:
        env = RestrictActions(env, restrict_actions)

    if simplify:
        env = SimplifyObservation(env)

    if shape_rewards:
        env = RewardShaping(env)

    if normalize:
        env = NormalizeObservation(env)

    if flatten:
        env = FlattenObservation(env)

    return env


def make_road_housing_curriculum_env(
    data_directory,
    scenario_file,
    max_ticks=200,
    lib_path=None,
    candidate_count=16,
    target_houses=3,
):
    """Create a masked spatial placement task for one fixed scenario."""
    env = JuliusEnv(
        data_directory=data_directory,
        scenario_file=scenario_file,
        max_ticks=max_ticks,
        lib_path=lib_path,
    )
    env = RoadHousingCandidateActions(env, candidate_count=candidate_count)
    env = ConnectedHousingReward(env, target_houses=target_houses)
    return ActionMaskForwarder(env)
