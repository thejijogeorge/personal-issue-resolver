import os
import pyodbc
from config import get_env

def get_db_connection():
    server = get_env("DB_SERVER")
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')  # Change to your DB name
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PWD')
    # The driver name must match what is installed on your Windows machine
    driver = '{ODBC Driver 17 for SQL Server}'
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes'

    return pyodbc.connect(conn_str)