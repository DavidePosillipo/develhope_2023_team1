import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import psycopg2
from sqlalchemy import create_engine

from src.DataIngestor import DataIngestor
from src.DataCleaner import DataCleaner
from src.DataVisualizer import DataVisualizer
from src.DataAnalyser import DataAnalyser

di = DataIngestor()
dc = DataCleaner()
da = DataAnalyser()
dv = DataVisualizer()

# import, clean, and export google_data can be done in one function. need another class? is it worth?
google_data = di.read_file("./progetto_2/data/raw/googleplaystore.csv")
google_data = dc.clean_google(google_data)

google_reviews = di.read_file('./progetto_2/data/raw/googleplaystore_user_reviews.csv')
google_reviews = dc.clean_google_reviews(google_reviews)

#creo la connessione al database con psycopg2
conn = di.connect(dbname='postgres',
                  dbuser='postgres',
                  dbhost='localhost',
                  dbport='5432')

#creo le tabelle vuote tramite psycopg passando internamente le ddl
di.create_google(conn)
di.create_reviews(conn)

# creo una connessione al database compatibile con il metodo db.to_sql(), usando la libreria sqlalchemy
engine=di.create_engine(dbname='postgres',
                        dbuser='postgres',
                        dbhost='localhost',
                        dbport='5432')

#carico i dati dei dataframe dentro postgress, che fungera' ora da data warehouseb
di.load(google_data,'googleplaystore',engine,replace=True,conn=conn)
di.load(google_reviews,'google_reviews',engine,replace=True,conn=conn)