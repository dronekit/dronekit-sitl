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

main(sys.argv[1:])
