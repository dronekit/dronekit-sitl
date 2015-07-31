#!/bin/bash

cd $(dirname $0)/..
sudo python setup.py sdist bdist_egg upload
