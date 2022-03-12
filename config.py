import os
from dotenv import load_dotenv
load_dotenv() # Reads env vars from .env file

username=os.getenv('DB_USER')
password=os.getenv('DB_PASS')
database=os.getenv('DB_NAME')
host=os.getenv('DB_HOST')

def getDatabaseConfigs():
    return f"dbname={database} user={username} host={host} password={password}"

def getSqlAlchemyConnectionString():
    return f"postgresql+psycopg2://{username}:{password}@{host}:5432/{database}"
