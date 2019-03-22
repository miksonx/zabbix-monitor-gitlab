#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Setup file installing python script
"""
__author__ = "Aytunc Beken"
__copyright__ = "Copyright (C) 2019 Aytunc Beken"
__version__ = "0.1"
__license__ = "MIT"
__maintainer__ = "Aytunc Beken"
__email__ = "aytuncbeken.ab@gmail.com"
__status__ = "Production"

from setuptools import setup, find_packages

setup(name="zabbix_gitlab",
      version='1.0',
      python_requires='>=2.7',
      description='Zabbix_Monitor_Gitlab Python Setup Script',
      author='Aytunc Beken',
      author_email='aytuncbeken.ab@gmail.com',
      packages=find_packages(),
      install_requires=['python-gitlab'],
      entry_points={
          'console_scripts': ['zabbix_gitlab=lib.zabbix_gitlab:main']
      })
