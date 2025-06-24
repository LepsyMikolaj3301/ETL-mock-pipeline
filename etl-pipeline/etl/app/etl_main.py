from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from extract import extract_files_url
from transform import transform as transform_to_df
from load import insert_to_postgres_spark
import json





default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='etl_pipeline',
    default_args=default_args,
    description='A simple ETL pipeline',
    schedule='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    @task
    def extract(**context):
    # Placeholder for extraction logic
        with open('init/setup.json', 'r') as f:
            config = json.load(f)
        
        try:
            extract_files_url(config['sim_conn_info'])
        except RuntimeError as e:
            # FIX
            dag.task_instance.xcom_push(key='extract_failed', value=str(e)) #type: ignore
            raise
        
    @task
    def transform(**context):
        return transform_to_df()

    @task
    def load(dfs: dict, **context):
        insert_to_postgres_spark(*dfs)
        
    extract_task = extract()
    transform_task = transform()
    # FIX
    load_task = load(transform_task)
    extract_task >> transform_task >> load_task