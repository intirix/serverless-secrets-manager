#!/bin/bash

workspace="$( dirname $0 )"

(
	cd "$workspace"
	workspace="$(pwd)"

	echo zip lambda.zip *.py
	zip lambda.zip *.py

	(
		cd .contents/lib/python2.7/site-packages
		echo zip -u -r "$workspace/lambda.zip" *
		zip -u -r "$workspace/lambda.zip" *
	)

)
