This is the source repository for Roboto: Google’s signature family
of fonts, the default font on Android and ChromeOS, and the
recommended font for Google’s visual language, Material Design.

It also contains the toolchain used in creating Roboto.

The font family supports all Latin, Cyrillic, and Greek characters in
Unicode 7.0, as well as the currency symbol for the Georgian lari, to
be published in Unicode 8.0.

The fonts are currently available in eighteen different styles.

[A subset of an earlier version of Roboto](https://www.google.com/fonts/specimen/Roboto) is available from Google Fonts, and can be used as a web font.

## Setup

#### Create a clean directory for roboto:

```bash
mkdir -p $HOME/roboto-src
cd $HOME/roboto-src
```

#### Download the code and dependencies:

```bash
git clone https://github.com/google/roboto.git
git clone https://github.com/behdad/fonttools.git
git clone https://github.com/googlei18n/cu2qu.git
git clone https://github.com/googlei18n/ufo2ft.git
git clone https://github.com/robofab-developers/robofab.git
git clone https://github.com/typesupply/feaTools.git
git clone https://github.com/typemytype/booleanOperations.git
```

download [Cython](http://cython.org/#download) and extract it into
the current directory. On Ubuntu, Cython can also be downloaded and installed
via:

```bash
sudo apt-get install cython
```

##### For post-production:

```bash
git clone https://github.com/googlei18n/nototools
git clone https://github.com/rougier/freetype-py.git
```

download the latest tarball release of HarfBuzz
[here](http://www.freedesktop.org/wiki/Software/HarfBuzz/) and extract it into
the **home** directory as `$HOME/harfbuzz` (alternatively, you can download the
latest source from GitHub via
`git clone https://github.com/behdad/harfbuzz.git`).

#### Install dependencies:

You can install the necessary modules at the sytem level:

```bash
cd fonttools
sudo python setup.py install
cd ../cu2qu
sudo python setup.py install
cd ../ufo2ft
sudo python setup.py install
cd ../robofab
sudo python setup.py install
cd ../feaTools
sudo python setup.py install
cd ../Cython-0.22
sudo python setup.py install
cd ../booleanOperations
sudo python setup.py install
cd ..
```

Or set `$PYTHONPATH` locally before running `make`:

```bash
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/fonttools/Lib"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/cu2qu/Lib"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/ufo2ft/Lib"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/robofab/Lib"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/feaTools/Lib"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/booleanOperations/Lib"
```

##### For post-production:

```bash
cd $HOME/harfbuzz
./configure
make
sudo make install
cd $HOME/roboto-src/
```

Install python modules to system:

```bash
cd noto
sudo python setup.py install
cd ../freetype-py
sudo python setup.py install
cd ..
```

Or:

```bash
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/noto"
PYTHONPATH="$PYTHONPATH:$HOME/roboto-src/freetype-py"
```

On Ubuntu (or other distributions of GNU/Linux, using the appropriate package
manager), make sure eog is installed:

```bash
sudo apt-get install eog
```

#### Running the toolchain:

```bash
cd roboto
make
```

## Dependencies
The Roboto build toolchain depends on:

- FontTools (https://github.com/behdad/fonttools)
- RoboFab (https://github.com/robofab-developers/robofab)
- NumPy and SciPy (http://www.numpy.org/)
- feaTools (https://github.com/typesupply/feaTools.git), for feature handling.
- BooleanOperations (https://github.com/typemytype/booleanOperations), for
  glyph overlap removal.
  - (requires Cython to install: http://cython.org/)

## OTF/TTF Generation
OTF generation depends on:

- ufo2ft (https://github.com/googlei18n/ufo2ft)
- cu2qu (https://github.com/googlei18n/cu2qu)

## Post-Production
Post-production scripts (most of the code outside of the `fontbuild` directory,
e.g. for testing output) depend on:

- The nototools module (https://github.com/googlei18n/nototools)
  - (Noto subsequently depends on HarfBuzz: https://github.com/behdad/harfbuzz)
- freetype-py (https://github.com/rougier/freetype-py)
- eog (https://wiki.gnome.org/Apps/EyeOfGnome)
