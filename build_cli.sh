#!/bin/bash -e

workspace="$( dirname $0 )"



(
	cd "$workspace"
	workspace="$(pwd)"

	VENV=.contents_cli

	if [ ! -e $VENV ]
	then
		virtualenv $VENV
		$VENV/bin/pip install -r requirements.cli.txt
	fi

	if [ ! -e $VENV/bin/coverage ]
	then
		$VENV/bin/pip install coverage
	fi

	$VENV/bin/coverage erase
	for x in *_test.py
	do
		#.contents/bin/coverage run -a --source $( echo *.py | tr ' ' ',' ) $x
		$VENV/bin/coverage run -a --omit=$VENV/*,*_test.py $x
	done
	$VENV/bin/coverage report

)
