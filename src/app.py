from dash import Dash, dash_table, html, dcc 
from dash.dependencies import Input, Output
import pandas as pd
import json
from employee_keys import extra_column


#------------------ function to convert unix time to readable time ----------------------
def clean_time(time):
    if(time):
        if len(time) == 26: #time with timezone localization
            ntime = time[6:-7]
            ntime = int(ntime) + (3.6e+6)*2 # convert to MET
            ntime = pd.to_datetime(ntime, unit = 'ms').strftime("%d/%m/%y %H:%M")
        if len(time) == 21: #without timezone localization
            ntime = time[6:-2]
            ntime = pd.to_datetime(ntime, unit = 'ms').strftime("%d/%m/%y %H:%M")
    else: 
        ntime = time
    return ntime

#------------------ function that transforms json object into pandas dataframe ----------
def make_table_from_json(json_object):
    # df = pd.json_normalize(json_object)
    df = pd.DataFrame(json_object['Employees'])
    time_column_names = ['DepartmentStartDate', 'StartDate', 'EndDate', 'ContractTypeStartDate', 'ContractHourStartDate', 'PositionStartDate']
    for column_name in time_column_names:
        if column_name in df.columns: 
            df = df.assign(
                **{column_name: df[column_name].apply(lambda x: clean_time(x))}
            )
    df = df.T.reset_index().rename(columns = {0: 'Information', 'index':'Key'})
    df['Explanation / Different Name'] = df.Key.map(extra_column).fillna('-')
    return df

#----------------- functions that transforms settings part of json object into pandas dataframe ----------
def display_settings(json_object):
    df = pd.DataFrame(json_object['ImportSettings'], index = [0]).T.reset_index().rename(columns = {0: 'Information', 'index':'Key'})
    return df

app = Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Display your jsons nicely'),

    dcc.Textarea(
        id='textarea-example',
        value='Paste the JSON object that you received in here\nLine Breaks can or cannot be put in',
        style={'width': '100%', 'height': 300},
    ),
    ## div in which we get told if object is correct or not correct
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line', 'marginBottom': 25, 'marginTop': 25}),

    dash_table.DataTable(id='data_table',data= [],columns= []),

    html.H3(children='Settings of this object'),

    dash_table.DataTable(id='settings_table',data= [],columns= [])
])

# -------------- error when no json object -----------------------------
@app.callback(
    Output('textarea-example-output', 'children'),
    Input('textarea-example', 'value')
)
def update_output(value):
    try: 
        json_object = json.loads(value)
        return 'You entered a correct json object \n'
    except:
        json_object = "none"
        return 'This is not a json object'


# ------ update data_table on callback ----------------
@app.callback(
    [Output("data_table", "data"), Output('data_table', 'columns'),
    Output("settings_table", "data"), Output('settings_table', 'columns')],
    Input('textarea-example', 'value')
)
def update_output(value):
    try: 
        json_object = json.loads(value)
        df1 = make_table_from_json(json_object)
        df2 = display_settings(json_object)
        print(df2)
        return df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns], df2.to_dict('records'), [{"name": i, "id": i} for i in df2.columns]
    except:
        json_object = "none"
        return [], [], [] , []


# ----- update settings_table on callback------------------------- 
# @app.callback(
#     [Output("settings_table", "data"), Output('settings_table', 'columns')],
#     Input('textarea-example', 'value')
# )
# def update_settings_output(value):
#     try: 
#         json_object = json.loads(value)
#         df2 = display_settings(json_object)
#         print(df2)
#         return df2.to_dict('records'), [{"name": i, "id": i} for i in df2.columns]
#     except:
#         json_object = "none"
#         return [], []


# ----- run main -------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

