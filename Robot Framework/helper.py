import pandas as pd
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger


def read_dynamic_report_and_get_dates():
    """Зчитує дані з UI, групуючи їх за Y-координатою (рядками)."""
    sel_lib = BuiltIn().get_library_instance('SeleniumLibrary')
    driver = sel_lib.driver

    # 1. Карта колонок за X-координатою
    columns = driver.find_elements("class name", "y-column")
    col_mapping = {}
    for col in columns:
        try:
            header_el = col.find_element("id", "header")
            header_text = header_el.text.strip().lower().replace(' ', '_')
            x_pos = col.location['x']
            col_mapping[x_pos] = header_text
        except:
            continue

    # 2. Збір клітинок
    all_cells = driver.find_elements("css selector", ".cell-text")
    rows_data = {}

    for cell in all_cells:
        try:
            text = cell.text.strip()
            # Пропускаємо порожні та заголовки
            if not text or text.lower() in [h.replace('_', ' ') for h in col_mapping.values()]:
                continue

            loc = cell.location
            y_pos = loc['y']
            x_pos = loc['x']

            closest_x = min(col_mapping.keys(), key=lambda x: abs(x - x_pos))
            col_name = col_mapping[closest_x]

            if y_pos not in rows_data:
                rows_data[y_pos] = {}
            rows_data[y_pos][col_name] = text
        except:
            continue

    df = pd.DataFrame(list(rows_data.values()))
    if not df.empty and 'visit_date' in df.columns:
        df.dropna(subset=['visit_date'], inplace=True)

    logger.info(f"UI Data Scraped:\n{df.to_string()}")
    return df, df['visit_date'].unique().tolist()


def read_parquet_by_date_list(folder_path, date_list):
    """ЦЕЙ KEYWORD МАЄ БУТИ ТУТ: Читає Parquet та фільтрує за датами."""
    logger.info(f"Reading Parquet from {folder_path} for dates: {date_list}")
    df = pd.read_parquet(folder_path, engine='pyarrow')

    # Перетворюємо дату в рядок для порівняння
    df['visit_date'] = df['visit_date'].astype(str).str.strip()

    # Фільтрація
    filtered_df = df[df['visit_date'].isin(date_list)].copy()

    # Мапінг колонки, щоб назва збігалася з UI
    if 'avg_time_spent' in filtered_df.columns:
        filtered_df.rename(
            columns={'avg_time_spent': 'average_time_spent'}, inplace=True)

    return filtered_df


def compare_reconciled_data(df_html, df_parquet):
    """Фінальна звірка з нормалізацією."""
    def normalize(df):
        cols = ['visit_date', 'facility_type', 'average_time_spent']
        available_cols = [c for c in cols if c in df.columns]
        d = df[available_cols].copy()

        d['visit_date'] = d['visit_date'].astype(str).str.strip()
        d['facility_type'] = d['facility_type'].astype(
            str).str.strip().str.lower()
        d['average_time_spent'] = pd.to_numeric(
            d['average_time_spent'], errors='coerce').astype(float).round(2)

        return d.sort_values(by=available_cols).reset_index(drop=True)

    df_h = normalize(df_html)
    df_p = normalize(df_parquet)

    try:
        pd.testing.assert_frame_equal(df_h, df_p, check_dtype=False)
        return True, "Data is identical"
    except Exception as e:
        return False, f"Mismatch detected:\n{str(e)}"
