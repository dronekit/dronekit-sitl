# dronekit-sitl-runner

| OS | Status |
|------|----|
| Windows | [![Build status](https://ci.appveyor.com/api/projects/status/github/3drobotics/dronekit-sitl-runner?branch=master&svg=true)](https://ci.appveyor.com/project/tcr3dr/dronekit-sitl-runner/branch/master) |
| OS X | [![Build Status](https://travis-ci.org/3drobotics/dronekit-sitl-runner.svg?branch=master)](https://travis-ci.org/3drobotics/dronekit-sitl-runner) |
| Linux | [![Build Status](https://circleci.com/gh/3drobotics/dronekit-sitl-runner.svg?style=shield)](https://circleci.com/gh/3drobotics/dronekit-sitl-runner) |

## Installing

Install from Github:

```
pip install git+https://github.com/3drobotics/dronekit-sitl-runner
```

## Usage

List of available commands:

```
  dronekit-sitl --list
  dronekit-sitl --reset
  dronekit-sitl <copter(-version)>
  dronekit-sitl <plane(-version)>
```

## Examples

```
dronekit-sitl copter-3.4-dev -I0 -S --model quad --home=-35.363261,149.165230,584,353
mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```

## Ardupilot versions available:

We are providing hosting for some pre-compiled Ardupilot Copter and Plane binaries

| Platform | List |
|------|----|
| Copter | <http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/copter/> |
| Plane | <http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/plane/> |


## License

dronekit-sitl-runner is licensed as MIT/ASL2
