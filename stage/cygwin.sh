STARTDIR=$(pwd)
rm -rf build ardupilot.tar.gz sitl.tar.gz
mkdir -p build/ardupilot
cd build
wget -qO ardupilot.tar.gz https://github.com/tcr3dr/ardupilot/archive/builder-copter-3.3-rc5.tar.gz
tar -xf ardupilot.tar.gz --strip-components=1 -C ardupilot
cd ardupilot/ArduCopter
(make configure SKETCHBOOK=$STARTDIR/build/ardupilot || true)
make sitl SKETCHBOOK=$STARTDIR/build/ardupilot -j64
(cp /tmp/ArduCopter.build/ArduCopter.elf . || true)
cd $STARTDIR
tar -cvf sitl.tar.gz -C $STARTDIR/build/ardupilot/ArduCopter/ ArduCopter.elf -C c:/cygwin/bin/ cyggcc_s-1.dll cygstdc++-6.dll cygwin1.dll
awk -F\" '/define THISFIRMWARE.*Copter/{ print $2 }' build/ardupilot/ArduCopter/* | awk '{ print tolower($2) }' > VERSION
