#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  FreeType high-level python API - copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
# -----------------------------------------------------------------------------
from distutils.core import setup
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
  long_description = f.read()

setup( name        = 'freetype-py',
       version     = '0.5.1',
       description = 'Freetype python bindings',
       long_description = long_description,
       author      = 'Nicolas P. Rougier',
       author_email= 'Nicolas.Rougier@inria.fr',
       url         = 'https://github.com/rougier/freetype-py',
       packages    = ['freetype', 'freetype.ft_enums'],
       classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: X11 Applications',
          'Environment :: MacOS X',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Graphics',
          ],
     )
