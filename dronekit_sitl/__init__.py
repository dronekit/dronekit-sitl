#!/usr/bin/python

from __future__ import print_function
import six
import re
import sys
import os
import subprocess
import string
import time
import json
import tarfile
import sys
from six.moves.urllib.request import URLopener, Request, urlopen
from six.moves.urllib.error import HTTPError
import os
import json
import shutil
import atexit
import select
import psutil
import tempfile
from subprocess import Popen, PIPE
import threading
from threading import Thread
from six.moves.queue import Queue, Empty


sitl_host = 'http://dronekit-assets.s3.amazonaws.com/sitl'
sitl_target = os.path.normpath(os.path.expanduser('~/.dronekit/sitl'))

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

    req = Request(sitl_list, headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    raw = urlopen(req).read()

    if six.PY3:
        raw = raw.decode('utf-8')

    versions = json.loads(raw)
    return versions

def download(system, version, target, verbose=False):
    sitl_file = "{}/{}/sitl-{}-{}-{}.tar.gz".format(sitl_host, system, target, system, version)

    # Delete old directories from legacy SITL.
    if os.path.isdir(sitl_target + '/' + system + '-' + version):
        if not (os.path.isfile(sitl_target + '/' + system + '-' + version + '/apm') or os.path.isfile(sitl_target + '/' + system + '-' + version + '/apm.exe')):
            try:
                shutil.rmtree(sitl_target + '/' + system + '-' + version)
                print('Removing legacy SITL build...')
            except:
                pass

    if not os.path.isdir(sitl_target + '/' + system + '-' + version):
        if verbose:
            print("Downloading SITL from %s" % sitl_file)

        if not os.path.isdir(sitl_target):
            os.makedirs(sitl_target)

        def check_complete(count, block_size, total_size):
            if verbose and total_size != -1 and (count * block_size) >= total_size:
                print('Download Complete.')

        try:
            testfile = URLopener()
            testfile.retrieve(sitl_file, sitl_target + '/sitl.tar.gz', check_complete)
        except HTTPError as e:
            if e.code == 404:
                print('File Not Found: %s' % sitl_file)
                sys.exit(1)
        except IOError as e:
            if e.args[1] == 404:
                print('File Not Found: %s' % sitl_file)
                sys.exit(1)

        # TODO: cleanup sitl.tar.gz
        tar = tarfile.open(sitl_target + '/sitl.tar.gz')
        tar.extractall(path=sitl_target + '/' + system + '-' + version)
        tar.close()

        if verbose:
            print("Payload Extracted.")
    else:
        if verbose:
            print("SITL already Downloaded and Extracted.")
    if verbose:
        print('Ready to boot.')

sitl_instance_count = 0

class ArdupilotCapabilities():
    def __init__(self, path):
        # Load the binary for primitive feature detection.
        elf = open(path, 'rb').read()

        # pysim is required for earlier SITL builds
        # lacking --home or --model params.
        need_sim = not b'--home' in elf or not b'--model' in elf
        self.using_sim = need_sim

        if b'ardupilot/APMrover2' in elf:
            self.model = 'rover'
        elif b'ardupilot/ArduPlane' in elf:
            self.model = 'plane'
        else:
            self.model = 'quad'

        process = subprocess.Popen([path, '--help'], stdout=subprocess.PIPE)
        helptext = str(process.communicate()[0])

        self.has_defaults_path = "--defaults path" in helptext


def main_thread():
    for thread in threading.enumerate():
        if thread.name == "MainThread":
            return thread
    raise Exception("MainThread not found.  Can't happen")

class SITL():
    def __init__(self, path=None, instance=None, defaults_filepath=None, gdb=False, gdb_breakpoints=[], valgrind=False):
        global sitl_instance_count
        if instance is None:
            self.instance = sitl_instance_count
            sitl_instance_count += 1
        else:
            self.instance = instance

        if path is not None:
            self.path = os.path.realpath(path)
        else:
            self.path = None
        self.p = None
        self.wd = None
        self.defaults_filepath = defaults_filepath
        self.gdb = gdb
        self.gdb_breakpoints = gdb_breakpoints
        self.valgrind = valgrind

    def download(self, system, version, target=None, verbose=False):
        if target == None:
            target = detect_target()

        if version == 'stable':
            try:
                version = version_list()[system]['stable']
            except:
                raise Exception('Cannot connect to version list. Please specify a specific version to continue.')

        self.path = os.path.join(os.path.join(os.path.join(sitl_target, system + '-' + version), 'apm'))

        return download(system, version, target, verbose=verbose)

    def emit_sitl_stdout(self, line):
        sys.stdout.write("SITL-%d> " % (self.instance,))
        sys.stdout.write(line.decode(sys.getdefaultencoding()) if six.PY3 else line)

    def emit_sitl_stderr(self, line):
        sys.stdout.write("SITL-%d.stderr> " % (self.instance,))
        sys.stdout.write(line.decode(sys.getdefaultencoding()) if six.PY3 else line)

    def _sitl_reader(self):
        while not self.sitl_reader_should_quit:
            line = self.stdout.readline(timeout=1)
            if line is not None:
                self.emit_sitl_stdout(line)
            line = self.stderr.readline(timeout=1)
            if line is not None:
                self.emit_sitl_stderr(line)
            if not main_thread().is_alive():
                break

    def launch(self, initial_args, verbose=False, await_ready=False, restart=False, wd=None, use_saved_data=False, speedup=None):
        args = initial_args[:]
        if not self.path:
            raise Exception('No path specified for SITL instance.')
        if not os.path.exists(self.path):
            if os.path.exists(self.path + '.exe'):
                self.path = self.path + '.exe'
            else:
                raise Exception('SITL binary %s does not exist.' % self.path)

        if self.p and self.poll() == None:
            if not restart:
                raise ChildProcessError('SITL is already running in this process, please use .stop() to kill it')
            self.stop()

        if wd is not None:
            self.wd = wd
        if self.wd is None or not use_saved_data:
            self.wd = tempfile.mkdtemp()

        if use_saved_data:
            # make sure there's an eeprom.bin, at least!
            eeprom_path = os.path.join(self.wd, "eeprom.bin")
            if not os.path.exists(eeprom_path):
                raise Exception('Told to use saved data, but (%s) does not exist' % (eeprom_path,))

        caps = ArdupilotCapabilities(self.path)
        self.using_sim = caps.using_sim # compatability

        # Defaults stabilizes SITL emulation.
        # https://github.com/dronekit/dronekit-sitl/issues/34
        if not any(x.startswith('--home') for x in args):
            args.append('--home=-35.363261,149.165230,584,353')
        if not any(x.startswith('--model') for x in args):
            args.append('--model=' + caps.model)

        if not any(x.startswith('-I') for x in args):
            args.extend(['-I', str(self.instance)])

        if speedup is not None:
            args.extend(['--speedup', str(speedup)])

        # Run pysim
        if self.using_sim:
            import argparse
            parser = argparse.ArgumentParser(usage=argparse.SUPPRESS)
            parser.add_argument('-I')
            parser.add_argument('--home')
            parser.add_argument('--rate')
            parser.add_argument('--model')
            parser.add_argument('-C', action='store_true')
            parser.add_argument('--gimbal', action='store_true')
            def noop(*args, **kwargs):
                pass

            parser.error = noop
            out = parser.parse_known_args(args[:])
            if out == None:
                print('Warning! Couldn\'t recognize arguments passed to legacy SITL.', file=sys.stderr)
            else:
                res, rest = out

                # Fixup actual args.
                args = [self.path]
                if res.I:
                    args += ['-I' + res.I]
                if res.C:
                    args += ['-C']

                # Legacy name for quad is +
                if res.model == 'quad':
                    res.model = '+'

                # pysim args
                print('Note: Starting pysim for legacy SITL.')
                simargs = [sys.executable, os.path.join(os.path.dirname(__file__), 'pysim/sim_wrapper.py'),
                           '--simin=127.0.0.1:5502', '--simout=127.0.0.1:5501', '--fgout=127.0.0.1:5503',
                           '--home='+res.home, '--frame='+res.model]

                if res.gimbal:
                    simargs.append('--gimbal')

                psim = Popen(simargs, cwd=self.wd, shell=sys.platform == 'win32')

                def cleanup_sim():
                    try:
                        kill(psim.pid)
                    except:
                        pass
                atexit.register(cleanup_sim)

                if verbose:
                    print('Pysim:', ' '.join((simargs)))

        # new versions of ardupilot allow us to specify a set of defaults:
        if caps.has_defaults_path:
            if self.defaults_filepath is not None:
                args.extend(["--defaults", self.defaults_filepath])
            if not use_saved_data:
                args.append("-w")
        else:
            if self.defaults_filepath is not None:
                raise ValueError("--defaults not supported by ardupilot binary")

        # the following is the "traditional" way of wiping parameters
        # and using pre-canned parameters generated and stored on s3
        if not use_saved_data and self.defaults_filepath is None:
            # Copy default eeprom into this dir.
            try:
                shutil.copy2(os.path.join(os.path.dirname(self.path), 'default_eeprom.bin'), os.path.join(self.wd, 'eeprom.bin'))
            except:
                pass

        # # Change CPU core affinity.
        # # TODO change affinity on osx/linux
        # if sys.platform == 'win32':
        #     # 0x14 = 0b1110 = all cores except cpu 1
        #     sitl = Popen(['start', '/affinity', '14', '/realtime', '/b', '/wait'] + sitl_args, shell=True, stdout=PIPE, stderr=PIPE)
        # else:
        #     sitl = Popen(sitl_args, stdout=PIPE, stderr=PIPE)

        popen_args = []
        if self.gdb:
            commands_file = "/tmp/gdb.tmp"
            commands_fd = open(commands_file,"w")
            for breakpoint in self.gdb_breakpoints:
                commands_fd.write("b %s\n" % breakpoint)
            commands_fd.write("r\n")
            popen_args.extend(["xterm", "-e", "gdb", "-q", "-x", commands_file, "--args"])
        if self.valgrind:
            popen_args.extend(["xterm", "-e", "valgrind" ])
        popen_args.append(self.path)
        popen_args.extend(args)

        if verbose:
            print('Execute:', ' '.join(popen_args))

        self.p = Popen(popen_args, cwd=self.wd, shell=sys.platform == 'win32', stdout=PIPE, stderr=PIPE)

        def cleanup():
            try:
                kill(self.p.pid)
            except:
                pass
        atexit.register(cleanup)

        self.stdout = NonBlockingStreamReader(self.p.stdout)
        self.stderr = NonBlockingStreamReader(self.p.stderr)

        if await_ready:
            self.block_until_ready(verbose=verbose)

        self.sitl_reader = None
        if verbose:
            # set up a reader to spit output from SITL out
            self.sitl_reader_should_quit = False
            self.sitl_reader = Thread(target = self._sitl_reader, args = ())
            self.sitl_reader.start()

    def poll(self):
        return self.p.poll()

    def stop(self):
        kill(self.p.pid)
        while self.p.poll() == None:
            time.sleep(1.0/10.0)

    def block_until_ready(self, verbose=False):
        # Block until "Waiting for connection . . ."
        if self.gdb:
            return
        if self.valgrind:
            time.sleep(5)
            return
        while self.poll() == None:
            line = self.stdout.readline(0.01)
            if line and verbose:
                self.emit_sitl_stdout(line)
            if line and b'Waiting for connection' in line:
                break

            line = self.stderr.readline(0.01)
            if line and verbose:
                self.emit_sitl_stderr(line)

        return self.poll()

    def complete(self, verbose=False):
        # tell the sitl reader to stop slurping the data we're after
        if self.sitl_reader is not None:
            self.sitl_reader_should_quit = True
            self.sitl_reader.join()

        while True:
            alive = self.poll()

            out = self.stdout.readline(0.01)
            if out and verbose:
                sys.stdout.write(out.decode(sys.getdefaultencoding()) if six.PY3 else out)

            err = self.stderr.readline(0.01)
            if err and verbose:
                sys.stderr.write(err.decode(sys.getdefaultencoding()) if six.PY3 else err)

            if not out and not err and alive != None:
                break

    def connection_string(self):
        '''returned string may be used to connect to simulated vehicle'''
        # these are magic numbers; ArduPilot listens on ports starting
        # at 5760+10*(instance-number)
        port = 5760
        port += 10 * self.instance
        return 'tcp:127.0.0.1:' + str(port)

def start_default(lat=None, lon=None):
    '''start a SITL session using sensible defaults.  This should be the simplest way to start a sitl session'''
    print("Starting copter simulator (SITL)")
    args = {}
    binary = os.getenv("SITL_BINARY")
    do_download = True
    if binary is not None:
        do_download = False
        args["path"] = binary
        defaults = os.getenv("SITL_DEFAULTS_FILEPATH")
        if defaults is not None:
            args["defaults_filepath"] = defaults
    sitl = SITL(**args)
    if do_download:
        sitl.download('copter', '3.3', verbose=True)
    if ((lat is not None and lon is None) or
        (lat is None and lon is not None)):
        print("Supply both lat and lon, or neither")
        exit(1)
    sitl_args = ['--model', 'quad', ]
    if lat is not None:
        sitl_args.append('--home=%f,%f,584,353' % (lat,lon,))
    sitl.launch(sitl_args, await_ready=True, restart=True)
    return sitl


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

def main(args=None):
    if args == None:
        args = sys.argv[1:]

        if sys.platform == 'win32':
            # Powershell will munge commas as separate arguments
            # which conflicts with how the --home parameter is sent.
            # We opt to just fix this rather than laboriously restructure
            # existing documentation.
            i = 0
            while i < len(args):
                if args[i].startswith('--home'):
                    if args[i] == '--home':
                        args[i] = '--home='
                    i += 1
                    while i < len(args):
                        if re.match(r'[\-+0-9.,]+', args[i]):
                            args[i-1] += ',' + args[i]
                            args[i-1] = re.sub(r'=,', '=', args[i-1])
                            args.pop(i)
                        else:
                            i += 1
                else:
                    i += 1

    system = 'copter'
    target = detect_target()
    version = '3.2.1'
    local = False

    if len(args) > 0 and args[0] == '--list':
        versions = version_list()
        for system in [system for system, v in versions.items()]:
            keys = [k for k, v in versions[system].items()]
            keys.sort()
            for k in keys:
                if k != 'stable':
                    print(system + '-' + k)
        sys.exit(0)

    if len(args) > 0 and (args[0] == '--version' or args[0] == '-v'):
        import pkg_resources
        print(pkg_resources.get_distribution(sys.modules[__name__].__package__).version)
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
        print('--local no longer needed. Specify an absolute or relative file path.')
        sys.exit(1)

    if len(args) > 0 and args[0] == 'download':
        capture = re.match(r'([a-z]*)(\-)(([0-9]{1,}|(\.))*)', args[1])
        system = capture.group(1)
        version = capture.group(3)
        print('os: %s, apm: %s, release: %s' % (target, system, version))
        sitl = SITL()
        sitl.download(system, version, target=target, verbose=True)
        sys.exit(1)

    if len(args) < 1 or not re.match(r'^(copter|plane|solo|rover)(-v?.+)?|^[./]|:', args[0]) and not local:
        print('Please specify one of:', file=sys.stderr)
        print('  dronekit-sitl --list', file=sys.stderr)
        print('  dronekit-sitl --reset', file=sys.stderr)
        print('  dronekit-sitl download <(copter|plane|rover|solo)(-version)>', file=sys.stderr)
        print('  dronekit-sitl <copter(-version)> [args...]', file=sys.stderr)
        print('  dronekit-sitl <plane(-version)> [args...]', file=sys.stderr)
        print('  dronekit-sitl <rover(-version)> [args...]', file=sys.stderr)
        print('  dronekit-sitl <solo(-version)> [args...]', file=sys.stderr)
        print('  dronekit-sitl ./path [args...]', file=sys.stderr)
        sys.exit(1)

    binpath = args[0]
    args = args[1:]
    if re.match(r'^copter(-v?(.+)|$)', binpath):
        system = 'copter'
        try:
            version = re.match(r'^copter-v?(.+)', binpath).group(1)
        except:
            version = 'stable'
    if re.match(r'^plane(-v?(.+)|$)', binpath):
        system = 'plane'
        try:
            version = re.match(r'^plane-v?(.+)', binpath).group(1)
        except:
            version = 'stable'
    if re.match(r'^solo(-v?(.+)|$)', binpath):
        system = 'solo'
        try:
            version = re.match(r'^solo-v?(.+)', binpath).group(1)
        except:
            version = 'stable'
    if re.match(r'^rover(-v?(.+)|$)', binpath):
        system = 'rover'
        try:
            version = re.match(r'^rover-v?(.+)', binpath).group(1)
        except:
            version = 'stable'
    local = re.match(r'^[./]|:', binpath)

    if local:
        print('os: %s, local binary: %s' % (target, binpath))
        sitl = SITL(path=binpath)
    else:
        print('os: %s, apm: %s, release: %s' % (target, system, version))
        sitl = SITL()
        sitl.download(system, version, target=target, verbose=True)

    try:
        sitl.launch(args, verbose=True)
        # sitl.block_until_ready(verbose=True)
        code = sitl.complete(verbose=True)

        if code != 0:
            sys.exit(code)
    except KeyboardInterrupt:
        pass
