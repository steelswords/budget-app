#!/usr/bin/python3
# Code from https://dash.plotly.com/datatable/editable
from dash import Dash, dash_table, dcc, html, State
from dash.dependencies import Input, Output
import pandas as pd
from budget import *

app = Dash(__name__)
app.Title = "Budget App"

db = connect()
#ensureDatabaseSchema(db)
print(getBudgetCategories(db))

params = [
    'Weight', 'Torque', 'Width', 'Height',
    'Efficiency', 'Power', 'Displacement'
]

expensePage = [
    html.H1("Expenses"),
    dcc.Dropdown(["2022"], "2022", id='expense-year'),
    dcc.Dropdown(["January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"], "January", id="expense-month"),
    dcc.Input(id="expense-day", type="number", placeholder="Day"),
    dcc.Dropdown([i[0] for i in getBudgetCategories(db)], "Food", id="expense-category-dropdown"),
    "Amount: ",
    dcc.Input(id="expense-amount", type="number", placeholder="Amount"),
    "Description: ",
    dcc.Input(id="expense-description", type="text",placeholder="Description"),
    html.Button('Add', id='add-expense', n_clicks=0),
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
    State('expense-year', 'expenseYear'),
    State('expense-month', 'expenseMonth'),
    State('expense-day', 'expenseDay'),
    State('expense-category-dropdown', 'expenseCategory'),
    Input('expense-amount', 'expenseAmount'),
    State('expense-description', 'expenseDescription'),
    State('add-expense', 'n_clicks'))
def add_expense_callback(expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount, expenseDescription):
    print("Adding budget expense from {year}-{month}-{day}: {category}: {amount}".format(expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount))
    addBudgetExpense(expenseYear, expenseMonth, expenseDay, expenseCategory, expenseAmount, expenseDescription)


if __name__ == '__main__':
    app.run_server(debug=True)

