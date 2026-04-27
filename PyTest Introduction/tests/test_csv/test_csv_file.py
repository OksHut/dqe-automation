import pytest
import re

# Шлях до файлу (використовуємо фікстуру csv_path з conftest.py)

@pytest.mark.validate_csv
def test_csv_schema(csv_reader, schema_validator, csv_path):
    """Валідація схеми файлу (id, name, age, email, is_active)"""
    data = csv_reader(csv_path)
    # DictReader дозволяє дістати заголовки через .keys() першого рядка
    actual_columns = data[0].keys()
    expected_columns = ['id', 'name', 'age', 'email', 'is_active']
    
    is_valid, missing = schema_validator(actual_columns, expected_columns)
    assert is_valid, f"Критична помилка: Відсутні колонки: {missing}"

def test_file_is_not_empty(csv_reader, csv_path):
    """Перевірка, що файл не порожній (буде unmarked)"""
    data = csv_reader(csv_path)
    assert len(data) > 0, "Помилка: Файл не містить даних!"

@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Очікувані дублікати в тестових даних")
def test_duplicates(csv_reader, csv_path):
    """Перевірка на відсутність дублікатів рядків"""
    data = csv_reader(csv_path)
    # Перетворюємо кожний рядок (словник) у tuple, щоб зробити їх hashable для set
    data_tuples = [tuple(row.items()) for row in data]
    assert len(data_tuples) == len(set(data_tuples)), "У файлі знайдено дублікати рядків!"

@pytest.mark.validate_csv
@pytest.mark.skip(reason="Валідація віку (0-100) пропущена згідно з вимогами")
def test_age_range_placeholder(csv_reader, csv_path):
    """Перевірка діапазону віку (0-100)"""
    data = csv_reader(csv_path)
    for row in data:
        age = int(row['age'])
        assert 0 <= age <= 100, f"Некоректний вік {age} у користувача {row['id']}"

@pytest.mark.validate_csv
def test_email_column_valid(csv_reader, csv_path):
    """Перевірка формату email за допомогою Regex"""
    data = csv_reader(csv_path)
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    for row in data:
        assert re.match(email_regex, row['email']), \
            f"Помилка: Невірний формат email '{row['email']}' у користувача id:{row['id']}"

@pytest.mark.parametrize("user_id, expected_status", [
    ("1", "False"), 
    ("2", "True")
])
def test_is_active_parametrized(csv_reader, csv_path, user_id, expected_status):
    """Параметризована перевірка статусу активації"""
    data = csv_reader(csv_path)
    # Шукаємо користувача за ID
    user = next((row for row in data if row['id'] == user_id), None)
    
    assert user is not None, f"Користувача з id {user_id} не знайдено!"
    assert user['is_active'] == expected_status, \
        f"Для ID {user_id} очікували статус {expected_status}, але знайшли {user['is_active']}"




#tafordqe/tasks/PyTest Introduction/tests/test_csv/test_csv_file.py



