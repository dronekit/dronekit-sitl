#!/bin/bash

if [[ $OSTYPE == cygwin* ]]; then
	AWSCMD="aws.cmd"
else
	AWSCMD="aws"
fi

$AWSCMD s3 sync ./publish/ s3://dronekit-assets/sitl/ --acl public-read
