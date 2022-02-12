#!/usr/bin/python3
import datetime
from consolemenu import *
from consolemenu.items import *
from consolemenu.prompt_utils import *

def getDateFromUser():
    inputString = str(input('date'))
    try:
        date = datetime.strptime(inputString)
        print("Entered date: ", date)
        return date
    except (Exception, ValueError) as error:
        print(error)

def addBudgetExpenseMenu(connection):
    pass

def addBudgetCategoryMenu(connection):
    """ Prompts user for category name to add """
    category = input("Enter new category name")
    addBudgetCategory(connection, category)

class ExpensesUI:
    def __init__(self, superMenu):
        pass


class BudgetUI:
    menu = ConsoleMenu("Budget App", "v 0.0a")
    def addExpenses(self):
        print("Adding expenses")
        input("Press any key to continue")

    def viewBudget(self):
        print("Viewing Budget")
        input("Press any key to continue")

    def addExpense(self):
        pu = PromptUtils(Screen())
        pu.input("Enter Amount: ")

    def manageCategories(self):
        print("Managing Categories")
        input("Press any key to continue")

    def addManageCategoriesMenu(self, menu):
        submenu = ConsoleMenu("Manage Categories", "What would you like to do?")

    def __init__(self):
        self.menu.append_item(FunctionItem("Add expenses", self.addExpense, []))
        self.menu.append_item(FunctionItem("View", self.viewBudget, []))
        self.menu.append_item(FunctionItem("Manage Categories", self.manageCategories, []))
        self.menu.show()



