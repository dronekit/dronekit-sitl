# Building a new SITL image

To build a new SITL version:

```
./build.sh solo 1.2.8
```

Where `builder-solo-1.2.8` is a tag uploaded to https://github.com/dronekit/ardupilot-releases.  This generates a file i.e. `stage/publish/solo/sitl-osx-solo-1.2.8.tar.gz`. Extract this file `~/.dronekit/sitl/solo-1.2.8` to use it.

Remove the `stage/build` and `stage/publish` directories to clear your build data.

## Publishers

For publishers, to rebuild ALL builds from the `versions.json` (manually uploaded to S3 and tracked there):

```
./rebuild.py
```

then

```
./republish.sh
```
