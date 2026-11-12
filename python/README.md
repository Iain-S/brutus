# Julius Gymnasium Environment

## Native Taxation And Finances

Rebuild the headless library for `env.get_finance_state()`. The read-only JSON
query separates current house collector coverage from cached monthly taxed
population, raw monthly tax bases, annual collected/uncollected denarii and
annual wages/interest/governor-salary counters. Monthly tax bases are not cash
and need not correspond to the current tax rate. Annual counters reset at the
native year boundary. Estimates and this/last-year overview totals are cached;
the query does not collect taxes or recalculate them.

Full raw diagnostics include all in-use house-size records (the native tax
collector's accounting criterion), forum/senate staffing, figure IDs and both
cached road flags and the read-only native road-access predicate used to spawn
collectors. A native adjacent-road check is not a city-entry connectivity proof.
`houses_covered_activity_cached` is a decaying, capped service-activity counter
shared with labor seekers, not unique/current tax-covered houses.
The planner retains accounting totals but only the first eight collector
buildings by ID, with explicit omission counts. Coverage is not proof of cash
collection: the tax rate may be zero, and collection happens monthly.

Optional `add_forum_district_N` choices use normal paid, road-connected 2x2
construction near the existing first-four district anchors. Existing native
tax/wage +/-1 actions are also elective proposals, with native bounds enforced
by previews. These do not prescribe a budget, tax rate or winning build order.
Action count remains 61; no game rules or observation layouts change.

```shell
python test_finance.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
python -m unittest discover -s . -p test_finance_feedback.py
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_finance_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_finance --output-on-failure
```

The paid fixture distinguishes occupied untaxed housing from staffed forum
coverage and actual collected denarii. It is not a sustainability benchmark;
trade and longer-term budget adequacy still need measurement.

## Native Housing Feedback

Rebuild the headless library for `env.get_housing_state()`. This read-only JSON
query includes all active houses, all 20 loaded house models, cached house/tile
desirability, inventory units, services and the cached native prosperity cap.
Current-level and next-level goods/service checks reuse the engine predicate
with private demand counters. Queries do not evolve houses, update caches,
consume goods, change global demands or advance time.

Desirability uses the current model; upgrade goods/services use the next model.
The devolution threshold takes precedence. Maximum-level houses have no next
level/check. Passing these independent checks does not guarantee evolution:
population, merging, timing and expansion space still matter. Wine diversity
uses the native cached citywide flag, not household wine quantity. Food types
count nonzero inventory slots, not cached consumption counts.

Planner feedback includes totals for all houses, referenced models and the first
eight house rows by ID with explicit omission counts. Optional repeatable
`landscape_district_N` choices place up to four paid gardens near existing
district anchors using the loaded garden range. They clear vegetation explicitly,
avoid infrastructure and add no access roads. This is a bounded tool, not a
required build order or housing/population cap. Forecasts expose independent
desirability blockers and the cached prosperity cap, not an upgrade prediction.
Action count remains 61 and existing observation/config layouts are unchanged.

```shell
python -m unittest discover -s . -p test_housing_feedback.py
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_housing_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_housing --output-on-failure
```

## Native Water Infrastructure

Rebuild the headless library before using `BUILD_RESERVOIR` (59) and
`BUILD_AQUEDUCT` (60). The action space is now 61; IDs 0-58 and the observation/
config struct layouts are unchanged. Older fixed-action-space RL models need
their matching build/package or explicit migration.

Reservoir coordinates are the top-left of a 3x3 footprint. The adapter uses the
normal GUI reservoir mode at that footprint's center with identical start/end
points, paying for one reservoir, not an implicit aqueduct drag. Aqueduct
actions place individual native-validated tiles. Costs, menu availability,
terrain rules and legal road crossings remain native game behavior.

`env.get_water_supply()` reads active wells/reservoirs/fountains and all
aqueduct tile wet/dry states. It exposes cached supply, staffing, near-water and
reservoir-range observations separately, without updating supply or advancing
time. Aqueduct wet/dry uses the cached native image band: the internal aqueduct
grid also stores topology offsets and is not a reliable boolean water flag.

The planner can choose bounded `establish_water_supply_district_N` proposals.
They compose an entry-connected fountain, source reservoir and optional relay/
midpoint aqueduct path in snapshots. Geometry is conservative (including avoiding
road crossings); real native construction and optional forecasts still validate
each proposal. Nothing forces a water-first build order. The current first-four
well-anchor service search and other placement limitations remain.

```shell
python test_water_supply.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_water_supply_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_water_supply --output-on-failure
```

The asset-backed check pays for all construction and tests actual fountain
access, an initially dry relay filled through aqueducts, invalid construction,
snapshot rollback and native evolution. Its food/religion/landscaping setup is
a test fixture, not a planner policy or demonstration of prosperity 25 citywide.
The `Headless Gym Tests` workflow runs the asset-free C fixtures on Linux without
original game data or model weights.

## Imperial Gifts And Personal Finances

Rebuild `julius_gym` before using the new imperial capability.
`env.get_imperial_state()` returns read-only versioned JSON data: favor,
personal savings, governor rank/salary, months since the last gift, the native
gift-overdose counter, and fresh costs/affordability for all three gift sizes.
It neither advances time nor changes the GUI's cached gift prices, and remains
available after an episode ends. Personal savings are not city treasury.

`ActionType.SEND_MODEST_GIFT` (56), `SEND_GENEROUS_GIFT` (57) and
`SEND_LAVISH_GIFT` (58) use the normal native gift functions. Coordinates are
ignored. Each is an ordinary paid simulation step; insufficient personal funds
reject the gift, and the normal tick is still charged. Costs, favor clamping,
diminishing returns and the native 12-month recovery are unchanged. The planner
offers engine-legal gift candidates without prescribing a gifting schedule.
Forecasts include favor/personal savings, with gift prices separate from city
treasury outlay. No salary changes or request dispatch are implemented yet.

Existing action IDs 0-55 and observation/config struct layouts are unchanged,
but subsequent water actions bring the current action space to 61. Existing fixed-action-space RL models
need their matching old build/package or explicit migration; they cannot be
assumed compatible with the expanded space.

```shell
python test_imperial.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_imperial_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_imperial --output-on-failure
```

The asset-backed test earns savings through ordinary salary, checks preview
rollback, sends native gifts, waits for normal recovery and retains a replayable
run bundle. It is a capability test, not a winning controller.

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

### Food Supply Diagnostics

`env.get_food_supply()` returns a separate versioned JSON payload for active
edible-food farms, granaries and markets, without advancing simulation time.
It remains available after an episode ends. Rebuild the library to use it.
Existing observation structures and `get_buildings()` records are unchanged.

The `buildings` rows contain position, workers/required workers, labor coverage,
computed road access, cached access/network and entry distance. The cached
access byte is not maintained for every building type; use the computed field
for the engine's present road-access predicate (not a delivery-path guarantee).
Farm `progress_points` and
`progress_max` are production work, not food inventory; one completed batch
normally dispatches a 100-unit load. Granary and market `food_units` arrays use
the payload's order: wheat, vegetables, fruit, meat/fish. Granary free-space
units are separate. Olives and vines are not edible food.

Inventories are physical amounts, not a guarantee of accessibility, adequate
staffing, delivery or nutrition. The city observation's food stock is a filtered,
cached granary indicator, not another container to add to these amounts.
Cargo, warehouses and household stocks are excluded; household stocks remain
available through `get_buildings()`. Raw primary/shared figure IDs are references,
not cargo counts; the shared slot can hold a labor seeker rather than a buyer.

```shell
python test_food_supply.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_food_supply_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_food_supply --output-on-failure
```

### Building Observation Counts

Building aggregates use active and newly created engine records rather than
periodically updated service/industry count buckets. Food buildings include
farms and granaries; industrial buildings include workshops. Counts do not
guarantee staffing or road access. `total_buildings` counts physical records,
including linked parts; entertainment counts a linked hippodrome as one venue.
The observation ABI is unchanged, but policies trained on incorrect zero counts
can behave differently after rebuilding.

The headless build includes an asset-free native regression:

```shell
cmake --build <ABSOLUTE_BUILD_DIRECTORY> --target gym_observation_counts_test
ctest --test-dir <ABSOLUTE_BUILD_DIRECTORY> -R gym_observation_counts --output-on-failure
```

For an additional construction/reset check with licensed data:

```shell
python test_building_observations.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

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
    # Choose action (0-60)
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

Discrete action space with 61 actions:

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

### Imperial Gifts (56-58)

- `SEND_MODEST_GIFT` (56), `SEND_GENEROUS_GIFT` (57), `SEND_LAVISH_GIFT` (58):
  use personal savings and the normal emperor gift rules, not city treasury.

### Water Construction (59-60)

- `BUILD_RESERVOIR` (59): One native reservoir at a 3x3 top-left footprint.
- `BUILD_AQUEDUCT` (60): One native aqueduct tile; normal routing/terrain rules apply.

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
