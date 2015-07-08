#!/usr/bin/env python

from setuptools import setup

setup(name='Dronekit SITL Runner',
      version='1.3.0',
      description='',
      author='Tim Ryan',
      author_email='tim@3drobotics.com',
      url='https://github.com/tcr3dr/dronekit-sitl-runner/',
      entry_points={
          'console_scripts': [
              'dronekit-sitl = dronekit_sitl_runner.__init__:main'
          ]
      },
      packages=['dronekit_sitl_runner'],
      )
