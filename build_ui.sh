#!/bin/bash -e

workspace="$( dirname $0 )"

if [ ! -e .contents_ui ]
then
	if [ -z "$VIRTUALENV" ]
	then
		VIRTUALENV=$( which virtualenv )
	fi
	if [ -z "$PYTHON_BIN" ]
	then
		PYTHON_BIN=$( which python3 )
	fi
	$VIRTUALENV -p $PYTHON_BIN .contents_ui
fi


(
	cd "$workspace"
	workspace="$(pwd)"
	/bin/rm -rf __pycache__ dist build

	VENV_BIN=.contents_ui/bin
	if [ -e .contents_ui/Scripts ]
	then
		VENV_BIN=.contents_ui/Scripts
	fi

	$VENV_BIN/pip3 install wheel
	$VENV_BIN/pip3 install -r requirements.txt
	$VENV_BIN/pip3 install -r requirements.ui.txt
	$VENV_BIN/pip3 install coverage

        $VENV_BIN/coverage erase
        for x in *_test.py
        do
                #.contents/bin/coverage run -a --source $( echo *.py | tr ' ' ',' ) $x
                $VENV_BIN/coverage run -a --omit=.contents_ui/*,*_test.py $x
        done
        $VENV_BIN/coverage report
	$VENV_BIN/pyinstaller ui.spec
	$VENV_BIN/pyinstaller ui-single.spec


)
