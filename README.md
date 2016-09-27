This is the source repository for Roboto: Google’s signature family
of fonts, the default font on Android and Chrome OS, and the
recommended font for Google’s visual language, Material Design.

It also contains the toolchain used in creating Roboto.

The font family supports all Latin, Cyrillic, and Greek characters in
Unicode 7.0, as well as the currency symbol for the Georgian lari, to
be published in Unicode 8.0.

The fonts are currently available in eighteen different styles.

[A subset of an earlier version of Roboto](https://www.google.com/fonts/specimen/Roboto) is available from Google Fonts, and can be used as a web font.

## Setup

Create a clean directory for Roboto:

```bash
mkdir -p $HOME/roboto-src
cd $HOME/roboto-src
```

Download the Roboto tools and sources:

```bash
git clone https://github.com/google/roboto.git
```

Create a virtual Python environment (optional but recommended):

```bash
pip install --user virtualenv
virtualenv roboto-env
source roboto-env/bin/activate
```

Download and install the dependencies:

```bash
cd roboto
pip install -r requirements.txt
```

#### Optional additional setup for running tests

Download the latest tarball release of HarfBuzz
[here](http://www.freedesktop.org/wiki/Software/HarfBuzz/) and extract it into
the **home** directory as `$HOME/harfbuzz` (alternatively, you can download the
latest source from GitHub via
`git clone https://github.com/behdad/harfbuzz.git`).

Build and install HarfBuzz:

```bash
cd $HOME/harfbuzz
./configure
make
sudo make install
cd $HOME/roboto-src/
```

On Ubuntu (or other distributions of GNU/Linux, using the appropriate package
manager), make sure eog is installed:

```bash
sudo apt-get install eog
```

## Run

```bash
cd roboto
make
```
