#!/usr/bin/env python

from distutils.core import setup

setup(name='gpcp',
      author='Connor McCoy <connormccoy@gmail.com>',
      version='2011-01-14',
      description='Tools for working with GPCP 1DD precipitation data.',
      package_dir={'gpcp': 'gpcp'},
      packages=['gpcp'],
      scripts=['gpcp/scripts/read_onedd_headers.py',
               'gpcp/scripts/onedd_to_delim.py'],
      requires=['argparse']
      )
