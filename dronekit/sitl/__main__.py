#!/usr/bin/python

<<<<<<< HEAD
import sys
from dronekit.sitl import main

main(sys.argv[1:])
=======
from __future__ import print_function
import re
import sys
import os
import subprocess
import string
import time
import json
import tarfile
import sys
import urllib
import urllib2
import os
import json
import shutil
import atexit
import select
from subprocess import Popen, PIPE
from os.path import expanduser
from threading import Thread
from Queue import Queue, Empty
from dronekit.sitl import detect_target, version_list, reset, SITL

system = 'copter'
target = detect_target()
version = '3.2.1'

args = sys.argv[1:]
if len(args) > 0 and args[0] == '--list':
    versions = version_list()
    for system in [system for system, v in versions.iteritems()]:
        keys = [k for k, v in versions[system].iteritems()]
        keys.sort()
        for k in keys:
            print(system + '-' + k)
    sys.exit(0)

if len(args) > 0 and args[0] == '--help':
    print('You can look up help for a particular vehicle, e.g.:', file=sys.stderr)
    print('  dronekit-sitl copter --help')
    print('  dronekit-sitl plane-3.3 --help')
    sys.exit(1)

if len(args) > 0 and args[0] == '--reset':
    reset()
    sys.exit(0)

if len(args) < 1 or not re.match(r'^(copter|plane)(-v?.+)?', args[0]):
    print('Please specify one of:', file=sys.stderr)
    print('  dronekit-sitl --list', file=sys.stderr)
    print('  dronekit-sitl --reset', file=sys.stderr)
    print('  dronekit-sitl <copter(-version)>', file=sys.stderr)
    print('  dronekit-sitl <plane(-version)>', file=sys.stderr)
    sys.exit(1)

if re.match(r'^copter-v?(.+)', args[0]):
    system = 'copter'
    version = re.match(r'^copter-v?(.+)', args[0]).group(1)
if re.match(r'^plane-v?(.+)', args[0]):
    system = 'plane'
    version = re.match(r'^plane-v?(.+)', args[0]).group(1)
args = args[1:]

print('os: %s, apm: %s, release: %s' % (target, system, version))

sitl = SITL(system, version)
sitl.download(target, verbose=True)
sitl.launch(args, verbose=True)
# sitl.block_until_ready(verbose=True)
code = sitl.complete(verbose=True)

if code != 0:
    sys.exit(code)
>>>>>>> b22b57d... Adds --help flag and missing files.
