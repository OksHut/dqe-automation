import time
import csv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. Контекстний менеджер для Selenium WebDriver ---
class SeleniumWebDriverContextManager:
    """
    Контекстний менеджер для ініціалізації та коректного завершення роботи Selenium WebDriver.
    Гарантує закриття браузера навіть при помилках.
    """
    def __init__(self, browser_name: str = 'chrome', headless: bool = True):
        self.browser_name = browser_name
        self.headless = headless
        self.driver: webdriver.Remote = None

    def __enter__(self) -> webdriver.Remote:
        print("⚙️ Ініціалізація WebDriver...")
        if self.browser_name.lower() == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            raise ValueError(f"Непідтримуваний браузер: {self.browser_name}")
        
        self.driver.implicitly_wait(5) 
        print("✅ WebDriver успішно ініціалізовано.")
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            print("🛑 Закриваю WebDriver...")
            self.driver.quit()
            print("✅ WebDriver закрито.")
        return False # Дозволяємо виняткам підніматися вище для логування

# --- 2. Витягнення даних з таблиці ---
def extract_table_data(driver: webdriver.Remote, output_dir: Path, output_filename: str = "table.csv"):
    print(f"\n--- Завдання 2: Витягнення даних з таблиці ---")
    output_path = output_dir / output_filename
    
    try:
        wait = WebDriverWait(driver, 15)
        # Локатор 1: By.CLASS_NAME для кореня таблиці
        table_root = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table")))
        
        # Локатор 2: By.CLASS_NAME для колонок
        columns = table_root.find_elements(By.CLASS_NAME, "y-column")
        
        headers = []
        columns_data_list = [] 
        
        for col_index, column in enumerate(columns):
            # Локатор 3: By.ID для заголовка всередині колонки
            try:
                header_element = column.find_element(By.ID, "header")
                header_text = header_element.text.strip()
            except NoSuchElementException:
                header_text = f"Col_{col_index}"
            
            headers.append(header_text)
            
            # Локатор 4: By.CSS_SELECTOR для комірок
            cell_elements = column.find_elements(By.CSS_SELECTOR, ".cell-text") 
            current_column_data = [c.text.strip() for c in cell_elements if c.text.strip() != header_text]
            columns_data_list.append(current_column_data)

        # Транспонуємо дані (колонки в рядки)
        rows_data = list(zip(*columns_data_list))

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows_data)
        print(f"✅ Таблицю збережено у {output_path}")

    except Exception as e:
        print(f"❌ Помилка в Завданні 2: {e}")

# --- 3. Взаємодія з Doughnut Chart ---
def extract_doughnut_chart_data(driver: webdriver.Remote, output_dir: Path, output_prefix: str = "doughnut", screenshot_prefix: str = "screenshot"):
    print(f"\n--- Завдання 3: Взаємодія з Doughnut Chart ---")
    
    try:
        wait = WebDriverWait(driver, 15)
        # Очікуємо корінь графіка ( pielayer )
        chart_root = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pielayer")))
        
        # Скриншот 0: Початковий стан
        chart_root.screenshot(str(output_dir / f"{screenshot_prefix}0.png"))
        print(f"📸 Скриншот початкового стану збережено.")

        # Знаходимо елементи легенди для кліків ( traces всередині scrollbox )
        legend_items = driver.find_elements(By.CSS_SELECTOR, ".scrollbox .traces")
        
        for i, item in enumerate(legend_items):
            # 1. Клік на фільтр
            item.click()
            time.sleep(1) # Пауза для анімації SVG
            
            # 2. Скриншот (screenshot1, screenshot2...)
            scr_name = f"{screenshot_prefix}{i+1}.png"
            chart_root.screenshot(str(output_dir / scr_name))
            
            # 3. Витягнення даних (tspan всередині slicetext)
            slice_labels = chart_root.find_elements(By.CSS_SELECTOR, "text.slicetext[data-notex='1']")
            chart_rows = []
            for label in slice_labels:
                tspans = label.find_elements(By.TAG_NAME, "tspan")
                if len(tspans) >= 2:
                    category = tspans[0].text.strip()
                    value = tspans[1].text.strip()
                    chart_rows.append([category, value])
            
            # 4. Збереження CSV (doughnut1.csv, doughnut2.csv...)
            csv_name = f"{output_prefix}{i+1}.csv"
            with open(output_dir / csv_name, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Facility Type", "Min Average Time Spent"])
                writer.writerows(chart_rows)
            
            print(f"✅ Оброблено фільтр {i+1}: {scr_name} та {csv_name}")

    except Exception as e:
        print(f"❌ Помилка в Завданні 3: {e}")

# --- Основна логіка ---
if __name__ == "__main__":
    # Створюємо папку для результатів
    output_data_dir = Path("output_data")
    output_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Визначаємо шлях до report.html в тій же папці, що і скрипт
    current_script_path = Path(__file__).resolve()
    report_file_path = current_script_path.parent / "report.html"
    REPORT_URL = report_file_path.as_uri()

    print(f"🚀 Починаємо DQ автоматизацію для: {REPORT_URL}")

    with SeleniumWebDriverContextManager(headless=True) as driver: 
        driver.get(REPORT_URL)
        
        # Виконання завдань
        extract_table_data(driver, output_data_dir)
        extract_doughnut_chart_data(driver, output_data_dir)

    print(f"\n✨ Робота завершена. Результати в папці: {output_data_dir.absolute()}")
    
