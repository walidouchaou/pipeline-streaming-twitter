from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from main import main

# Définition des comptes Twitter et du type de ligne
COMPTES_TWITTER_RER = [
    "https://x.com/RER_A",
    "https://x.com/RERB",
    "https://x.com/RERC_SNCF",
    "https://x.com/RERD_SNCF",
    "https://x.com/RERE_T4_SNCF",
    "https://x.com/LigneH_SNCF",
    "https://x.com/LIGNEJ_SNCF",
    "https://x.com/LigneK_SNCF",
    "https://x.com/LIGNEL_sncf",
    "https://x.com/lignesNetU_SNCF",
    "https://x.com/LIGNEP_SNCF",
    "https://x.com/LIGNER_SNCF"
]

COMPTES_TWITTER_METRO = [
    "https://x.com/Ligne1_RATP",
    "https://x.com/Ligne2_RATP",
    "https://x.com/Ligne3_RATP",
    "https://x.com/Ligne4_RATP",
    "https://x.com/Ligne5_RATP",
    "https://x.com/Ligne6_RATP",
    "https://x.com/Ligne7_RATP",
    "https://x.com/Ligne8_RATP",
    "https://x.com/Ligne9_RATP",
    "https://x.com/Ligne10_RATP",
    "https://x.com/Ligne11_RATP",
    "https://x.com/Ligne12_RATP",
    "https://x.com/Ligne13_RATP",
    "https://x.com/Ligne14_RATP",
]

LIGNE_TYPE = "RER"  # ou le type que vous souhaitez utiliser

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'il_de_france_twitter',
    default_args=default_args,
    description='Scraping des tweets il de france',
    schedule_interval=None,
)

rer_twitter = PythonOperator(
    task_id='RER_twitter',
    python_callable=main,
    op_kwargs={
        'comptes_twitter': COMPTES_TWITTER_RER,
        'ligne_type': LIGNE_TYPE
    },
    dag=dag,
)
metro_twitter = PythonOperator(
    task_id='METRO_twitter',
    python_callable=main,
    op_kwargs={
        'comptes_twitter': COMPTES_TWITTER_METRO,
        'ligne_type': "METRO"
    },
    
    dag=dag,
)
rer_twitter >> metro_twitter



