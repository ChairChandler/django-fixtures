#!/usr/bin/env bash
echo "Be sure to activate venv with wheel" && \
python setup.py bdist_wheel && \
echo "Removing build and *.egg-info" && \
rm -rf build -- *.egg-info