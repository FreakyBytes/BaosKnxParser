#!/usr/bin/env python3

from distutils.core import setup

setup(name='Baos KNX parser',
      version='0.1.0',
      description='simple Python library to parse BAOS KNX packages',
      author='Martin Peters',
      author_email='',
      url='https://github.com/FreakyBytes/',
      packages=['baos_knx_parser', ],
      install_requires=[
          'bitstruct>=3.3,<3.4',
      ]
      )
