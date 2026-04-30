import pytest
import pandas as pd
import csv
import os

# Fixture to read the CSV file


@pytest.fixture(scope="session")
def csv_reader():
    """fixture for csv reading """
    def _read_file(path_to_file):
        if not os.path.exists(path_to_file):
            pytest.fail(f"file is not found: {path_to_file}")
        with open(path_to_file, mode='r', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    return _read_file

# Fixture to validate the schema of the file


@pytest.fixture(scope="session")
def schema_validator():
    """fixture for validation """
    def _validate(actual_schema, expected_schema):
        actual_set = set(actual_schema)
        expected_set = set(expected_schema)
        return expected_set.issubset(actual_set), expected_set - actual_set
    return _validate

# additional function


@pytest.fixture(scope="session")
def csv_path():
    """
    fixture for getting the path to the csv file
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'src', 'data', 'data.csv')

# Pytest hook to mark unmarked tests with a custom mark


def pytest_collection_modifyitems(config, items):
    """
    adds unmarked if test cis not marked
    """
    for item in items:
        # go through all markers of the test and check if there is a marker other than 'parametrize'
        custom_markers = [
            mark for mark in item.iter_markers() if mark.name != "parametrize"]
        if not custom_markers:
            item.add_marker(pytest.mark.unmarked)
