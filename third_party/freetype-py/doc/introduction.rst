============
Introduction
============

To be able to use freetype python, you need the freetype library version 2
installed on your system.


Pre-requisites
==============

You need to have the Freetype library installed on your system to be able to use
the freetype python bindings.

.. warning::

   If you don't compile the Freetype library yourself, chances are subpixel
   anti-aliasing will be disabled due to patent problems. Have a look at
   `Freetype FAQ <http://www.freetype.org/freetype2/docs/ft2faq.html#builds>`_
   to know how to enable it.

Mac users
---------
Freetype should be already installed on your system. If not, either install it
using `homebrew <http://brew.sh>`_ or compile it and place the library binary
file in '/usr/local/lib'.

Linux users
-----------
Freetype should be already installed on your system. If not, either install
relevant package from your package manager or compile from sources and place
the library binary file in '/usr/local/lib'.

Window users
------------
You can try to install a window binaries available from the Freetype site or
you can compile it from sources. In such a case, make sure the resulting
library binaries is named 'Freetype.dll' (and not something like
Freetype245.dll) and make sure to place a copy in Windows/System32 directory.


Installation
============

The easiest way to install freetype-pu is to use pip::

  pip install freetype-py

Or you can get the latest version from git and install yourself::

  git clone https://github.com/rougier/freetype-py.git
  cd freetype-py
  python setup.py install
