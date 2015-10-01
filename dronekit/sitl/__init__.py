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
import atexit
import select
import psutil
from subprocess import Popen, PIPE
from os.path import expanduser
from threading import Thread
from Queue import Queue, Empty

sitl_host = 'http://d3jdmgrrydviou.cloudfront.net'
sitl_target = os.path.normpath(expanduser('~/.dronekit/sitl'))

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass
    try:
        process.kill()
    except psutil.NoSuchProcess:
        pass

class NonBlockingStreamReader:
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    break

        self._t = Thread(target = _populateQueue,
                         args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                               timeout = timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception):
    pass

def version_list():
    sitl_list = '{}/versions.json'.format(sitl_host)

    req = urllib2.Request(sitl_list, headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    raw = urllib2.urlopen(req).read()
    versions = json.loads(raw)
    return versions

def download(system, version, target, verbose=False):
    sitl_file = "{}/{}/sitl-{}-v{}.tar.gz".format(sitl_host, system, target, version)

    if not os.path.isdir(sitl_target + '/' + system + '-' + version):
        if verbose:
            print("Downloading SITL from %s" % sitl_file)

        if not os.path.isdir(sitl_target):
            os.makedirs(sitl_target)

        testfile = urllib.URLopener()
        testfile.retrieve(sitl_file, sitl_target + '/sitl.tar.gz')

        tar = tarfile.open(sitl_target + '/sitl.tar.gz')
        tar.extractall(path=sitl_target + '/' + system + '-' + version)
        tar.close()

        if verbose:
            print('Extracted.')
    else:
        if verbose:
            print("SITL already Downloaded.")

class SITL():
    def __init__(self, system, version):
        self.system = system
        self.version = version
        self.p = None

    def download(self, target=None, verbose=False):
        if target == None:
            target = detect_target()

        return download(self.system, self.version, target, verbose=verbose)

    def launch(self, args, auto_download=True, verbose=False, await_ready=False, restart=False, local=False):
        if self.p and self.poll() == None:
            if not restart:
                raise ChildProcessError('SITL is already running, please use .stop() to kill it')
            self.stop()

        if auto_download:
            self.download()

        elfname = {
            "copter": "ArduCopter.elf",
            "plane": "ArduPlane.elf",
            "rover": "APMrover2.elf",
            "solo": "ArduCopter.elf",
        }

        if not local:
            args = [os.path.join('.', elfname[self.system])] + args
        else:
            args = [os.path.join('.', args[0])] + args[1:]

        if local:
            wd = os.getcwd()
        else:
            wd = os.path.join(sitl_target, self.system + '-' + self.version)

        # Load the binary for primitive feature detection.
        elf = open(os.path.join(wd, args[0])).read()

        # Provide a --home argument if one was not provided.
        # This stabilizes defaults in SITL.
        # https://github.com/dronekit/dronekit-sitl/issues/34
        if '--home' in elf:
            if not any(x.startswith('--home') for x in args):
                args.append('--home=-35.363261,149.165230,584,353')

        # Provide a --model argument if one was not provided.
        if '--model' in elf:
            if not any(x.startswith('--model') for x in args):
                args.append('--model=quad')

        if verbose:
            print('Execute:', str(args))

        # # Change CPU core affinity.
        # # TODO change affinity on osx/linux
        # if sys.platform == 'win32':
        #     # 0x14 = 0b1110 = all cores except cpu 1
        #     sitl = Popen(['start', '/affinity', '14', '/realtime', '/b', '/wait'] + sitl_args, shell=True, stdout=PIPE, stderr=PIPE)
        # else:
        #     sitl = Popen(sitl_args, stdout=PIPE, stderr=PIPE)

        p = Popen(args, cwd=wd, shell=sys.platform == 'win32', stdout=PIPE, stderr=PIPE)
        self.p = p

        def cleanup():
            try:
                kill(p.pid)
            except:
                pass
        atexit.register(cleanup)

        self.stdout = NonBlockingStreamReader(p.stdout)
        self.stderr = NonBlockingStreamReader(p.stderr)

        if await_ready:
            self.block_until_ready(verbose=verbose)

    def poll(self):
        return self.p.poll()

    def stop(self):
        kill(self.p.pid)
        while self.p.poll() == None:
            time.sleep(1.0/10.0)

    def block_until_ready(self, verbose=False):
        # Block until "Waiting for connection . . ."
        while self.poll() == None:
            line = self.stdout.readline(0.01)
            if line and verbose:
                sys.stdout.write(line)
            if line and 'Waiting for connection' in line:
                break

            line = self.stderr.readline(0.01)
            if line and verbose:
                sys.stderr.write(line)

        return self.poll()

    def complete(self, verbose=False):
        while self.poll() == None:
            line = self.stdout.readline(0.01)
            if line and verbose:
                sys.stdout.write(line)

            line = self.stderr.readline(0.01)
            if line and verbose:
                sys.stderr.write(line)

def launch(system, version, args):
    return SITL(system, version, args)

def detect_target():
    if sys.platform == 'darwin':
        return 'osx'
    if sys.platform == 'win32':
        return 'win'
    return 'linux'

def reset():
    # delete local sitl installations
    try:
        shutil.rmtree(sitl_target + '/')
    except:
        pass
    print('SITL directory cleared.')

def main(args=[]):
    system = 'copter'
    target = detect_target()
    version = '3.2.1'
    local = False

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

    if len(args) > 0 and args[0] == '--local':
        local = True

    if len(args) < 1 or not re.match(r'^(copter|plane|solo|rover)(-v?.+)?', args[0]) and not local:
        print('Please specify one of:', file=sys.stderr)
        print('  dronekit-sitl --list', file=sys.stderr)
        print('  dronekit-sitl --reset', file=sys.stderr)
        print('  dronekit-sitl <copter(-version)>', file=sys.stderr)
        print('  dronekit-sitl <plane(-version)>', file=sys.stderr)
        print('  dronekit-sitl <rover(-version)>', file=sys.stderr)
        print('  dronekit-sitl <solo(-version)>', file=sys.stderr)
        sys.exit(1)

    if re.match(r'^copter-v?(.+)', args[0]):
        system = 'copter'
        version = re.match(r'^copter-v?(.+)', args[0]).group(1)
    if re.match(r'^plane-v?(.+)', args[0]):
        system = 'plane'
        version = re.match(r'^plane-v?(.+)', args[0]).group(1)
    if re.match(r'^solo-v?(.+)', args[0]):
        system = 'solo'
        version = re.match(r'^solo-v?(.+)', args[0]).group(1)
    if re.match(r'^rover-v?(.+)', args[0]):
        system = 'rover'
        version = re.match(r'^rover-v?(.+)', args[0]).group(1)
    args = args[1:]

    print('os: %s, apm: %s, release: %s' % (target, system, version))

    sitl = SITL(system, version)
    if not local:
        sitl.download(target, verbose=True)

    sitl.launch(args, verbose=True, local=local)
    # sitl.block_until_ready(verbose=True)
    code = sitl.complete(verbose=True)

    if code != 0:
        sys.exit(code)
