TARGET_LABEL="copter"
TARGET_ARDU="ArduCopter"
TARGET_VERSION="3.3-rc5"

STARTDIR=$(pwd)
rm -rf build ardupilot.tar.gz sitl.tar.gz
mkdir -p build/ardupilot
cd build
wget -qO ardupilot.tar.gz https://github.com/tcr3dr/ardupilot/archive/builder-$TARGET_LABEL-$TARGET_VERSION.tar.gz
tar -xf ardupilot.tar.gz --strip-components=1 -C ardupilot
cd ardupilot/$TARGET_ARDU
(make configure SKETCHBOOK=$STARTDIR/build/ardupilot || true)
make sitl SKETCHBOOK=$STARTDIR/build/ardupilot -j64
(cp /tmp/$TARGET_ARDU.build/$TARGET_ARDU.elf . || true)
cd $STARTDIR
tar -cvf sitl.tar.gz -C $STARTDIR/build/ardupilot/$TARGET_ARDU/ $TARGET_ARDU.elf -C c:/cygwin/bin/ cyggcc_s-1.dll cygstdc++-6.dll cygwin1.dll
