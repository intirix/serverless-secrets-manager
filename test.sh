#!/bin/bash -e

workspace="$( dirname $0 )"



(
	cd "$workspace"
	workspace="$(pwd)"

	.contents/bin/coverage erase
	for x in *_test.py
	do
		#.contents/bin/coverage run -a --source $( echo *.py | tr ' ' ',' ) $x
		.contents/bin/coverage run -a --omit=.contents/*,*_test.py $x
	done
	.contents/bin/coverage report


)
