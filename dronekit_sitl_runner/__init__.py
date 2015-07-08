#!/usr/bin/python

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
from subprocess import Popen
from os.path import expanduser

sitl_host = 'http://d3jdmgrrydviou.cloudfront.net'
sitl_target = expanduser('~/.dronekit/sitl')

def version_list():
    sitl_list = '{}/versions.json'.format(sitl_host)

    req = urllib2.Request(sitl_list, headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    raw = urllib2.urlopen(req).read()
    versions = json.loads(raw)
    return versions

def download(system, version, target):
    sitl_file = "{}/{}/sitl-{}-v{}.tar.gz".format(sitl_host, system, target, version)

    if not os.path.isdir(sitl_target + '/' + system + '-' + version):
        print("Downloading SITL from %s" % sitl_file)

        if not os.path.isdir(sitl_target):
            os.makedirs(sitl_target)

        testfile = urllib.URLopener()
        testfile.retrieve(sitl_file, sitl_target + '/sitl.tar.gz')

        tar = tarfile.open(sitl_target + '/sitl.tar.gz')
        tar.extractall(path=sitl_target + '/' + system + '-' + version)
        tar.close()

        print('Extracted.')
    else:
        print("SITL already Downloaded.")

def launch(system, version, args):
    elfname = {
        "copter": "ArduCopter.elf",
        "plane": "ArduPlane.elf",
    }
    args = ['./' + system + '-' + version + '/' + elfname[system]] + args
    print('Execute:', str(args))

    p = Popen(args, cwd=sitl_target)
    p.communicate()

def detect_target():
    if sys.platform == 'darwin':
        return 'osx'
    if sys.platform.startswith('win'):
        return 'win'
    return 'linux'

def reset():
    # delete local sitl installations
    shutil.rmtree(sitl_target + '/')
    print('SITL directory cleared.')

def main():
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

    download(system, version, target)
    launch(system, version, args)
