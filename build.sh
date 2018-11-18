#!/bin/bash -e

workspace="$( dirname $0 )"



(
	cd "$workspace"
	workspace="$(pwd)"

	if [ ! -e .contents ]
	then
		virtualenv .contents
		.contents/bin/pip install -r requirements.txt
	fi

	.contents/bin/coverage erase
	for x in *_test.py
	do
		#.contents/bin/coverage run -a --source $( echo *.py | tr ' ' ',' ) $x
		.contents/bin/coverage run -a --omit=.contents/*,*_test.py $x
	done
	.contents/bin/coverage report

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
