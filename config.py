import os
from dotenv import load_dotenv
load_dotenv() # Reads env vars from .env file

def getDatabaseConfigs():
    # TODO: By the user: fill in these parameters
    return f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} host={os.getenv('DB_HOST')} password={os.getenv('DB_PASS')}"

def getSqlAlchemyConnectionString():
    username=os.getenv('DB_USER')
    password=os.getenv('DB_PASS')
    database=os.getenv('DB_NAME')
    host=os.getenv('DB_HOST')

    return f"postgresql+psycopg2://{username}:{password}@{host}:5432/{database}"
