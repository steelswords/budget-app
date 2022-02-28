#!/usr/bin/python3
# Code from https://dash.plotly.com/datatable/editable
from dash import Dash, dash_table, dcc, html, State
from dash.dash_table import DataTable, FormatTemplate
from dash.dependencies import Input, Output
import calendar
import pandas as pd
from budget import *

app = Dash(__name__)
app.Title = "Budget App"

print(getBudgetCategories(db))

money = FormatTemplate.money(2)

lowerCaseMonthNames = [ m.lower() for m in list(calendar.month_name)[1:]]

def getBucketPageData():
    categories = getBudgetCategories(db)
    data = []
    for i in range(0, len(categories)):
        data += [{'category': categories[i]}]
        data += [{'category': "Spent:"}]
    return data


params = [
    'Weight', 'Torque', 'Width', 'Height',
    'Efficiency', 'Power', 'Displacement'
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

viewPage = [
    dash_table.DataTable(
        id='table-editing-simple',
        columns=(
            [{'id': 'Model', 'name': 'Model'}] +
            [{'id': p, 'name': p} for p in params]
        ),
        data=[
            dict(Model=i, **{param: 0 for param in params})
            for i in range(1, 5)
        ],
        editable=True
    ),
]

monthNames = list(calendar.month_name)[1:12]

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

def getBucketData(year : int):
    wholeDataFrame = pd.read_sql(f"SELECT * FROM budgetbuckets where year = {year}", sqlAlchemyEngine)
    result = []
    for category in wholeDataFrame['category']:
        # Find the bucket allocation for each month
        innerResult = {'category': category}
        dataFrame = pd.read_sql(f"SELECT * FROM budgetbuckets where year = {year} and category = '{category}';", sqlAlchemyEngine)
        print(dataFrame)
        for month in lowerCaseMonthNames:
            amountAllocated = dataFrame[month][0]
            innerResult[month.capitalize()] = amountAllocated
        result.append(innerResult)
    #print(result)
    return result

#def getBucketData(year : int):
#    dataFrame = pd.read_sql(f"SELECT * FROM budgetbuckets where year = {year};", sqlAlchemyEngine)
#    return dataFrame.to_dict()
    

bucketColumns=(
    [{'id': 'category', 'name': 'Category'}] +
    #[{'id': 'January', 'name': 'January'}]
    [{'id': m, 'name': m, 'type':'numeric', 'format':money} for m in list(calendar.month_name)[1:13]]
)

bucketPage = [
    html.H2("Budget by Category and Month"),
    dash_table.DataTable(
        id='bucket-budget-edit-table',
        columns = bucketColumns,
        data = getBucketData(2022),
        editable=True),
    html.Button('Save', id='save-buckets', n_clicks=0),
    html.Button('Copy Buckets to Next Month', id='copy-buckets', n_clicks=0),
    html.H2("Expenses by Category and Month"),
    dash_table.DataTable(
        id='bucket-year-edit-table',
        columns=bucketColumns,
        #data = [{'category': 
        #data=[{'category': c, 'category': 'Spent:'} for c in getBudgetCategories(db)] +
        #    [{'January': amount} for amount in range(1,14)],
        #data = [{'category': 'Food', 'January': 397.99, 'February': 421}],
        data=getExpenseData(2022),
        #data = [{'category': 'Food', 'March': 300, 'June': 250},
        #    {'category': 'Tristan - WTF', 'May': 300, 'July': 250},],
        editable=False),
    html.Div(id='empty-output'),

    ]

#@app.callback(
#        Output('empty-output', 'children'),
#        Input('bucket-year-edit-table', 'data_timestamp'),
#        State('bucket-year-edit-table', 'data'))
#def updateYearBucketTable(timestamp, rows):
#    for row in rows:
#        try:
#            print("Changing row['January'] to {}".format(row['January']))
#            for element in row:
#                print('"{}"'.format(element))
#        except Exception as error:
#            print(error)
#    return ""

app.layout = html.Div([
    html.H1('Budget'),
    dcc.Tabs([
        dcc.Tab(label='View', children = bucketPage),
        dcc.Tab(label='Edit', children = expensePage)
    ])
])

# Old example code.
@app.callback(
    Output('table-editing-simple-output', 'figure'),
    Input('table-editing-simple', 'data'),
    Input('table-editing-simple', 'columns'))
def display_output(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return {
        'data': [{
            'type': 'parcoords',
            'dimensions': [{
                'label': col['name'],
                'values': df[col['id']]
            } for col in columns]
        }]
    }

# Callback to update budget buckets
@app.callback(
    Output('empty-output', 'children'),
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
            print(f"Setting {row['category']} for month {monthNumber} to {budgetedAmount}")
            setBucketBudget(year = 2022, category = row['category'],
                month = monthNumber, amountBudgeted = budgetedAmount)




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
    expenseString = f"Adding budget expense from {expenseYear}-{month}-{expenseDay}: {expenseCategory}: {expenseAmount} ({expenseDescription})"
    if expenseDay is not None and expenseAmount is not None and expenseDescription is not None and expenseCategory is not None:
        print(expenseString)
        addBudgetExpense(db, expenseYear, month,
                expenseDay, expenseCategory, expenseAmount, expenseDescription)
    return expenseString, "", None, None, ""



if __name__ == '__main__':
    app.run_server(debug=True)


