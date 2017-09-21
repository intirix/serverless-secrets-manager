#!/bin/bash -e

workspace="$( dirname $0 )"

if [ ! -e .contents_ui ]
then
	virtualenv -p python3 .contents_ui
fi


(
	cd "$workspace"
	workspace="$(pwd)"
	/bin/rm -rf __pycache__ dist build

	.contents_ui/bin/pip3 install -r requirements.txt
	.contents_ui/bin/pip3 install -r requirements.ui.txt
	.contents_ui/bin/pip3 install coverage

        .contents_ui/bin/coverage erase
        for x in *_test.py
        do
                #.contents/bin/coverage run -a --source $( echo *.py | tr ' ' ',' ) $x
                .contents_ui/bin/coverage run -a --omit=.contents_ui/*,*_test.py $x
        done
        .contents_ui/bin/coverage report
	.contents_ui/bin/pyinstaller ui.spec
	.contents_ui/bin/pyinstaller ui-single.spec


)
