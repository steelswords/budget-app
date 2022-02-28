#!/usr/bin/python3

from datetime import datetime
import calendar
import psycopg2
import configparser
import pandas as pd
from userInput import *
from config import *
from sqlalchemy import create_engine

testing=True
expenseTableName="expenses"
if testing:
    expenseTableName="seedexpenses"

# Start SQLAlchemy engine for getting pandas dataframes from the db
sqlAlchemyEngine = None
try:
    sqlAlchemyEngine = create_engine(getSqlAlchemyConnectionString())
except(Exception) as error:
    print("An error occurred! %s" % error)


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
db = connect()

def ensureDatabaseSchema(connection):
    """ Ensure the database is properly set up with the proper tables. """
    commands = (
            """
            CREATE TABLE IF NOT EXISTS categories(
                name varchar(200) not null,
                primary key(name),
                UNIQUE(name)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS {}(
                year smallint not null,
                month smallint not null,
                day smallint not null,
                amount numeric,
                category varchar(200) references categories(name),
                description varchar(500),
                UNIQUE(year, month, day, amount, category, description)
            )
            """.format(expenseTableName),
            """
            CREATE TABLE IF NOT EXISTS budgetbuckets(
                category varchar(200) references categories(name),
                year smallint not null,
                January numeric,
                February numeric,
                March numeric,
                April numeric,
                May numeric,
                June numeric,
                July numeric,
                August numeric,
                September numeric,
                October numeric,
                November numeric,
                December numeric,
                UNIQUE(category, year)
                )
            """,
    )
    categories = [
            "Food",
            "Tristan - WTF",
            "Mar - WTF",
            "Household Discretionary",
            "Date",
            "Eating Out",
            "Clothes",
            "Tech Budget",
            "Decorations",
            "Gifts",
            "Furniture",
            "Gas",
            "Laundry",
            "Haircuts",
            "Medical",
            "Classroom",
            "Birthday Budget",
            "Down payment",
            "Vacation",
            "Rent",
            "Car Maintenance",
            "Health Insurance",
            "Car Payment",
            "Phone Bill",
            "Car insurance",
            "Gas Power",
            "Electricity",
            "Retirement Contribution",
            "Savings Contribution",
            "Christmas Budget",
            "Christmas Siblings",
            ]
    try:
        cur = connection.cursor()
        for command in commands:
            cur.execute(command)
        for category in categories:
            try:
                addBudgetCategory(connection, category)
            except Exception as error:
                print(error)
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def getBudgetCategories(connection):
    try:
        cur = connection.cursor()
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        connection.commit()
        cur.close()
        return [i[0] for i in categories]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def isBudgetCategoryPresent(connection, categoryName : str) -> bool:
    cur = connection.cursor()
    #cur.execute("SELECT * FROM categories where name ilike %s", (categoryName))
    cur.execute("SELECT * FROM categories where name = %s;", (categoryName,))
    matches = cur.fetchall()
    connection.commit()
    cur.close()
    # print(matches)
    return len(matches) > 0

def addBudgetCategory(connection, categoryName):
    """ Adds a budget category to the database if it doesn't already exist """
    if connection is None:
        print("ERROR: Connection not open!")
        return
    try:
        if isBudgetCategoryPresent(connection, categoryName):
            print("{} is already present in categories table".format(categoryName))
            #return
        cur = connection.cursor()
        cur.execute("INSERT INTO categories(name) VALUES(%s)", (categoryName,))
        connection.commit()
        cur.close()
        #print("Budget Categories: ")
        #print(getBudgetCategories(connection))
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

#def setBucketCategory(year : int, month : int, category : str, amountToBudget):
#    try:
#        cur = connection.cursor()
#        sqlCmd = f"INSERT INTO budgetbuckets(year, month, category, amount) VALUES ({year}, {month}, {category}, {amountToBudget})"
#        cur.execute(sqlCmd)
#        connection.commit()
#        cur.close()
#    except (Exception, psycopg2.DatabaseError) as error:
#        print(error)

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
    
def setBucketBudget(year : int, category : str, month : int, amountBudgeted):
    """Sets the budget for a specified category in a specified month."""
    # TODO: If the category/year does not exist in the table, create it.
    monthName = list(calendar.month_name)[month]

    # Commit to database
    sqlCmd = f"UPDATE budgetbuckets SET {monthName} = {amountBudgeted} where category='{category}';"
    print(sqlCmd)
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
    #ensureDatabaseSchema(connection)
    print("Categories: ")
    print(getBudgetCategories(connection))
    getDateFromUser()

if __name__ == '__main__':
    setBucketBudget(2022, 'Food', 5, 399)


