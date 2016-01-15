#! /usr/bin/env bash

set -eu -o pipefail

# Verify that PyPi package display is valid
echo "Checking PyPi package HTML"
if ! python setup.py --long-description | rst2html.py --strict > /dev/null; then
    echo
    echo "Error: invalid package display; check CHANGELOG.md"
    exit 1
fi

# Build package
rm -rf build dist
python setup.py sdist bdist_wheel
python3 setup.py bdist_wheel || echo "Python 3 not supported"

# Upload to PyPi
twine upload -u rax_cbd_dev dist/*
