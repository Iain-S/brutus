# Building Brutus

If you have experience in compiling from source, these are the basic instructions.

To build Brutus, you'll need:

- `git`
- a compiler (`gcc` is known to work)
- `cmake`
- `SDL2`
- `SDL2_mixer`
- `GSL` the GNU Scientific Library

After cloning the repo, run the following commands to build Brutus with debug symbols:

```sh
mkdir debug && cd debug
cmake ..
make
```

This results in a `julius` executable. See [Running Brutus](RUNNING.md) for instructions on how to run it.

--------------------------------------------------

For detailed building instructions, please check out [Building for Linux](building_linux.md).
