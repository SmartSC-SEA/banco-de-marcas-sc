#utils/db.py
import MySQLdb
import os
from dotenv import load_dotenv
load_dotenv()  # carrega .env

DB_HOST     = os.getenv('DB_HOST')
DB_USER     = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME     = os.getenv('DB_NAME')

def connect_db():
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4'
    )

DBCAT_HOST     = os.getenv('DBCAT_HOST')
DBCAT_USER     = os.getenv('DBCAT_USER')
DBCAT_PASSWORD = os.getenv('DBCAT_PASSWORD')
DBCAT_NAME     = os.getenv('DBCAT_NAME')

def connect_catalogo():
    return MySQLdb.connect(
        host=DBCAT_HOST,
        user=DBCAT_USER,
        passwd=DBCAT_PASSWORD,
        db=DBCAT_NAME,
        charset='utf8mb4'
    )
