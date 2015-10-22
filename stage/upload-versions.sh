#!/bin/bash

aws s3 cp versions.json s3://dronekit-assets/sitl/versions.json --acl public-read
