# Running Brutus

Brutus requires the original Caesar 3 files to run. This can be an old CD-ROM version, or a digital copy
from either [GOG](https://www.gog.com/game/caesar_3) or
[Steam](https://store.steampowered.com/app/517790/Caesar_3/).

Note that there are [command line options](#command-line-options) which are available to all platforms.

If you have the high-quality MP3 music files that were once available for download from the Sierra Website,
the game supports playing them.

Please check [MP3 support](mp3_support.md) for details.

## Linux/BSD

### GOG version with InnoExtract

If you bought the GOG edition, you can download the offline installer exe, and use
[InnoExtract](http://constexpr.org/innoextract/) to extract the game files:

1. Build Brutus or install using your package manager
2. [Install](http://constexpr.org/innoextract/install) `innoextract` for your distribution
3. Download the Caesar 3 offline installer exe from GOG
4. Run the following command to extract the game files to a new `app` directory:

        $ innoextract -m setup_caesar3_2.0.0.9.exe

5. Move the `julius` executable to the extracted `app` directory and run from there, OR run Julius
   with the path to the game files as parameter:

        $ julius path-to-app-directory

Note that your user requires write access to the directory containing the game files, since the
saved games are also stored there.

### Using WINE

Another option is to get the game files by installing Caesar 3 using [WINE](https://www.winehq.org/):

1. Build Brutus
2. Install Caesar 3 using WINE, take note where the game is installed
3. Run Brutus with the path where the game is installed:

        $ julius path-to-c3-directory

## Command line options

Brutus supports some command-line options. Its usage is:

    $ julius [ARGUMENTS] [DATA_DIR]

`[ARGUMENTS]` can be the following:

* `--anneal`

    Optional. As soon as the game has loaded, start annealing the map area specified in `src/platform/julius.c::main_loop`.

* `--display-scale NUMBER`

    Optional. Scales the entire Julius application by a factor of `NUMBER`. Useful for high-dpi systems.

    `NUMBER`can be any number between `0.5` and `5`. The default is `1`.

* `--cursor-scale NUMBER`

    Optional. Scales the mouse cursor by a factor of `NUMBER`. Cursor scaling is independent of display scaling.

    `NUMBER` can only be set to `1`, `1.5` or `2`. The default is `1`.

`[DATA_DIR]` Is the location of the Caesar 3 asset files.

If `[DATA_DIR]` is not provided, Brutus will try to load the asset files from the directory where it is installed.

If the files are not found, it will check if a previous valid directory was stored in the internal preferences
and load the asset files from that directory.

If Brutus still fails to load the assets, it will ask you to point to a valid directory.
