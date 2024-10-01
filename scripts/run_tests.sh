#!/usr/bin/env bash
activate_venv() {
	echo "Creating venv"
	if [ ! -d .venv ]; then
		python3 -m venv .venv
	fi
	echo "Activating venv"
	source .venv/bin/activate
	pip install pytest coverage pytest-cases
}

UP="$(dirname -- "$0")/.."

cd "$UP" && \
activate_venv && \
echo "Generating reports/tests_report.txt" && \
coverage run -m pytest > reports/tests_report.txt && \
echo "Generating reports/coverage_report.txt" && \
coverage report -m > reports/coverage_report.txt && \
echo "Removing .coverage" && \
rm -rf .coverage