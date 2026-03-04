import pandas as pd
from sklearn.datasets import fetch_california_housing
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from train_model_v2 import train


def download_data():
    data = fetch_california_housing(as_frame=True)
    df = data.frame
    df.to_csv("california_raw.csv", index=False)
    print(f"Загружено строк: {df.shape[0]}")


def clear_data():
    df = pd.read_csv("california_raw.csv")

    df = df[df['MedHouseVal'] < 5.0]

    df = df[df['AveRooms'] < 15]

    df = df[df['AveOccup'] < 6]

    df.to_csv('df_clear.csv', index=False)
    return True


dag_apartments = DAG(
    dag_id="california_housing_pipe",
    start_date=datetime(2026, 3, 1),
    schedule_interval="@weekly",
    catchup=False,
)

t1 = PythonOperator(task_id="get_data", python_callable=download_data, dag=dag_apartments)
t2 = PythonOperator(task_id="clean_data", python_callable=clear_data, dag=dag_apartments)
t3 = PythonOperator(task_id="train_model", python_callable=train, dag=dag_apartments)

t1 >> t2 >> t3
