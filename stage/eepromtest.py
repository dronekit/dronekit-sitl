import sys
import os
import dronekit
import time
import re
from dronekit_sitl import SITL

print 'launching SITL...'
s = SITL(path=os.path.join(os.path.dirname(__file__), 'build/out/apm'))
s.launch([], wd=os.path.join(os.path.dirname(__file__), 'build/test'), verbose=True)

print 'connecting...'
time.sleep(1)
vehicle = dronekit.connect('tcp:127.0.0.1:5760')

print 'waiting a fair amount of time...'
start = time.time()
while time.time() - start < 10:
    time.sleep(.1)

    line = s.stdout.readline(0.01)
    if line:
        sys.stdout.write(line)

    line = s.stderr.readline(0.01)
    if line:
        sys.stderr.write(line)

print 'checking for messages...'
messages = False
def logme(*args):
    global messages
    messages = True
vehicle.add_message_listener('*', logme)
start = time.time()
while not messages and time.time() - start < 15:
    time.sleep(.1)

if not messages:
    print 'did not receive any output'
    sys.exit(1)
else:
    print 'success!'
