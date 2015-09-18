#!/bin/bash

aws s3 cp versions.json s3://dronekit-sitl-binaries/versions.json --acl public-read
