#!/bin/bash -e

workspace="$( dirname $0 )"



(
	cd "$workspace"
	workspace="$(pwd)"

	if [ ! -e .contents ]
	then
		virtualenv .contents
		.contents/bin/pip install -r requirements.txt
		.contents/bin/pip install -r requirements.dev.txt
	fi

	if [ ! -e .contents2 ]
	then
		virtualenv .contents2
		.contents2/bin/pip install -r requirements.txt
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

	for x in .contents2/lib*/python*/site-packages
	do
		(
			cd $x
			echo zip -u -r "$workspace/lambda.zip" *
			zip -u -r "$workspace/lambda.zip" *
		)
	done

)
