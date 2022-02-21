#!/usr/bin/python3
from budget import *
import csv
import random
from calendar import monthrange
import random

def seedDatabase(connection, filename="seed_expenses.csv"):
    """Inserts seed expense entries into the database."""

    ensureDatabaseSchema(connection)
    categories = getBudgetCategories(connection)
    numberToGeneratePerMonth = 40
    for month in range(1,12):
        for i in range(numberToGeneratePerMonth):
            year=2022
            numberOfDaysInMonth = monthrange(year, month)[1]
            day = random.randrange(1, numberOfDaysInMonth +1)
            itemCategory = categories[random.randrange(0,len(categories))]
            amount = random.uniform(1,45)
            description = f"Seed expense {i}"
            addBudgetExpense(connection, year, month, day, itemCategory, amount, description)
            print(f"Inserted seed expense: {year}/{month}/{day}: {amount} in '{itemCategory}': {description}")

if __name__ == "__main__":
    connection = connect()
    seedDatabase(connection)
