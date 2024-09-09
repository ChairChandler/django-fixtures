#!/usr/bin/env bash
echo "Be sure to activate venv with pytest, coverage and other requirements" && \
echo "Generating tests_report.txt" && \
coverage run -m pytest > tests_report.txt && \
echo "Generating coverage_report.txt" && \
coverage report -m > coverage_report.txt && \
echo "Removing .coverage" && \
rm -rf .coverage