#!/bin/bash
set -e

echo "Running Black Check..."
black --check .
echo "Running Isort Check..."
isort --check-only .

echo "Running Tests..."
# Add current directory to PYTHONPATH so that 'api' and 'pdfsmarteditor' modules can be found
export PYTHONPATH=$PYTHONPATH:.
python -m pytest --cov=pdfsmarteditor --cov-report=xml
