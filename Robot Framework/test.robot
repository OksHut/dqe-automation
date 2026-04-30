*** Settings ***
Documentation     Data Quality Automation: Dynamic Reconciliation.
...               Цей тест автоматично збирає дані з DIV-звіту та порівнює з Parquet.
Library           SeleniumLibrary
Library           helper.py
Test Teardown     Close Browser

*** Variables ***
# Шляхи до файлів. Використовуй прямі слеші / для Windows.
${REPORT_FILE}       ${CURDIR}/generated_report/report.html
${PARQUET_FOLDER}    ${CURDIR}/parquet_data/facility_type_avg_time_spent_per_visit_date
${BROWSER}           chrome

*** Test Cases ***
Reconcile BI Report With Parquet Source Dynamically
    [Documentation]    Відкриття DIV-звіту, динамічний збір даних та звірка з Parquet.
    [Tags]             DataReconciliation    Dynamic
    
    # 1. Відкриваємо браузер
    Open Browser    file://${REPORT_FILE}    ${BROWSER}
    Maximize Browser Window
    
    # 2. Чекаємо на твій специфічний елемент (колонку), щоб JS встиг відрендерити дані
    Wait Until Element Is Visible    class=y-column    timeout=15s
    
    # 3. Невелика пауза для стабільності завантаження всіх комірок
    Sleep    2s
    
    # 4. ВИКЛИК ПІТОН-ЛОГІКИ
    # Ми не передаємо аргументи, бо функція сама бере драйвер із SeleniumLibrary
    ${df_html}    ${dates_to_check}=    Read Dynamic Report And Get Dates
    
    # 5. Читаємо Parquet лише за знайденими у звіті датами
    ${df_parquet}=    Read Parquet By Date List    ${PARQUET_FOLDER}    ${dates_to_check}
    
    # 6. Порівнюємо дані (округлення та сортування вже всередині helper.py)
    ${status}    ${error}=    Compare Reconciled Data    ${df_html}    ${df_parquet}
    
    # 7. Обробка результату
    IF    ${status} == ${False}
        Fail    Data mismatch detected for period: ${dates_to_check}\nDetails:\n${error}
    END
    
    Log    Success! Verified dates: ${dates_to_check}