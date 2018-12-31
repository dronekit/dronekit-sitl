# DroneKit-SITL

![Logo](https://cloud.githubusercontent.com/assets/5368500/10805537/90dd4b14-7e22-11e5-9592-5925348a7df9.png)

[![PyPi published version](https://img.shields.io/pypi/v/dronekit-sitl.svg)](https://pypi.org/project/dronekit_sitl/) [![Windows Build status](https://img.shields.io/appveyor/ci/3drobotics/dronekit-sitl.svg?label=windows)](https://ci.appveyor.com/project/3drobotics/dronekit-sitl/branch/master) [![OS X Build Status](https://img.shields.io/travis/dronekit/dronekit-sitl.svg?label=os%20x)](https://travis-ci.org/dronekit/dronekit-sitl) [![Linux Build Status](https://img.shields.io/circleci/project/dronekit/dronekit-sitl.svg?label=linux)](https://circleci.com/gh/dronekit/dronekit-sitl)<a href="https://discuss.dronekit.io/c/development"><img align="right" src="https://img.shields.io/badge/support-discuss.dronekit.io-blue.svg"></img></a>

SITL Runner for DroneKit.

## Overview

The ArduPilot [SITL (Software In The Loop) simulator](http://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) allows you to simulate an ArduPilot based autopilot and communicate with it using MAVLink over the local IP network. 

DroneKit-SITL is the fastest and easiest way to run SITL on Windows, Linux, or MAC OSX. It is installed from Python’s pip tool on all platforms, and provides a few simple commands to run pre-built vehicle binaries that are appropriate for the host operating system (downloading them if needed). You can even use it to run binaries you've build locally.

The tool is used extensively by DroneKit projects to test DroneKit apps and example code.

**Note:** DroneKit-SITL currently only supplies x86 binaries for Mac, Linux and Windows. You can't run it on ARM platforms like RaPi.

## Installing

Install using pip (recommended):

```
pip install dronekit-sitl
```

Installing from Github master:
```
pip install git+https://github.com/dronekit/dronekit-sitl
```

The `-UI` or `--upgrade --ignore-installed` flags can be added to the commands to update an existing installation to the latest version.

## Usage

List of available commands:

```
  dronekit-sitl --list
  dronekit-sitl --reset
  dronekit-sitl <copter(-version)> [parameters]
  dronekit-sitl <plane(-version)> [parameters]
  dronekit-sitl <rover(-version)> [parameters]
  dronekit-sitl <solo(-version)> [parameters]
  dronekit-sitl /path/to/local/binary [parameters]
```

The ``--list`` commmand is used to display the available build versions (e.g. `copter-3.4-dev`).

The ``-h`` *parameter* can be passed in the command above to list all the parameters to the build 
(these are reproduced below).

| Option | Description |
|------|----|
| --h | Help (display help for the build - i.e. these parameters) |
| --home HOME | Set home location (lat,lng,alt,yaw) |
| --model MODEL | Set simulation model |
| --wipe | Wipe eeprom and dataflash |
| --rate RATE | Set SITL framerate |
| --console | Use console instead of TCP ports |
| --instance N | Set instance of SITL (adds 10*instance to all port numbers) |
| --speedup SPEEDUP | Set simulation speedup |
| --gimbal | Enable simulated MAVLink gimbal |
| --autotest-dir | DIR set directory for additional files |


## Examples

The following command might be used to start SITL for build of `copter-3.3`:

```
dronekit-sitl copter-3.3 --home=-35.363261,149.165230,584,353
```

SITL starts and waits for TCP connections on `127.0.0.1:5760`. In a second terminal you can spawn an instance of MAVProxy to
forward messages to UDP ports `127.0.0.1:14550` and `127.0.0.1:14551` (in the same way as **sim_vehicle.sh**):

```
mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```


## Ardupilot versions available

You can get the available vehicle builds using the command:
```bash
dronekit-sitl --list
```

You can also view the pre-compiled Ardupilot Copter, Plane and Rover binaries at the links below:

| Platform | List |
|------|----|
| Copter | <http://dronekit-assets.s3-website-us-east-1.amazonaws.com/sitl/copter/> |
| Plane | <http://dronekit-assets.s3-website-us-east-1.amazonaws.com/sitl/plane/> |
| Rover | <http://dronekit-assets.s3-website-us-east-1.amazonaws.com/sitl/rover/> |
| Solo | <http://dronekit-assets.s3-website-us-east-1.amazonaws.com/sitl/solo/> |


## API

SITL exposes a Python API for managing a SITL instance.

```
from dronekit_sitl import SITL
sitl = SITL(path=apm) # load a binary path (optional)
sitl.download(system, version, verbose=False) # ...or download system (e.g. "copter") and version (e.g. "3.3")
sitl.launch(args, verbose=False, await_ready=False, restart=False)
sitl.block_until_ready(verbose=False) # explicitly wait until receiving commands
code = sitl.complete(verbose=False) # wait until exit
sitl.poll() # returns None or return code
sitl.stop() # terminates SITL
```

A simpler (but less flexible) interface is also available:
```
import dronekit_sitl
sitl = dronekit_sitl.start_default() # basic ArduCopter sim
connection_string = sitl.connection_string()
.
.
sitl.stop() # terminates SITL
```

## License

dronekit-sitl is licensed as MIT, Apache-2.0, and GPLv3.

pysim is licensed as GPLv3.


## Resources

* **Documentation:** 
  * This page! 
  * Dronekit-Python: [Setting up a Simulated Vehicle (SITL)](http://python.dronekit.io/develop/sitl_setup.html)
* **Examples:** 
  * [Example section above](#examples), 
  * [DroneKit Python QuickStart](http://python.dronekit.io/guide/quick_start.html#basic-hello-drone)
* **Open Issues:** [/dronekit-sitl/issues](https://github.com/dronekit/dronekit-sitl/issues)
* **Forums:** [https://discuss.dronekit.io](https://discuss.dronekit.io/c/development)
