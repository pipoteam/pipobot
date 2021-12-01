#!/bin/sh
if [ $# -eq 1 ]; then
	if [ "${1}" = 'cov' ]; then
		COV=true
	fi
fi


if [ $COV ]; then
	PYTHONPATH=. py.test tests -v --cov-report term-missing --cov pipobot -s
else
	PYTHONPATH=. py.test tests -v -s
fi
