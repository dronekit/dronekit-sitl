# dronekit-sitl-runner

```
pip install git+https://github.com/tcr3dr/dronekit-sitl-runner
```

Then run one of:

```
  dronekit-sitl --list
  dronekit-sitl --reset
  dronekit-sitl <copter(-version)>
  dronekit-sitl <plane(-version)>
```

## example

```
dronekit-sitl copter-3.4-dev -I0 -S --model quad --home=-35.363261,149.165230,584,353
mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```

See all versions here:

<http://dronekit-sitl-binaries.s3-website-us-east-1.amazonaws.com/>

## license

dronekit-sitl-runner is licensed as MIT/ASL2
