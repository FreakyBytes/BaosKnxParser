#!/usr/bin/env python3

from distutils.core import setup

setup(name='BaosKnxParser',
      version='0.5.0',
      description='simple Python library to parse BAOS KNX packages',
      author='Martin Peters',
      author_email='',
      url='https://github.com/FreakyBytes/',
      packages=['baos_knx_parser', ],
      install_requires=[
          'bitstruct>=3.5,<3.6',
      ]
      )
