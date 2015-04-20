# Setup

#### Create a clean directory for roboto:

```bash
mkdir -p $HOME/roboto-src
cd $HOME/roboto-src
```

#### Download the code and dependencies:

```bash
git clone https://github.com/google/roboto.git
git clone https://github.com/behdad/fonttools.git
git clone https://github.com/robofab-developers/robofab.git
git clone https://github.com/jamesgk/feaTools.git
git clone https://github.com/typemytype/booleanOperations.git
```

download [Cython](http://cython.org/#download) and extract it into
the current directory.

##### For OTF generation:

```bash
git clone https://github.com/typesupply/ufo2fdk.git
```

To build the FDK yourself:

```bash
git clone https://github.com/adobe-type-tools/afdko.git
```

download the latest version of Python 2.7
[here](https://www.python.org/downloads/) and extract it into the current
directory.

If you're not building the FDK yourself, download the pre-built version
[here](http://www.adobe.com/devnet/opentype/afdko.html) and unzip it into the
current directory.

##### For TTF generation, on Ubuntu:

```bash
sudo apt-get install fontforge python-fontforge
```

##### For post-production:

```bash
git clone https://code.google.com/p/noto/
git clone https://github.com/rougier/freetype-py.git
```

download the latest tarball release of HarfBuzz [here](http://www.freedesktop.org/wiki/Software/HarfBuzz/) and extract it into the current directory.

#### Install dependencies:

```bash
cd fonttools
sudo python setup.py install
cd ../robofab
sudo python setup.py install
cd ../feaTools
git checkout expanded
sudo python setup.py install
cd ../Cython-0.22
sudo python setup.py install
cd ../booleanOperations/cppWrapper
sudo python setup.py build_ext --inplace
cp pyClipper.so ../Lib/booleanOperations
cd ..
sudo python setup.py install
cd ..
```

##### For OTF generation:

```bash
cd ufo2fdk
sudo python setup.py install
cd ..
```

If building the FDK yourself, follow the instructions in `afdko/FDK/FDK Build Notes.txt`:

```bash
cd Python-2.7
./configure --prefix=AFDKOPythonBuild
make install
mv AFDKOPythonBuild ../afdko/FDK/Tools/osx/Python
cd ../fonttools
sudo ../afdko/FDK/Tools/osx/Python/bin/python setup.py install
cd ../afdko/FDK/Tools/Programs
./BuildAll.sh
cd ../..
./FinishInstallOSX
cd ../..
```

Otherwise:

```bash
cd FDK
./FinishInstallOSX
cd ..
```

In either case, use whatever install scripts and directory
(`FinishInstall`[`OSX`|`Linux`|`Windows.cmd`],
`BuildAll`[`.sh`|`Linux.sh`|`.cmd`],
`FDK/Tools/`[`osx`|`linux`|`win`]) are appropriate for your platform (more
detailed information can be found in `FDK/Read_Me_First.html`).

##### For post-production:

```bash
cd harfbuzz
./configure
make
sudo make install
cd ../noto
sudo python setup.py install
cd ../freetype-py
sudo python setup.py install
cd ..
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
- An expanded version of Tal Leming's feaTools
  (https://github.com/jamesgk/feaTools/tree/expanded), for feature handling.
- BooleanOperations (https://github.com/typemytype/booleanOperations), for
  glyph overlap removal.
  - (requires Cython to install: http://cython.org/)

## OTF Generation
OTF generation depends on:

- ufo2fdk (https://github.com/typesupply/ufo2fdk)
- Open-source portions of the AFDKO
  (https://github.com/adobe-type-tools/afdko/releases)

The AFDKO from GitHub can be time consuming to setup. It is easier to just use
the variety which includes closed-source tools
(http://www.adobe.com/devnet/opentype/afdko.html), though these closed-source
portions are not used to build Roboto.

## TTF Generation
TTF generation depends on:

- FontForge (https://github.com/fontforge/fontforge)

Whose Python interface should be availabe on Ubuntu by default via `apt-get
install fontforge python-fontforge`.

## Post-Production
Post-production scripts (most of the code outside of the `fontbuild` directory,
e.g. for testing output) depend on:

- The nototools module, installed as part of Noto
  (https://code.google.com/p/noto/)
  - (Noto subsequently depends on HarfBuzz: https://github.com/behdad/harfbuzz)
- freetype-py (https://github.com/rougier/freetype-py)
