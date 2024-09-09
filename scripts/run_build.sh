#!/usr/bin/env bash
activate_venv() {
	echo "Creating venv"
	if [ ! -f .venv ]; then
		python -m venv .venv
	fi
	echo "Activating venv"
	source .venv/bin/activate
	pip install wheel
}

UP="$(dirname -- "$0")/.."

cd "$UP" && \
activate_venv &&
python setup.py bdist && \
echo "Removing build and *.egg-info" && \
rm -rf build -- *.egg-info