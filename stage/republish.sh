#!/bin/bash

if [[ $OSTYPE == cygwin* ]]; then
	AWSCMD="aws.exe"
else
	AWSCMD="aws"
fi

$AWSCMD s3 sync ./publish/ s3://dronekit-sitl-binaries/ --acl public-read
