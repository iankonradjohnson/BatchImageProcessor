#!/bin/bash

report_success() {
    echo "SUCCESS"
}

report_failure() {
    echo "FAILED"
    exit 1
}

# Run unit tests
python -m unittest discover || report_failure

# Check for at least 95% test coverage
coverage run -m unittest discover
coverage report -m --fail-under=95 || report_failure

# Format code with Black
black .

# Run pylint
pylint_output=$(pylint python 2>&1)
score=$(echo "$pylint_output" | grep "Your code has been rated at" | awk '{print $7}' | cut -d"/" -f1)
if [[ "$score" != "10.00" ]]; then
    echo "Pylint check failed with the following output:"
    echo "$pylint_output"
    report_failure
fi

# If all the checks passed
report_success
