# dronekit-sitl-runner

```
git clone https://github.com/tcr3dr/dronekit-sitl-runner.git
./dronekit-sitl-runner/dronekit-sitl
```

Then run mavproxy:

```
mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```
