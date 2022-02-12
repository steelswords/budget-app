#!/usr/bin/python3

from datetime import datetime
import psycopg2
import configparser
from userInput import *
from config import getDatabaseConfigs

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

def ensureDatabaseSchema(connection):
    """ Ensure the database is properly set up with the proper tables. """
    commands = (
            """
            CREATE TABLE categories(
                name varchar(200) not null,
                primary key(name)
            )
            """,
            """
            CREATE TABLE expenses(
                year smallint not null,
                month smallint not null,
                day smallint not null,
                amount numeric,
                category varchar(200) references categories(name),
                description varchar(500)
            )
            """,
            """
            CREATE TABLE budgetbuckets(
                year smallint not null,
                month smallint not null,
                category varchar(200) references categories(name)
                )
            """
    )
    try:
        cur = connection.cursor()
        for command in commands:
            cur.execute(command)
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
        return categories
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def addBudgetCategory(connection, categoryName):
    """ Adds a budget category to the database """
    if connection is None:
        print("ERROR: Connection not open!")
        return
    try:
        cur = connection.cursor()
        cur.execute("INSERT INTO categories(name) VALUES(%s)", (categoryName,))
        connection.commit()
        cur.close()
        print("Budget Categories: ")
        print(getBudgetCategories(connection))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def getBudgetExpenses(connection):
    try:
        cur = connection.cursor()
        cur.execute("SELECT * FROM expenses");
        connection.commit()
        expenses = expenses.fetchall()
        cur.close()
        return expenses
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def addBudgetExpense(connection, year, month, day, category, amount, description):
    try:
        cur = connection.cursor()
        cur.execute("INSERT INTO expenses(year, month, day, amount, category,description) VALUES(%s)",
                (year, month, day, amount, category, description))
        connection.commit()
        cur.close()
        print("Budget Categories: ")
        print(getBudgetCategories(connection))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)



def main():
    connection = connect()
    #ensureDatabaseSchema(connection)
    print("Categories: ")
    print(getBudgetCategories(connection))
    getDateFromUser()







if __name__ == '__main__':
    budget = BudgetUI()


