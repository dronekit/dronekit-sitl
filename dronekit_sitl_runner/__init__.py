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
    if sys.platform == 'windows':
        return 'win'
    return 'linux'

def reset():
    # delete local sitl installations
    shutil.rmtree(sitl_target + '/')
    print('SITL directory cleared.')
