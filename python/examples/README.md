# Julius RL Training Examples

## Deterministic Tarraco Starter

Run the construction baseline without a model or training:

```shell
python examples/run_baseline.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

Run from `python/` with the dedicated training interpreter and a rebuilt library.
The script selects peaceful campaign rank 3, checks its event schedule, finds a
clear site connected to the entry road, and places a street, eight housing lots,
two wells, prefecture and engineer's post. It then waits, reporting population and
victory state. Every placement uses normal construction costs and rules.

The default 3000-tick run produced 46 residents with no failed placements in the
tested original game data. This is a starter settlement, not a mission-winning
policy: it does not yet provide food or grow the city to the victory thresholds.
Use `--max-ticks` to set the horizon and `--log` for an alternate JSONL log path.
Resolve the output path from the launch directory; the default is
`runs/baseline.jsonl`. The log records each action, treasury, population and
termination state. The runner stops on a construction failure and rejects a
run with no population growth.

Regression checks with licensed data:

```shell
python test_baseline.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH>
python test_campaign.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

Gym steps now advance exactly one simulation tick, independent of GUI windows
or wall-clock timing. Existing trained policies may behave differently after
this correction. Normal graphical play continues to use the graphical loop.

### Expansion and Food

```shell
python examples/run_baseline.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH> --blocks 3 --food --max-ticks 12000
python test_food_baseline.py --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

`--blocks` places additional housing blocks. `--food` adds an engine-validated
low bridge to Tarraco's farmland, a wheat farm, a worker settlement, granary and
market. Forest clearing and bridge construction use normal costs. The tested
12000-tick run reached 182 residents and 1300 stored food with no failed builds.
The integration test compares complete logs from two fresh runs.

### Delivery Diagnostics

The food mode also adds local markets and safety services for the farm district.
Placement preserves access beyond the bridge landing and connects granaries at
the middle of an edge, as required by the engine. An anchor now restricts the
initial road search to the neighborhood of the target, while allowing traversal
along the connected road network when nearby sites are occupied.

`env.get_buildings()` returns active building footprints, types, employment,
labor-seeker coverage, house population, current household food inventory, house
level, and well/fountain access. It reads engine state without advancing time or
changing the existing observation struct. Types use `src/building/type.h` IDs;
non-house records use level -1. Diagnostic food stock means current inventory,
not a prediction of future food security.

The runner samples resident food/water coverage every 800 ticks and at episode
end. Each log row includes `supply_sample_tick` so cached coverage is not mistaken
for a current measurement. A companion `.buildings.json` contains the final
building diagnostics.

The tested `--food --blocks 5 --max-ticks 24000` run peaked at 262 residents and
ended with 181 residents, 2200 stored food, 51 residents with food in their homes,
and a surviving farm. Storage and markets were staffed. The population decline
and incomplete food/water coverage remain unresolved; this is not a sustainable
city or a winning policy. The earlier 182-resident result above describes the
previous construction-only food baseline.

`test_food_baseline.py` now checks 24000 ticks, household food delivery, staffed
storage/markets, farm survival and replay equality. Run the small geometry tests
without game data using `python test_baseline_planning.py`.

Food stocks establish production and storage, not adequate delivery to every
house. The controller still needs service coverage, expansion and rating
management to win. Food produced/consumed-last-month observation fields are
currently placeholders and should not be used to evaluate this chain.

Low bridge is action 55, appended without renumbering existing actions; the
discrete action count is now 56. Models trained with the old 55-action space
need an explicit compatibility wrapper or retraining. `env.bridge_span(x, y)`
queries the engine for a legal bridge length and cardinal direction.

This directory contains example RL agents for training on Julius, optimized for 4GB GPU memory constraints.

## Quick Start

```bash
# Install dependencies
pip install stable-baselines3[extra] torch

# Train A2C agent (most memory efficient)
python examples/train_a2c.py --data-dir /path/to/caesar3/data --timesteps 300000

# Train DQN agent
python examples/train_dqn.py --data-dir /path/to/caesar3/data --timesteps 200000

# Train PPO agent
python examples/train_ppo_optimized.py --data-dir /path/to/caesar3/data --timesteps 250000
```

## Algorithms Comparison

| Algorithm | GPU Memory | Training Speed | Sample Efficiency | Recommended For |
|-----------|------------|----------------|-------------------|-----------------|
| **A2C** | ~500MB-1GB | Fast | Medium | **Best for 4GB GPU** |
| **DQN** | ~1-2GB | Medium | High | Good exploration |
| **PPO** | ~1.5-2.5GB | Slower | High | Best final performance |

### A2C (Advantage Actor-Critic)
- **Memory**: 500MB-1GB GPU RAM
- **Best for**: Very limited GPU memory (4GB or less)
- **Pros**: Very memory efficient, fast training, stable
- **Cons**: Less sample efficient than PPO
- **Use when**: You want quick results with minimal resources

### DQN (Deep Q-Network)
- **Memory**: 1-2GB GPU RAM
- **Best for**: Discrete action spaces (perfect for Julius)
- **Pros**: Good sample efficiency, proven algorithm
- **Cons**: Needs replay buffer (uses more memory)
- **Use when**: You want good exploration behavior

### PPO (Proximal Policy Optimization)
- **Memory**: 1.5-2.5GB GPU RAM
- **Best for**: Best final performance
- **Pros**: State-of-the-art performance, very stable
- **Cons**: Uses more memory, slower training
- **Use when**: You have enough memory and want best results

## Training Scripts

### train_a2c.py
Train A2C agent with parallel environments.

```bash
python examples/train_a2c.py \
  --data-dir /path/to/caesar3/data \
  --max-ticks 3000 \
  --timesteps 300000 \
  --n-envs 4 \
  --model-path models/julius_a2c
```

**Arguments:**
- `--data-dir`: Path to Caesar III data directory (required)
- `--scenario`: Optional scenario file to load
- `--max-ticks`: Maximum ticks per episode (default: 3000)
- `--timesteps`: Total training timesteps (default: 300000)
- `--n-envs`: Number of parallel environments (default: 4)
- `--model-path`: Where to save the model (default: models/julius_a2c)
- `--load`: Load existing model to continue training
- `--no-gpu`: Force CPU training

**Memory-efficient settings:**
- Network: [128, 128] for policy and value
- N-steps: 5 (very small rollout buffer)
- 4 parallel environments for faster training
- Estimated GPU memory: 500MB-1GB

### train_dqn.py
Train DQN agent with experience replay.

```bash
python examples/train_dqn.py \
  --data-dir /path/to/caesar3/data \
  --max-ticks 3000 \
  --timesteps 200000 \
  --model-path models/julius_dqn
```

**Arguments:** Same as A2C (no --n-envs)

**Memory-efficient settings:**
- Network: [128, 128] Q-network
- Replay buffer: 50,000 transitions (reduced from default 1M)
- Batch size: 32 (small)
- Estimated GPU memory: 1-2GB

### train_ppo_optimized.py
Train PPO agent with optimized hyperparameters.

```bash
python examples/train_ppo_optimized.py \
  --data-dir /path/to/caesar3/data \
  --max-ticks 3000 \
  --timesteps 250000 \
  --n-envs 2 \
  --model-path models/julius_ppo
```

**Arguments:** Same as A2C

**Memory-efficient settings:**
- Network: [128, 128] for policy and value
- N-steps: 1024 (reduced from default 2048)
- Batch size: 64 (small)
- N-epochs: 4 (reduced from default 10)
- 2 parallel environments
- Estimated GPU memory: 1.5-2.5GB

## Environment Wrappers

The training scripts use several wrappers to improve learning efficiency:

### SimplifyObservation
Reduces observation space to only essential metrics:
- Ratings (culture, prosperity, peace, favor)
- Finance (treasury, tax percentage)
- Population (total, sentiment)
- Labor (unemployment)
- Resources (food stocks)

This reduces the observation space from 40+ metrics to ~10, making learning faster.

### NormalizeObservation
Normalizes all values to roughly [-1, 1] range for better neural network training.

### FlattenObservation
Converts nested dictionary observation to flat numpy array. Required for DQN.

### RewardShaping
Adds shaped rewards to guide learning:
- Reward for population growth
- Reward for improving ratings
- Reward for maintaining positive treasury

You can customize wrappers in `julius_gym/wrappers.py` or use `make_efficient_env()`:

```python
from julius_gym.wrappers import make_efficient_env

env = make_efficient_env(
    data_directory="/path/to/data",
    max_ticks=3000,
    simplify=True,      # Use simplified observation space
    normalize=True,     # Normalize values
    flatten=True,       # Flatten to Box space (for DQN)
    shape_rewards=True, # Add reward shaping
)
```

## Training Tips

### 1. Start with A2C
If you're limited by memory, start with A2C. It's fast and memory efficient.

```bash
python examples/train_a2c.py --data-dir /path/to/data --timesteps 300000
```

### 2. Monitor Training
All scripts log to TensorBoard:

```bash
tensorboard --logdir=./tensorboard
```

Then open http://localhost:6006 in your browser.

### 3. Checkpoint Regularly
All scripts automatically save checkpoints every 10,000 steps to `models/checkpoints/`.

### 4. Adjust Episode Length
If episodes are too long and using too much memory, reduce `--max-ticks`:

```bash
python examples/train_a2c.py --data-dir /path/to/data --max-ticks 2000
```

### 5. Reduce Parallel Environments
If running out of memory, reduce `--n-envs`:

```bash
python examples/train_a2c.py --data-dir /path/to/data --n-envs 2
```

### 6. CPU Training
If GPU memory is too limited, train on CPU (will be slower):

```bash
python examples/train_a2c.py --data-dir /path/to/data --no-gpu
```

## Evaluation

All training scripts automatically evaluate the trained agent after training. To evaluate a saved model separately:

```python
from stable_baselines3 import A2C
from julius_gym.wrappers import make_efficient_env
from examples.train_utils import evaluate_agent, print_evaluation_stats

# Load model
model = A2C.load("models/julius_a2c")

# Create environment
env = make_efficient_env(
    data_directory="/path/to/data",
    max_ticks=3000,
    simplify=True,
    normalize=True,
    flatten=True,
)

# Evaluate
stats = evaluate_agent(model, env, n_eval_episodes=10)
print_evaluation_stats(stats)
```

## Comparing Agents

Use `train_utils.py` to compare different trained agents:

```python
from stable_baselines3 import A2C, DQN, PPO
from julius_gym.wrappers import make_efficient_env
from examples.train_utils import compare_agents

models = {
    "A2C": A2C.load("models/julius_a2c"),
    "DQN": DQN.load("models/julius_dqn"),
    "PPO": PPO.load("models/julius_ppo"),
}

env = make_efficient_env(data_directory="/path/to/data")

compare_agents(models, env, n_eval_episodes=10)
```

## Hyperparameter Tuning

If default hyperparameters don't work well, you can tune them. Here are the most important ones:

### Learning Rate
- Default: 7e-4 (A2C), 1e-4 (DQN), 3e-4 (PPO)
- If training is unstable: Lower it (1e-4 or 1e-5)
- If training is too slow: Raise it (1e-3)

### Network Size
- Default: [128, 128]
- For 2GB GPU: Try [64, 64]
- For more capacity: Try [256, 256] (but uses more memory)

### Batch Size
- Default: 32-64
- Smaller batch = less memory but noisier gradients
- Larger batch = more memory but more stable

## Troubleshooting

### Out of Memory (OOM) Error
1. Reduce `--n-envs` to 1 or 2
2. Reduce `--max-ticks` to 2000 or 1500
3. Switch to A2C (most memory efficient)
4. Reduce network size to [64, 64]
5. Use CPU training with `--no-gpu`

### Training is Very Slow
1. Increase `--n-envs` to 4 or 8
2. Use GPU training (remove `--no-gpu`)
3. Switch to A2C (fastest algorithm)
4. Reduce `--max-ticks` for shorter episodes

### Agent Not Learning
1. Increase `--timesteps` (try 500k or 1M)
2. Try different algorithm (PPO often works best)
3. Check TensorBoard for signs of learning
4. Adjust reward shaping in `wrappers.py`
5. Try without SimplifyObservation wrapper

### Agent Performs Well in Training but Poorly in Evaluation
1. This is overfitting. Try:
   - Add more exploration (increase `ent_coef`)
   - Train for fewer timesteps
   - Use different scenarios for evaluation

## Advanced Usage

### Custom Reward Function

Edit `wrappers.py` to customize the reward function:

```python
class CustomRewardShaping(gym.Wrapper):
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        # Add your custom rewards here
        if obs["ratings"]["culture"] > 80:
            reward += 1.0  # Bonus for high culture

        return obs, reward, terminated, truncated, info
```

### Custom Network Architecture

Pass `policy_kwargs` to the model:

```python
from stable_baselines3 import PPO
import torch.nn as nn

model = PPO(
    "MlpPolicy",
    env,
    policy_kwargs=dict(
        net_arch=[256, 256, 128],  # 3-layer network
        activation_fn=nn.ReLU,  # Use ReLU instead of Tanh
    ),
)
```

### Multi-Scenario Training

Train on multiple scenarios by loading different scenario files:

```python
from stable_baselines3.common.vec_env import SubprocVecEnv

scenarios = [
    "/path/to/scenario1.map",
    "/path/to/scenario2.map",
    "/path/to/scenario3.map",
]

def make_env(scenario):
    def _init():
        return make_efficient_env(
            data_directory="/path/to/data",
            scenario_file=scenario,
        )
    return _init

env = SubprocVecEnv([make_env(s) for s in scenarios])
model = PPO("MlpPolicy", env)
model.learn(total_timesteps=1000000)
```

## Expected Results

With 300k-500k timesteps of training, you should see:

### A2C
- Population: 1000-2000
- Average rating: 40-60
- Treasury: Positive (>0)
- Training time: ~1-2 hours on 4GB GPU

### DQN
- Population: 1500-2500
- Average rating: 50-70
- Treasury: Positive (>500)
- Training time: ~2-3 hours on 4GB GPU

### PPO
- Population: 2000-3000
- Average rating: 60-80
- Treasury: Positive (>1000)
- Training time: ~3-4 hours on 4GB GPU

These are rough estimates and will vary significantly based on the scenario and training settings.

## Further Reading

- [Stable-Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [RL Training Tips](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [A2C/A3C Paper](https://arxiv.org/abs/1602.01783)
- [DQN Paper](https://arxiv.org/abs/1312.5602)
