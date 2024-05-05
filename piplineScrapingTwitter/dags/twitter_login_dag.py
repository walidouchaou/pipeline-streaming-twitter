from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from main import main

DAG_START_DATE = datetime(2024, 5, 3, 20, 45)
# Define the DAG
# Default arguments for the DAG
DAG_DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': DAG_START_DATE,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}




with DAG (
    'twitter_login_dag',
    description='A simple DAG to login to Twitter',
    default_args=DAG_DEFAULT_ARGS,
    schedule_interval='0 1 * * *',
    catchup=False,
    max_active_runs=1,
) as dag:
    # Define the task
    login_twitter_task = PythonOperator(
        task_id='login_twitter',
        python_callable=main,
        dag=dag
    )


    # Définissez la dépendance entre les tâches ici
    login_twitter_task