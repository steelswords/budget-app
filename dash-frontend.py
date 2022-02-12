#!/usr/bin/python3
# Code from https://dash.plotly.com/datatable/editable
from dash import Dash, dash_table, dcc, html, State
from dash.dependencies import Input, Output
import calendar
import pandas as pd
from budget import *

app = Dash(__name__)
app.Title = "Budget App"

db = connect()
ensureDatabaseSchema(db)
print(getBudgetCategories(db))

params = [
    'Weight', 'Torque', 'Width', 'Height',
    'Efficiency', 'Power', 'Displacement'
]

expensePage = [
    html.H1("Expenses"),
    dcc.Dropdown(["2022"], "2022", id='expense-year'),
    dcc.Dropdown(list(calendar.month_name), "January", id="expense-month"),
    html.Div(dcc.Input(id="expense-day", type="number", placeholder="Day")),
    dcc.Dropdown([i[0] for i in getBudgetCategories(db)], "Food", id="expense-category-dropdown"),
    "Amount: ",
    dcc.Input(id="expense-amount", type="number", placeholder="Amount"),
    "Description: ",
    dcc.Input(id="expense-description", type="text",placeholder="Description"),
    html.Button('Add', id='add-expense', n_clicks=0),
    html.Div(id='expense-output')
]


app.layout = html.Div([
    html.H1('Budget'),
    dcc.Tabs([
        dcc.Tab(label='View', children = [
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
            )]),
        dcc.Tab(label='Edit', children = expensePage)
    ])
])


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
    expenseString = "Adding budget expense from {}-{}-{}: {}: {} ({})".format(
            expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount, expenseDescription)
    if expenseDay is not None and expenseAmount is not None and expenseDescription is not None and expenseCategory is not None:
        print(expenseString)
        #addBudgetExpense(expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount, expenseDescription)
    return expenseString, "", None, None, ""



if __name__ == '__main__':
    app.run_server(debug=True)


