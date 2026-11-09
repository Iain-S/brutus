# Julius Gymnasium Environment

## Peaceful Campaign Selection

With a rebuilt headless library, select a campaign using `campaign_rank` instead
of `scenario_file`. Ranks are zero-based and select the peaceful branch:

```python
env = julius_gym.JuliusEnv(
    data_directory=data_dir,
    lib_path=lib_path,
    campaign_rank=3,  # Tarraco; mission index 4
)
obs, info = env.reset()
print(info["mission"])
```

Every reset reloads the campaign from the original `mission1.pak`.
`env.get_mission_info()` returns campaign identity, tutorial classification,
scheduled combat events (including distant battles), and the gladiator revolt
flag. Event types are 1=uprising, 2=enemy army, 3=Caesar, 4=distant battle;
years are offsets from the returned start year, months are engine month values.
An empty schedule does not prevent attacks triggered by poor imperial favor.
The existing configuration struct ABI and scenario-file usage are unchanged.

Run the campaign audit and reset/snapshot replay smoke test with explicit paths:

```shell
python test_campaign.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

The default target is Tarraco: no tutorial classification, population goal 2500,
culture 45, prosperity 25, peace 30, and favor 70 in the tested original data.
The test rejects scheduled combat or tutorial behavior and checks repeated
1600-tick no-op traces, actual game-time progression, and snapshot replay.
This is an interface smoke test, not a winning controller. See
`examples/README.md` for the deterministic starter settlement runner.

OpenAI Gymnasium environment for training reinforcement learning agents on Julius, an open-source re-implementation of Caesar III.

## Installation

### Prerequisites

1. **Build the Julius shared library:**

```bash
cd /path/to/julius
mkdir build && cd build
cmake .. -DBUILD_GYMNASIUM_LIB=ON -DHEADLESS_BUILD=ON
make julius_gym
```

This will create `libjulius_gym.so` in the build directory.

2. **Install Python package:**

```bash
cd python
pip install -e .
```

### Caesar III Data Files

You need the original Caesar III data files to run Julius. The environment expects the path to the directory containing `c3.eng` and other game data files.

## Usage

### Basic Example

```python
import julius_gym

# Create environment
env = julius_gym.JuliusEnv(
    data_directory="/path/to/caesar3/data",
    scenario_file="/path/to/scenario.map",  # Optional
    max_ticks=10000,  # Optional max steps per episode
    lib_path="build/libjulius_gym.so"  # Optional, auto-detected if in standard location
)

# Reset environment
observation, info = env.reset()

# Run episode
done = False
total_reward = 0

while not done:
    # Choose action (0-55)
    action = env.action_space.sample()  # Random action

    # Execute action
    observation, reward, terminated, truncated, info = env.step(action)

    total_reward += reward
    done = terminated or truncated

    print(f"Reward: {reward}, Info: {info}")

print(f"Episode finished with total reward: {total_reward}")
env.close()
```

### With Stable-Baselines3

```python
from stable_baselines3 import PPO
import julius_gym

# Create environment
env = julius_gym.JuliusEnv(
    data_directory="/path/to/caesar3/data",
    max_ticks=5000
)

# Train agent
model = PPO("MultiInputPolicy", env, verbose=1)
model.learn(total_timesteps=100000)

# Save model
model.save("julius_ppo")

# Load and test
model = PPO.load("julius_ppo")
obs, info = env.reset()
for _ in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
```

## Observation Space

The observation space is a dictionary containing:

- **ratings**: City ratings (culture, prosperity, peace, favor) [0-100]
- **finance**: Treasury, tax percentage, income/expenses
- **population**: Total population, sentiment, working age counts
- **labor**: Employment statistics, wages
- **resources**: Food stocks and availability
- **buildings**: Housing counts and capacity
- **migration**: Immigration/emigration statistics
- **culture**: Entertainment, education, health, religion metrics
- **time**: Current game time (tick, day, month, year)
- **victory**: Scenario victory conditions

## Action Space

Discrete action space with 56 actions:

### Administrative Actions (0-4)
- `NONE` (0): No action
- `ADJUST_TAX_UP` (1): Increase tax by 1%
- `ADJUST_TAX_DOWN` (2): Decrease tax by 1%
- `ADJUST_WAGES_UP` (3): Increase wages
- `ADJUST_WAGES_DOWN` (4): Decrease wages

### Building Actions (5-53)
- Various buildings: housing, roads, infrastructure, services, production, entertainment
- Buildings are placed at default coordinates (50, 50)

### Destruction (54)
- `CLEAR_LAND` (54): Clear land/demolish buildings

### Bridge (55)

- `BUILD_LOW_BRIDGE` (55): Build an engine-validated low bridge from a shoreline water tile.

## Reward Structure

- **Rating improvements**: +0.1 per rating point increase
- **Maintaining positive treasury**: +0.01
- **Bankruptcy**: -1.0
- **Victory**: +100.0
- **Defeat**: -50.0
- **Failed actions**: -0.1

## Episode Termination

Episodes end when:
- Victory conditions are met (terminated=True)
- Defeat conditions are met (terminated=True)
- Max ticks reached (truncated=True)
- Severe bankruptcy (treasury < -5000)

## API Reference

### `JuliusEnv`

```python
JuliusEnv(
    data_directory: str,
    scenario_file: Optional[str] = None,
    max_ticks: int = 0,
    lib_path: Optional[str] = None
)
```

**Parameters:**
- `data_directory`: Path to Caesar III data files
- `scenario_file`: Optional scenario file to load
- `max_ticks`: Maximum ticks per episode (0 = unlimited)
- `lib_path`: Optional path to libjulius_gym.so

**Methods:**
- `reset()`: Reset environment to initial state
- `step(action)`: Execute action and advance one tick
- `close()`: Clean up resources

## Development

### Snapshot and reset regression test

`JuliusEnv.snapshot()` captures an active episode and can later restore it.
Snapshots use temporary Julius save files internally; use them as a context
manager so the temporary file is removed promptly:

```python
env.reset()
with env.snapshot() as snapshot:
    # Explore an action branch.
    env.step(0)
    snapshot.restore()
```

Snapshots also retain the complete in-memory random generator state, including
cached values and the population-age random pool, which ordinary game saves do
not serialize. Rebuild the headless library after updating snapshot support.
An inhabited-city regression compares identical construction sequences with
and without candidate previews:

```shell
python test_inhabited_snapshots.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

To check reset and snapshot determinism against licensed game data, run:

```bash
python test_snapshot_restore.py \
  --data-dir /absolute/path/to/caesar3/data \
  --scenario /absolute/path/to/scenario.map \
  --lib-path /absolute/path/to/libjulius_gym.so
```

The script skips cleanly when these paths are not supplied, so it is safe to
run in source-only environments.

### Spatial placement curriculum

`examples/train_road_housing.py` is a small, real-map training milestone. It
exposes normalized city state plus each candidate pair's coordinates and build
status to `MaskablePPO`, masks housing until its adjacent road has been built,
and rewards three connected placements.
It is deliberately not a full scenario-winning agent.

```bash
python examples/train_road_housing.py \
  --data-dir /absolute/path/to/caesar3/data \
  --scenario /absolute/path/to/scenario.map \
  --lib-path /absolute/path/to/libjulius_gym.so \
  --timesteps 5000
```

Run `test_road_housing_curriculum.py` with the same paths to check the action
mask and real map mutations without a training run.

### Fixed-scenario evaluation

Use `examples/evaluate_scenario.py` to measure the real scenario outcome,
elapsed Gym ticks, active victory criteria, and compact final city diagnostics.
It reports those independently of cumulative shaped reward and accepts a short,
coordinate-aware plan before advancing with no-op ticks:

```bash
python examples/evaluate_scenario.py \
  --data-dir /absolute/path/to/caesar3/data \
  --scenario /absolute/path/to/scenario.map \
  --lib-path /absolute/path/to/libjulius_gym.so \
  --max-ticks 5000 \
  --action 'BUILD_ROAD@18,1' \
  --action 'BUILD_HOUSING@19,1'
```

Pass `--json-out report.json` to save a machine-readable report.  Run
`test_scenario_evaluator.py` with the same paths for a short reset/evaluation
repeatability check.

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black julius_gym/
isort julius_gym/
```

## License

AGPL v3 - See LICENSE file for details.
