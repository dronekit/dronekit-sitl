#!PYTHONUNBUFFERED=1 /usr/bin/python

import sys, os
import subprocess, string, time
import json
import tarfile,sys
import urllib
import os

self = os.path.dirname(os.path.realpath(__file__))
 
target = 'linux'
if sys.platform == 'darwin':
    target = 'osx'

if not os.path.isdir(self + '/sitl'):
    print "Downloading SITL."
    
    testfile = urllib.URLopener()
    testfile.retrieve('http://dronekit-sitl-binaries.s3.amazonaws.com/copter/sitl-' + target + '-v3.4-dev.tar.gz', self + '/sitl.tar.gz')

    tar = tarfile.open(self + '/sitl.tar.gz')
    tar.extractall(path=self + '/sitl')
    tar.close()

    print 'Extracted.'
else:
    print "SITL already Downloaded."


env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'

subprocess.Popen([self + '/sitl/ArduCopter.elf', '-S', '-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353'], bufsize=1, env=env, universal_newlines=True)

p = subprocess.Popen(['mavproxy.py', '--master', 'tcp:127.0.0.1:5760', '--sitl', '127.0.0.1:5501', '--out', '127.0.0.1:14550', '--out', '127.0.0.1:14551'], stdin=subprocess.PIPE)

while True:
    input = sys.stdin.read(1)
    if not input:
        break
    p.stdin.write(input)
    p.stdin.flush()
