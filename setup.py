#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dronekit_sitl',
      version='3.1.0',
      description='DroneKit library to run SITL (simulation environment)',
      author='Tim Ryan',
      author_email='tim@3drobotics.com',
      url='https://github.com/dronekit/dronekit-sitl/',
      install_requires = [
        'psutil>=3.0',
        'dronekit>=2.0.0b6',
        'six>=1.10'
      ],
      package_data={
        'dronekit_sitl': ['*.parm'],
      },
      entry_points={
          'console_scripts': [
              'dronekit-sitl = dronekit_sitl.__init__:main'
          ]
      },
      packages = ['dronekit_sitl', 'dronekit_sitl.pysim'],
      )

# Delete home dir scripts for fresh install, just in case.
import shutil
import os
sitl_target = os.path.normpath(os.path.expanduser('~/.dronekit/sitl'))
try:
  shutil.rmtree(sitl_target)
  print('Cleared cached SITL binaries.')
except:
  pass
