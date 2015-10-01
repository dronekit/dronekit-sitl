#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dronekit_sitl',
      version='2.1.0',
      description='Runs SITL as part of DroneKit.',
      author='Tim Ryan',
      author_email='tim@3drobotics.com',
      url='https://github.com/tcr3dr/dronekit-sitl-runner/',
      install_requires = ['psutil>=3.0'],
      entry_points={
          'console_scripts': [
              'dronekit-sitl = dronekit.sitl.__main__'
          ]
      },
      packages = ['dronekit', 'dronekit.sitl'],
      namespace_packages = ['dronekit']
      )
