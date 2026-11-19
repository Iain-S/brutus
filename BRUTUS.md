# Brutus

See also `python/README.md`.

## Build

Install some external dependencies in `ext/`.

Make a directory with `mkdir build` and `cd build`.

Build with

```shell
cmake -G "MinGW Makefiles" -DCMAKE_MAKE_PROGRAM=mingw32-make -DBUILD_GYMNASIUM_LIB=ON -DHEADLESS_BUILD=ON -DBUILD_EXTERNAL_DEPS=ON ..
```

followed by `mingw32-make.exe julius_gym`.

## Run

Change out of `build/` and into `python/` with `cd ../python`.

Use the dedicated Conda training environment (the local absolute prefix is
recorded in ignored `local.md`):

```powershell
conda activate <BRUTUS_CONDA_PREFIX>
python -m pip install -e <REPO_ROOT>\python
```

`python\venv` is a legacy duplicate and is not the default environment for
new work.

Run some training with 

```shell
python .\examples\train_a2c.py --data-dir C:\path\to\Caesar3\ --lib-path C:\path\to\build\libjulius_gym.dll
 ```
