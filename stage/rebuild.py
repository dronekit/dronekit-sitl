import sys
import json
import os
import shutil
import subprocess

# Clear publish directory
try:
    shutil.rmtree(os.path.join(os.path.dirname(__file__), 'publish'))
except:
    pass
os.makedirs(os.path.join(os.path.dirname(__file__), 'publish'))

# New env
try:
    shutil.rmtree(os.path.join(os.path.dirname(__file__), 'env'))
except:
    pass

data = json.loads(open(os.path.join(os.path.dirname(__file__), 'versions.json'), 'rb').read())

for target, versions in data.iteritems():
    for version, data in versions.iteritems():
        if version != 'stable':
            err = subprocess.call('bash ./build.sh ' + target + ' ' + version, shell=True)
            if err:
                print('error, stopping on', target, version)
                sys.exit(1)
