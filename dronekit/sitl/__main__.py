#!/usr/bin/python

import sys
import re
from dronekit.sitl import main

if sys.platform == 'win32':
    # Powershell will munge commas as separate arguments
    # which conflicts with how the --home parameter is sent.
    # We opt to just fix this rather than laboriously restructure
    # existing documentation.
    i = 0
    while i < len(sys.argv):
        if sys.argv[i].startswith('--home'):
            if sys.argv[i] == '--home':
                sys.argv[i] = '--home='
            i += 1
            while i < len(sys.argv):
                if re.match(r'[\-+0-9.,]+', sys.argv[i]):
                    sys.argv[i-1] += ',' + sys.argv[i]
                    sys.argv[i-1] = re.sub(r'=,', '=', sys.argv[i-1])
                    sys.argv.pop(i)
                else:
                    i += 1
        else:
            i += 1
    print sys.argv

# Provide a --home argument if one was not provided.
# This stabilizes defaults in SITL.
# https://github.com/dronekit/dronekit-sitl/issues/34
if not any(x.startswith('--home') for x in sys.argv):
    sys.argv.append('--home=-35.363261,149.165230,584,353')

# Provide a --model argument if one was not provided.
if not any(x.startswith('--model') for x in sys.argv):
    sys.argv.append('--model=quad')

main(sys.argv[1:])
