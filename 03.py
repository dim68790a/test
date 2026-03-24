import json
import logging
import os

import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Параметры подключения к вашему API
MOVIELENS_HOST = os.environ.get("MOVIELENS_HOST", "carsapi")
MOVIELENS_SCHEMA = os.environ.get("MOVIELENS_SCHEMA", "http")
MOVIELENS_PORT = os.environ.get("MOVIELENS_PORT", "8081")

MOVIELENS_USER = os.environ["MOVIELENS_USER"]
MOVIELENS_PASSWORD = os.environ["MOVIELENS_PASSWORD"]

# Настройка логгера
logger = logging.getLogger(__name__)


def _get_session():
    """Создаёт сессию для запросов к вашему Car API."""
    session = requests.Session()
    session.auth = (MOVIELENS_USER, MOVIELENS_PASSWORD)
    base_url = f"{MOVIELENS_SCHEMA}://{MOVIELENS_HOST}:{MOVIELENS_PORT}"
    return session, base_url


def _get_all_cars(batch_size=100):
    """Получает все записи из /cars с пагинацией."""
    session, base_url = _get_session()
    url = f"{base_url}/cars"

    offset = 0
    total = None
    all_cars = []

    while total is None or offset < total:
        params = {"offset": offset, "limit": batch_size}
        response = session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        all_cars.extend(data["result"])
        offset += batch_size
        total = data["total"]

        if len(data["result"]) == 0:
            break

    return all_cars


def fetch_cars(**context):
    """Загружает все автомобили и сохраняет в JSON."""
    logger.info("Fetching all cars from the API...")

    cars = _get_all_cars(batch_size=100)
    logger.info(f"Fetched {len(cars)} car records.")

    # Путь для сохранения
    output_path = "/data/cars/cars_full.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(cars, f)

    logger.info(f"Saved cars to {output_path}")
    
    # Передаем путь к файлу в XCom для следующего таска
    context['ti'].xcom_push(key='raw_data_path', value=output_path)


def clean_cars_data(**context):
    """Предобработка данных: удаление дубликатов, пропусков, преобразование категориальных признаков."""
    # Получаем путь к сырым данным из XCom
    raw_data_path = context['ti'].xcom_pull(key='raw_data_path', task_ids='fetch_cars')
    
    if not raw_data_path:
        # Если XCom пуст, используем путь по умолчанию
        raw_data_path = "/data/cars/cars_full.json"
    
    logger.info(f"Loading raw data from {raw_data_path}")
    
    # Загружаем JSON
    with open(raw_data_path, "r") as f:
        raw_cars = json.load(f)
    
    # Конвертируем в DataFrame
    df = pd.DataFrame(raw_cars)
    logger.info(f"Loaded {len(df)} records")
    
    # 1. Удаляем дубликаты
    initial_count = len(df)
    df = df.drop_duplicates()
    logger.info(f"Removed {initial_count - len(df)} duplicate rows")
    
    # 2. Удаляем строки с пропущенными значениями в критических колонках
    critical_columns = ['Make', 'Model', 'Year', 'Price_euro']
    before_dropna = len(df)
    df = df.dropna(subset=critical_columns)
    logger.info(f"Removed {before_dropna - len(df)} rows with missing critical values")
    
    # 3. Преобразуем категориальные признаки в числовые
    # Определяем маппинг для Fuel_type
    fuel_mapping = {
        'Petrol': 0,
        'Diesel': 1,
        'Hybrid': 2,
        'Electric': 3,
        'Plug-in Hybrid': 4,
        'Metan/Propan': 5,
        'Metan/Propan?': 5  # для возможных вариаций
    }
    
    # Нормализуем значения Fuel_type (приводим к нижнему регистру и стандартизируем)
    if 'Fuel_type' in df.columns:
        # Заменяем возможные варианты на стандартные
        df['Fuel_type_clean'] = df['Fuel_type'].astype(str).str.strip()
        # Создаем числовую колонку
        df['Fuel_type_encoded'] = df['Fuel_type_clean'].map(fuel_mapping)
        # Заполняем неизвестные значения -1
        df['Fuel_type_encoded'] = df['Fuel_type_encoded'].fillna(-1).astype(int)
        logger.info(f"Fuel_type mapping completed. Unique values: {df['Fuel_type_clean'].nunique()}")
    else:
        logger.warning("Fuel_type column not found")
        df['Fuel_type_encoded'] = -1
    
    # Определяем маппинг для Transmission
    transmission_mapping = {
        'Manual': 1,
        'Automatic': 0,
        'Auto': 0,
        'Manual?': 1  # для возможных вариаций
    }
    
    if 'Transmission' in df.columns:
        df['Transmission_clean'] = df['Transmission'].astype(str).str.strip()
        df['Transmission_encoded'] = df['Transmission_clean'].map(transmission_mapping)
        df['Transmission_encoded'] = df['Transmission_encoded'].fillna(-1).astype(int)
        logger.info(f"Transmission mapping completed. Unique values: {df['Transmission_clean'].nunique()}")
    else:
        logger.warning("Transmission column not found")
        df['Transmission_encoded'] = -1
    
    # 4. Удаляем временные колонки
    df = df.drop(columns=['Fuel_type_clean', 'Transmission_clean'], errors='ignore')
    
    # 5. Сохраняем очищенный датасет
    output_dir = "/data/cleaned"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/cars_cleaned.json"
    
    # Сохраняем в JSON
    df.to_json(output_path, orient='records', indent=2)
    logger.info(f"Saved cleaned data to {output_path}")
    
    # Сохраняем также в CSV для удобства
    csv_output_path = f"{output_dir}/cars_cleaned.csv"
    df.to_csv(csv_output_path, index=False)
    logger.info(f"Saved cleaned data to {csv_output_path}")
    
    # Сохраняем статистику
    stats = {
        'original_count': len(raw_cars),
        'after_deduplication': initial_count,
        'after_na_removal': len(df),
        'final_count': len(df),
        'columns': list(df.columns),
        'fuel_types_present': df['Fuel_type_encoded'].unique().tolist(),
        'transmission_types_present': df['Transmission_encoded'].unique().tolist()
    }
    
    stats_path = f"{output_dir}/cleaning_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Saved cleaning statistics to {stats_path}")
    
    return stats


def analyze_cars(**context):
    """Анализирует данные: например, средняя цена по году."""
    input_path = "/data/cleaned/cars_cleaned.csv"
    output_path = "/data/cars/price_by_year.csv"

    logger.info(f"Reading cleaned cars from {input_path}")
    df = pd.read_csv(input_path)

    if df.empty:
        logger.warning("No car data to analyze.")
        return

    # Пример анализа: средняя цена по году
    summary = df.groupby("Year")["Price_euro"].agg(
        mean_price="mean",
        count="count",
        min_price="min",
        max_price="max"
    ).round(2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary.to_csv(output_path)
    logger.info(f"Analysis saved to {output_path}")
    
    # Дополнительный анализ: средняя цена по типу топлива
    fuel_summary = df.groupby("Fuel_type_encoded")["Price_euro"].agg(
        mean_price="mean",
        count="count",
        min_price="min",
        max_price="max"
    ).round(2)
    
    fuel_output_path = "/data/cars/price_by_fuel.csv"
    fuel_summary.to_csv(fuel_output_path)
    logger.info(f"Fuel analysis saved to {fuel_output_path}")


# Определяем DAG
with DAG(
    dag_id="01_cars",
    description="Fetches car data from the custom API, cleans it, and analyzes it.",
    start_date=datetime(2026, 2, 3),  # сегодняшняя дата (ваш контекст)
    schedule="@daily",               # можно оставить daily или сделать @once
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_cars",
        python_callable=fetch_cars,
    )

    clean_task = PythonOperator(
        task_id="clean_cars_data",
        python_callable=clean_cars_data,
    )

    analyze_task = PythonOperator(
        task_id="analyze_cars",
        python_callable=analyze_cars,
    )

    fetch_task >> clean_task >> analyze_task
