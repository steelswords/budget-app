#!/usr/bin/python3

from datetime import datetime
import calendar
import psycopg2
import configparser
from userInput import *
from config import getDatabaseConfigs

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

def ensureDatabaseSchema(connection):
    """ Ensure the database is properly set up with the proper tables. """
    commands = (
            """
            CREATE TABLE IF NOT EXISTS categories(
                name varchar(200) not null,
                primary key(name)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS expenses(
                year smallint not null,
                month smallint not null,
                day smallint not null,
                amount numeric,
                category varchar(200) references categories(name),
                description varchar(500)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS budgetbuckets(
                year smallint not null,
                month smallint not null,
                category varchar(200) references categories(name)
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
            "Decorations",
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
            addBudgetCategory(connection, category)
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
            return
        cur = connection.cursor()
        cur.execute("INSERT INTO categories(name) VALUES(%s)", (categoryName,))
        connection.commit()
        cur.close()
        #print("Budget Categories: ")
        #print(getBudgetCategories(connection))
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
        cur.execute("INSERT INTO expenses(year, month, day, amount, category,description) VALUES (%s)",
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


