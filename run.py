#!PYTHONUNBUFFERED=1 /usr/bin/python

import sys, os
import subprocess, string, time
import json

env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'

subprocess.Popen(['./sitl/ArduCopter.elf', '-S', '-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353'], bufsize=1, env=env, universal_newlines=True)

p = subprocess.Popen(['mavproxy.py', '--master', 'tcp:127.0.0.1:5760', '--sitl', '127.0.0.1:5501', '--out', '127.0.0.1:14550', '--out', '127.0.0.1:14551'], stdin=subprocess.PIPE)

while True:
	input = sys.stdin.read(1)
	if not input:
		break
	p.stdin.write(input)
	p.stdin.flush()
