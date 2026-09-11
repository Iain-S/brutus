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

Activate the venv with `.\venv\Scripts\Activate.ps1`.

Run some training with 

```shell
python .\examples\train_a2c.py --data-dir C:\path\to\Caesar3\ --lib-path C:\path\to\build\libjulius_gym.dll
 ```