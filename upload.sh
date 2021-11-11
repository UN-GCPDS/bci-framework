#!/usr/bin/bash

rm -R *.egg-info build dist
python setup.py sdist bdist_wheel
twine upload dist/*

