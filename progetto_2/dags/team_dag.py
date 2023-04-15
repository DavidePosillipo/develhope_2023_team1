from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

from src.DataIngestor import DataIngestor
from src.DataCleaner import DataCleaner
from src.DataVisualizer import DataVisualizer
from src.DataAnalyser import DataAnalyser

di = DataIngestor()
dc = DataCleaner()
da = DataAnalyser()
dv = DataVisualizer()

default_dag_args = {
    'start_date': datetime(2023, 4, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'project_id': 1
}

def function_1(**context):

    print('start function_1')
    # import dataframe
    google_data = di.read_file("./progetto_2/data/raw/googleplaystore.csv")
    # save dataframe using XCom
    context['ti'].xcom_push(key='google', value=google_data)
    print('function_1 done')

def function_2(**context):

    print('start function_2')
    # getting dataframe from Context
    google_data = context['ti'].xcom_pull(key='google')
    # cleaning dataframe using DataCleaner Class
    google_data = dc.clean_google(google_data)
    # save dataframe using XCom
    context['ti'].xcom_push(key='google', value=google_data)
    print('function_2 done')

def function_3(**context):

    print('start function_3')
    # import dataframe
    google_reviews = di.read_file('./progetto_2/data/raw/googleplaystore_user_reviews.csv')
    # save dataframe using XCom
    context['ti'].xcom_push(key='reviews', value=google_reviews)
    print('function_3 done')

def function_4(**context):

    print('start function_4')
    # getting dataframe from Context
    google_data = context['ti'].xcom_pull(key='google')
    google_reviews = context['ti'].xcom_pull(key='reviews')
    # cleaning dataframe using DataCleaner Class
    google_reviews = dc.clean_google_reviews(google_reviews, google_data)
    # save dataframe using XCom
    context['ti'].xcom_push(key='reviews', value=google_reviews)
    print('function_4 done')

def function_5():
    # create app database
    pass

def function_6():
    # create review database
    pass

def function_7(**context):

    print('start function_7')
    # save app dataframe on database
    google_data = context['ti'].xcom_pull(key='google')
    di.to_cloud(google_data, to_table='NOMETABELLA', if_exists='fail', index=False)
    print('function_7 done')

def function_8(**context):
    print('start function_8')
    # save review dataframe on database
    google_reviews = context['ti'].xcom_pull(key='reviews')
    di.to_cloud(google_reviews, to_table='NOMETABELLA', if_exists='fail', index=False)
    print('function_8 done')
    
def function_9(**context):
    print('start function_9')
    # getting app and reviews dataframe
    google_data = context['ti'].xcom_pull(key='google')
    google_reviews = context['ti'].xcom_pull(key='reviews')
    # running analysis
    google_data = da.assign_sentiment(google_data, google_reviews)
    context['ti'].xcom_push(key='google_data', value=google_data)
    print('function_9 done')

def function_10():
    # create score database
    pass

def function_11(**context):

    print('start function_10')
    google_data = context['ti'].xcom_pull(key='google_data')
    di.to_cloud(google_data, to_table='nometabella', if_exists='fail', index=False)
    print('function_10 done')

# Define the DAG

with DAG('etl_main', default_args=default_dag_args, schedule_interval=None) as dag:

# Define the operators
    task_1 = PythonOperator(task_id='task_1',
                            python_callable=function_1,
                            provide_context=True)
    
    task_2 = PythonOperator(task_id='task_2',
                            python_callable=function_2,
                            provide_context=True)
    
    task_3 = PythonOperator(task_id='task_3',
                            python_callable=function_3,
                            provide_context=True)
    
    task_4 = PythonOperator(task_id='task_4',
                            python_callable=function_4,
                            provide_context=True)
    
    task_5 = PythonOperator(task_id='task_5',
                            python_callable=function_5,
                            provide_context=False)
    
    task_6 = PythonOperator(task_id='task_6',
                            python_callable=function_6,
                            provide_context=False)
    
    task_7 = PythonOperator(task_id='task_7',
                            python_callable=function_7,
                            provide_context=True)
    
    task_8 = PythonOperator(task_id='task_8',
                            python_callable=function_8,
                            provide_context=True)
    
    task_9 = PythonOperator(task_id='task_9',
                            python_callable=function_9,
                            provide_context=True)
    
    task_10 = PythonOperator(task_id='task_10',
                             python_callable=function_10,
                             provide_context=False)
    
    task_11 = PythonOperator(task_id='task_11',
                             python_callable=function_11,
                             provide_context=True)

# Define the task dependencies
[task_5, task_6, task_10] >> [task_1, task_3] >> task_2 >> task_4 >> task_7 >> task_8 >> task_9 >> task_11