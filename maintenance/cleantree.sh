#!/bin/sh

basedir="$(dirname "$(realpath "$0")")"
rootdir="$basedir/.."

set -e

if ! [ -x "$rootdir/partmgr-gui" -a -x "$rootdir/setup.py" ]; then
	echo "rootdir sanity check failed"
	exit 1
fi

cd "$rootdir"
find . \( \
	\( -name '__pycache__' \) -o \
	\( -name '*.pyo' \) -o \
	\( -name '*.pyc' \) -o \
	\( -name '*$py.class' \) \
       \) -delete
rm -rf build dist
rm -f MANIFEST
