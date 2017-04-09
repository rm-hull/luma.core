#!/usr/bin/env bash

rm -rf build dist
python setup.py clean sdist bdist_wheel upload -r pypi