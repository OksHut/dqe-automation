import pytest
import re
import os



#without marker
def test_file_is_not_empty(csv_reader, csv_path):
    data = csv_reader(csv_path)
    assert len(data) > 0, "File is empty"


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Expected duplicates")
def test_duplicates(csv_path):
    assert False


@pytest.mark.validate_csv
def test_csv_schema(csv_reader, schema_validator,csv_path):
    data = csv_reader(csv_path)
    actual_columns = data[0].keys()
    expected_columns = ['id', 'name', 'age', 'email', 'is_active']
    
    is_valid, missing = schema_validator(actual_columns, expected_columns)
    assert is_valid, f"Missed columns: {missing}"



@pytest.mark.validate_csv
@pytest.mark.skip(reason="Skip as per requirements")
def test_age_range_placeholder(csv_path):
    pass


#validate email format
@pytest.mark.validate_csv
def test_email_column_valid(csv_reader,csv_path):
    """
    check emails
    """

    data = csv_reader(csv_path)

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    for row in data:
       
        assert re.match(email_regex, row['email']), \
            f"Error: wrong format '{row['email']}' у користувача з id {row['id']}"


@pytest.mark.parametrize("id, status", [("1", "False"), ("2", "True")])
def test_is_active_parametrized(csv_reader, csv_path, id, status):
    data = csv_reader(csv_path)
    user = next(row for row in data if row['id'] == id)
    assert user['is_active'] == status






#tafordqe/tasks/PyTest Introduction/tests/test_csv/test_csv_file.py



