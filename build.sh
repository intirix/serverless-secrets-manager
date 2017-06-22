#!/bin/bash

workspace="$( dirname $0 )"

(
	cd "$workspace"
	workspace="$(pwd)"

	echo zip lambda.zip *.py
	zip lambda.zip *.py

	(
		cd .contents2/lib/python2.7/site-packages
		echo zip -u -r "$workspace/lambda.zip" *
		zip -u -r "$workspace/lambda.zip" *
	)
	(
		cd .contents2/lib64/python2.7/site-packages
		echo zip -u -r "$workspace/lambda.zip" *
		zip -u -r "$workspace/lambda.zip" *
	)

)
