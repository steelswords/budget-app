#!/usr/bin/python3
import sys
from datetime import datetime
import calendar
import psycopg2
import configparser
import pandas as pd
from userInput import *
from config import *
from sqlalchemy import create_engine

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "queries/create_schema.sql")
CATEGORIES_FILE = os.path.join(os.path.dirname(__file__), "queries/categories.sql")


# Start SQLAlchemy engine for getting pandas dataframes from the db
sqlAlchemyEngine = None
try:
    sqlAlchemyEngine = create_engine(getSqlAlchemyConnectionString())
except(Exception) as error:
    print("An error occurred creating SqlAlchemy engine! %s" % error)


def monthNameToNumber(monthName : str) -> int:
    value = list(calendar.month_name).index(monthName)
    return value

def connect():
    connection = None
    try:
        databaseConnectionSettings = getDatabaseConfigs()
        connection = psycopg2.connect(databaseConnectionSettings)

        cur = connection.cursor()

        print("Connected to database. PostgreSQL version: ")
        cur.execute("select version()")
        print(cur.fetchone())

    except(Exception, psycopg2.DatabaseError) as error:
        print("ERROR! %s" % error)
    return connection

# Start a PostgresQL database conneciton
try:
    db = connect()
except (Exception) as error:
    print(error)


def ensureDatabaseSchema(connection):
    """ Ensure the database is properly set up with the proper tables. """
    try:
        cur = connection.cursor()
        with open(SCHEMA_FILE, 'r') as f:
            result_iterator = cur.execute(f.read())
        connection.commit()
        with open(CATEGORIES_FILE, 'r') as f:
            result_iterator = cur.execute(f.read())
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def getBudgetCategories(connection):
    try:
        cur = connection.cursor()
        cur.execute("SELECT name FROM categories ORDER BY table_order ASC;")
        categories = cur.fetchall()
        connection.commit()
        cur.close()
        return [i[0] for i in categories]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def isBudgetCategoryPresent(connection, categoryName : str) -> bool:
    cur = connection.cursor()
    cur.execute("SELECT name FROM categories where name = %s;", (categoryName,))
    matches = cur.fetchall()
    connection.commit()
    cur.close()
    return len(matches) > 0

def addBudgetCategory(connection, categoryName, order=100):
    """ Adds a budget category to the database if it doesn't already exist """
    if connection is None:
        print("ERROR: Connection not open!")
        return
    try:
        if isBudgetCategoryPresent(connection, categoryName):
            print("{} is already present in categories table".format(categoryName))
            #return
        cur = connection.cursor()
        cur.execute("INSERT INTO categories(name, table_order) VALUES(%s, %s);", (categoryName,order,))
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        addBucketBudget(2022, categoryName)

def getBudgetExpenses(connection):
    try:
        cur = connection.cursor()
        cur.execute("SELECT * FROM {}".format(expenseTableName));
        connection.commit()
        expenses = cur.fetchall()
        cur.close()
        return expenses
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def addBudgetExpense(connection, year : int, month : int, day : int, category : str,
        amount : float, description : str):
    try:
        cur = connection.cursor()
        sqlCmd = "INSERT INTO {}(year, month, day, amount, category, description) VALUES ({}, {}, {}, {}, '{}', '{}');".format(expenseTableName, year, month, day, amount, category, description)
        cur.execute(sqlCmd)
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def getBucketsByYear(year : int):
    """Returns pandas dataframe with category and allocations by month"""
    try:
        return pd.read_sql(f"SELECT * FROM budgetbuckets where year = {year};", sqlAlchemyEngine)
    except Exception as error:
        print(error)

def addBucketBudget(year : int, category : str):
    cur = db.cursor()
    sqlCmd = f"INSERT INTO budgetbuckets(category, year) VALUES ('{category}', {year});"
    try:
        cur.execute(sqlCmd)
        db.commit()
        cur.close()
    except Exception as error:
        print(error)
    
def setBucketBudget(year : int, category : str, month : int, amountBudgeted = 0):
    """Sets the budget for a specified category in a specified month."""
    # TODO: If the category/year does not exist in the table, create it.
    monthName = list(calendar.month_name)[month]

    # Commit to database
    sqlCmd = f"UPDATE budgetbuckets SET {monthName} = {amountBudgeted} where category='{category}';"
    #print(sqlCmd)
    try:
        cur = db.cursor()
        cur.execute(sqlCmd)
        db.commit()
        cur.close()
    except Exception as error:
        print(error)

def getBucketDataframe():
    try:
        sqlCmd = "SELECT * FROM budgetbuckets;"
        return pd.read_sql(sqlCmd, sqlAlchemyEngine)
    except Exception as error:
        print(error)

def main():
    connection = connect()
    ensureDatabaseSchema(connection)
    print("Categories: ")
    print(getBudgetCategories(connection))
    # getDateFromUser()

if __name__ == '__main__':
    main()

