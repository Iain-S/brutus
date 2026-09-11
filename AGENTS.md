# Brutus contributor guide

`brutus` is a fork of Julius, an open-source Caesar III reimplementation. It
has two distinct build paths:

- the normal graphical Julius application;
- a headless shared library and Python Gymnasium package for reinforcement
  learning.

Treat `<REPO_ROOT>` below as an **absolute** path to this checkout, for
example `C:\\work\\brutus` or `/work/brutus`. Do not add machine-specific paths
to source files, documentation, or commits.

## Repository orientation

- Main C application: `src/`, root `CMakeLists.txt`.
- Python Gymnasium package: `python/julius_gym/`.
- Gymnasium C API: `src/gymnasium/`.
- Main-build documentation: `doc/BUILDING.md` (with upstream detail linked
  there).
- Gym-specific usage and API documentation: `python/README.md` and
  `python/examples/README.md`.

## Normal Julius build

The graphical build requires CMake, a C compiler, SDL2, and SDL2_mixer.
libpng is optional: the CMake configuration falls back to bundled PNG/zlib
sources when it is unavailable. Follow `doc/BUILDING.md` for platform-specific
packages and flags.

Always configure from a separate build directory. Do not reuse a CMake build
directory after moving the checkout, changing generators, or switching between
graphical and headless builds: `CMakeCache.txt` records absolute source and
toolchain paths.

```powershell
cmake -S <REPO_ROOT> -B <REPO_ROOT>\build-gui
cmake --build <REPO_ROOT>\build-gui --parallel
```

On Windows with MinGW Makefiles, choose the generator explicitly if needed:

```powershell
cmake -S <REPO_ROOT> -B <REPO_ROOT>\build-gui -G "MinGW Makefiles"
cmake --build <REPO_ROOT>\build-gui --parallel
```

## Training Gym build

The training integration is a headless C shared library loaded by Python via
`ctypes`. Configure it separately from the graphical application:

```powershell
cmake -S <REPO_ROOT> -B <REPO_ROOT>\build-gym `
  -DHEADLESS_BUILD=ON `
  -DBUILD_GYMNASIUM_LIB=ON
cmake --build <REPO_ROOT>\build-gym --target julius_gym --parallel
```

Use the same explicit MinGW generator as above when that is the installed
toolchain. The output is `libjulius_gym.dll` on Windows,
`libjulius_gym.so` on Linux, and normally `libjulius_gym.dylib` on macOS.

### Python environment and package

Use the dedicated Conda environment recorded in the ignored `local.md` as the
canonical Brutus training environment. Treat `<BRUTUS_CONDA_PREFIX>` as its
absolute Conda prefix; do not put a developer-specific prefix in tracked
documentation. Activate it and install the package in editable mode:

```powershell
conda activate <BRUTUS_CONDA_PREFIX>
python -m pip install -e <REPO_ROOT>\python
python -m pip install -r <REPO_ROOT>\python\requirements-examples.txt
```

`requirements-examples.txt` supplies Stable-Baselines3 for the training
examples. The package itself requires Gymnasium and NumPy. Use
`python -m pip`, rather than a bare `pip`, to ensure installation targets the
active virtual environment.

`<REPO_ROOT>\python\venv` is a legacy duplicate, not the default environment
for active training work. Do not rely on it in new scripts or instructions. If
using an alternative environment temporarily, verify its actual interpreter:

```powershell
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

Do not commit any Conda environment, virtual environment, or local environment
configuration.

### Running a training smoke test

Training needs an installed copy of the original Caesar III data. Supply its
directory and the library explicitly. Explicit `--lib-path` is especially
important on Windows: the current Python auto-discovery list only names `.so`
paths.

```powershell
Set-Location <REPO_ROOT>\python
.\venv\Scripts\Activate.ps1
python .\examples\train_a2c.py `
  --data-dir <ABSOLUTE_CAESAR3_DATA_DIR> `
  --lib-path <REPO_ROOT>\build-gym\libjulius_gym.dll `
  --timesteps 100 --n-envs 1 --no-gpu
```

The data directory must contain the original game data (including `c3.eng`).
Do not commit the game files, trained models, run outputs, logs, or personal
local configuration.

## Validation and change hygiene

- For a C-only Gym smoke check, load the resulting shared library with Python
  `ctypes`; a full environment reset additionally needs the Caesar III data.
- `python -m pip check` validates installed Python requirements.
- Run focused Python tests or scripts with explicit `--data-dir` and
  `--lib-path`; many existing test scripts intentionally require both.
- Preserve unrelated staged, unstaged, and untracked work. Review
  `git status --short` before staging or committing.
