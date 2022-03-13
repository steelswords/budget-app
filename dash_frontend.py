#!/usr/bin/python3
# Code from https://dash.plotly.com/datatable/editable
from dash import Dash, dash_table, dcc, html, State
from dash.dash_table import DataTable, FormatTemplate
from dash.dependencies import Input, Output
import calendar
import pandas as pd
from budget import *

app = Dash(__name__, title="Budget App")

print(getBudgetCategories(db))

money = FormatTemplate.money(2)

monthNames = list(calendar.month_name)[1:12]
lowerCaseMonthNames = [ m.lower() for m in list(calendar.month_name)[1:]]

bucketColumns=(
    [{'id': 'category', 'name': 'Category'}] +
    [{'id': m, 'name': m, 'type':'numeric', 'format':money} for m in list(calendar.month_name)[1:13]]
)

def getBucketData(year : int):
    result = []
    for category in getBudgetCategories(db):
        # Find the bucket allocation for each month
        innerResult = {'category': category}
        dataFrame = pd.read_sql(f"SELECT * FROM budgetbuckets where year = {year} and category = '{category}';", sqlAlchemyEngine)
        print(dataFrame)
        for month in lowerCaseMonthNames:
            amountAllocated = dataFrame[month][0]
            innerResult[month.capitalize()] = amountAllocated
        result.append(innerResult)
    return result

def getExpenseData(year : int):
    """Returns a list of dictionaries representing how much was spent in each
    category for each month. E.g. [{'January': 126.33}, {'February': 12.77}...]
    The inner lists are in the same order of categories as getBudgetCategories() returns"""
    result = []
    categories = getBudgetCategories(db)
    for category in categories:
        # Find the sum of expenses for each month, add them to list
        innerResult = {'category': category}
        dataFrame = pd.read_sql(f"SELECT * FROM {expenseTableName} WHERE category = '{category}'", sqlAlchemyEngine)
        # Add list to list of lists
        for month in range(1,13):
            amountSpent = dataFrame.query(f'month == {month}').amount.sum()
            monthString = list(calendar.month_name)[month]
            innerResult[monthString] = amountSpent
        result.append(innerResult)
    print(result)
    return result

def getTooltipData(year : int):
    """Returns tooltip_data for the combined table, populated with Markdown tables and properly formatted """
    buckets = getBucketData(2022)
    dataFrame = pd.read_sql(f"SELECT * FROM {expenseTableName}", sqlAlchemyEngine)
    tooltips = []
    for index in range(0, len(buckets)):
        category = buckets[index]['category']
        innerDictionary = {m : {'value': "", 'type': 'markdown'} for m in monthNames}
        for month in monthNames:
            innerDictionary[month]['value'] = getMarkdownTableFromExpenses(year, month, category, dataFrame)
        # Every odd row contians buckets, not expenses. So we don't want there to be a tooltip there.
        tooltips.append({m: "" for m in monthNames})
        tooltips.append(innerDictionary)
    return tooltips

def getMarkdownTableFromExpenses(year : int, month : str, category : str, dataFrame) -> str:
    """Returns a string that contains a Markdown table detailing the day, amount, and desscription of
    all expenses meeting year, month, and category parameters"""
    tooltip = "|Day| Amount | Description |"
    tooltip += "\n|---|-----|-------------------|"
    relevantData = dataFrame.query(f"year == {year} and month == {monthNameToNumber(month)} and category == '{category}'")
    for index, row in relevantData.iterrows():
        amountFormattedAsMoney = "${:,.2f}".format(row['amount'])
        tooltip += f"\n|{row['day']}| {amountFormattedAsMoney} | {row['description']} |"
    return tooltip

def getCombinedTable():
    """Returns a DataTable that interleaves the alloted bucket amounts with the total expenses per month for each
    category"""
    buckets = getBucketData(2022)
    expenses = getExpenseData(2022)
    tooltips = []
    result = []
    for index in range(0, len(buckets)):
        bucketsRow = buckets[index]
        expensesRow = expenses[index]
        baseCategoryName = expensesRow['category']
        # Add a name to expenses category name
        expensesRow['category'] = baseCategoryName + ' - Spent'
        print(f"Combining {bucketsRow['category']} with {expensesRow['category']}")
        result.append(bucketsRow)
        result.append(expensesRow)

    return dash_table.DataTable(id='combined-bucket-expenses-table',
        columns = bucketColumns,
        data = result,
        editable = False,
        style_data_conditional = [
            {
                'if' : {'row_index': 'even'},
                'backgroundColor' : 'rgb(230,230,230)',
            }
        ],
        tooltip_data = getTooltipData(2022),
        tooltip_duration=None, # So they will stay up indefinitely
    )

bucketPage = [
    html.H2("Budget by Category and Month"),
    dash_table.DataTable(
        id='bucket-budget-edit-table',
        columns = bucketColumns,
        data = getBucketData(2022),
        editable=True,
        style_data_conditional = [
            {
                'if' : {'row_index': 'even'},
                'backgroundColor' : 'rgb(230,230,230)',
            }
        ],
    ),
    html.Button('Save', id='save-buckets', n_clicks=0),
    html.Button('Copy Buckets to Next Month', id='copy-buckets', n_clicks=0),
    html.H2("Budget and Expenses by Category and Month"),
    html.P("Remember to refresh this page if you've added expenses!"),
    getCombinedTable(),
    html.Div(id='empty-output')
]

expensePage = [
    html.H1("Expenses"),
    dcc.Dropdown(["2022"], "2022", id='expense-year'),
    dcc.Dropdown(list(calendar.month_name), "January", id="expense-month"),
    html.Div(dcc.Input(id="expense-day", type="number", placeholder="Day")),
    dcc.Dropdown(getBudgetCategories(db), "Food", id="expense-category-dropdown"),
    "Amount: ",
    dcc.Input(id="expense-amount", type="number", placeholder="Amount"),
    "Description: ",
    dcc.Input(id="expense-description", type="text",placeholder="Description"),
    html.Button('Add', id='add-expense', n_clicks=0),
    html.Div(id='expense-output')
]

# Main layout
# This is a function so when you refresh the page the buckets will update.
# TODO: Get this to happen dynamically whenever you add entries.
def serve_layout():
    return html.Div([
        html.H1('Budget'),
        dcc.Tabs([
            dcc.Tab(label='View', children = bucketPage),
            dcc.Tab(label='Edit', children = expensePage)
        ])
    ])

app.layout = serve_layout()

# Callback to update expense 

# Callback to update budget buckets
@app.callback(
    Output('combined-bucket-expenses-table', 'data'),
    State('bucket-budget-edit-table', 'data'),
    Input('bucket-budget-edit-table', 'data_timestamp'),
    Input('bucket-budget-edit-table', 'columns'))
def budgetBucketCallback(data, data_timestamp, columns):
    monthNames = list(calendar.month_name)
    for row in data:
        # Update the database. This gets expensive, so it might be worthwhile later to
        # cache this data and check for changes somewhere
        for monthNumber in range(1,13):
            budgetedAmount = row[monthNames[monthNumber]]
            if budgetedAmount is None:
                budgetedAmount = 0
            #print(f"Setting {row['category']} for month {monthNumber} to {budgetedAmount}")
            setBucketBudget(year = 2022, category = row['category'],
                month = monthNumber, amountBudgeted = budgetedAmount)
    return getCombinedTable()

# Callback to add Budget Expenses
@app.callback(
    Output('expense-output', 'children'),
    Output('expense-day', 'value'),
    Output('expense-category-dropdown', 'value'),
    Output('expense-amount', 'value'),
    Output('expense-description', 'value'),
    State('expense-year', 'value'),
    State('expense-month', 'value'),
    State('expense-day', 'value'),
    State('expense-category-dropdown', 'value'),
    State('expense-amount', 'value'),
    State('expense-description', 'value'),
    Input('add-expense', 'n_clicks'))
def add_expense_callback(expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount, expenseDescription, n_clicks):
    month = monthNameToNumber(expenseMonth)
    expenseString = f"expense from {expenseYear}-{month}-{expenseDay}: {expenseCategory}: {expenseAmount} ({expenseDescription})"
    if expenseDay is not None and expenseAmount is not None and expenseDescription is not None and expenseCategory is not None:
        print(f"Adding {expenseString}")
        addBudgetExpense(db, expenseYear, month,
                expenseDay, expenseCategory, expenseAmount, expenseDescription)
    else:
        print(f"Could not add {expenseString}")
    return expenseString, "", None, None, ""

if __name__ == '__main__':
    app.run_server(debug=True)


