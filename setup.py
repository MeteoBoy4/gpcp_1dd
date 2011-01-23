#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='gpcp',
      author='Connor McCoy',
      author_email='connormccoy@gmail.com',
      version='2011.01.23',
      description='Tools for working with GPCP 1DD precipitation data.',
      packages=find_packages(),
      scripts=['gpcp/scripts/read_onedd_headers.py',
               'gpcp/scripts/onedd_to_delim.py'],
      requires=['argparse']
      )
