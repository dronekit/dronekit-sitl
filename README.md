# dronekit-sitl

[![Windows Build status](https://img.shields.io/appveyor/ci/3drobotics/dronekit-sitl.svg?label=windows)](https://ci.appveyor.com/project/3drobotics/dronekit-sitl/branch/master) [![OS X Build Status](https://img.shields.io/travis/dronekit/dronekit-sitl.svg?label=os%20x)](https://travis-ci.org/dronekit/dronekit-sitl) [![Linux Build Status](https://img.shields.io/circleci/project/dronekit/dronekit-sitl.svg?label=linux)](https://circleci.com/gh/dronekit/dronekit-sitl)

## Installing

Install using pip:

```
pip2 install dronekit-sitl -UI
```


## Usage

List of available commands:

```
  dronekit-sitl --list
  dronekit-sitl --reset
  dronekit-sitl <copter(-version)> [parameters]
  dronekit-sitl <plane(-version)> [parameters]
  dronekit-sitl <rover(-version)> [parameters]
  dronekit-sitl <solo(-version)> [parameters]
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

The following command might be used to start SITL for build of ``copter-3.3-rc5``:

```
dronekit-sitl copter-3.3-rc5 -I0 -S --model quad --home=-35.363261,149.165230,584,353
```

SITL starts and waits for TCP connections on ``127.0.0.1:5760``. In a second terminal you can spawn an instance of MAVProxy to
forward messages to UDP ports ``127.0.0.1:14550`` and ``127.0.0.1:14551`` (in the same way as **sim_vehicle.sh**):

```
mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```


## Ardupilot versions available:

We are providing hosting for some pre-compiled Ardupilot Copter, Plane and Rover binaries

| Platform | List |
|------|----|
| Copter | <http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/copter/> |
| Plane | <http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/plane/> |
| Rover | <http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/rover/> |


## API

SITL exposes a Python API for managing a SITL instance.

```
from dronekit_sitl import SITL
sitl = SITL(system, version) # launch system (e.g. "copter") and version (e.g. "3.3")
sitl.download(target, verbose=False) # explicitly download version
sitl.launch(args, verbose=False, auto_download=True, await_ready=False, restart=False)
sitl.block_until_ready(verbose=False) # explicitly wait until receiving commands
code = sitl.complete(verbose=False) # wait until exit
sitl.poll() # returns None or return code
sitl.stop() # terminates SITL
```


## License

dronekit-sitl is licensed as MIT, Apache-2.0, and GPLv3.

pysim is licensed as GPLv3.
