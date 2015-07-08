# dronekit-sitl-runner

[![Windows Build status](https://img.shields.io/appveyor/ci/tcr3dr/dronekit-sitl-runner.svg?label=windows)](https://ci.appveyor.com/project/tcr3dr/dronekit-sitl-runner/branch/master) [![OS X Build Status](https://img.shields.io/travis/3drobotics/dronekit-sitl-runner.svg?label=os%20x)](https://travis-ci.org/3drobotics/dronekit-sitl-runner) [![Linux Build Status](https://img.shields.io/circleci/project/3drobotics/dronekit-sitl-runner.svg?label=linux)](https://circleci.com/gh/3drobotics/dronekit-sitl-runner)

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
