#!/usr/bin/env bash
activate_venv() {
	echo "Creating venv"
	if [ ! -d .venv ]; then
		python3 -m venv .venv
	fi
	echo "Activating venv"
	source .venv/bin/activate
	pip install wheel
}

UP="$(dirname -- "$0")/.."

cd "$UP" && \
activate_venv &&
python setup.py bdist_wheel && \
echo "Removing build and *.egg-info" && \
rm -rf build -- *.egg-info