#!/bin/sh

basedir="$(realpath -e "$0" | xargs dirname)"
rootdir="$basedir/.."

die()
{
	echo "ERROR: $*" >&2
	exit 1
}

venvdir="$rootdir/venv-pyside"

virtualenv --clear --system-site-packages "$venvdir" || die "virtualenv failed."
. "$venvdir"/bin/activate || die "venv activate failed."
pip3 install PySide6 || die "pip install PySide6 failed."
