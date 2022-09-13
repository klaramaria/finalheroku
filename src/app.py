from dash import Dash, dash_table, html, dcc 
from dash.dependencies import Input, Output
import pandas as pd
import json
from employee_keys import extra_column, string_example
from setting_keys import extra_column_s


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
def make_table_from_json(json_object, key):
    # df = pd.json_normalize(json_object)
    # key_list = list(json_object.keys())
    #key_list.remove('Name')
    if key == 'Employees':
        df = pd.DataFrame(json_object[key])
    else: 
        df = pd.DataFrame(json_object, index = [0])
    time_column_names = ['DepartmentStartDate', 'StartDate', 'EndDate', 'ContractTypeStartDate', 'ContractHourStartDate', 'PositionStartDate']
    for column_name in time_column_names:
        if column_name in df.columns: 
            df = df.assign(
                **{column_name: df[column_name].apply(lambda x: clean_time(x))}
            )
    df = df.T.reset_index().rename(columns = {0: 'Value', 'index':'Key'})
    df['Explanation / Alternate Name'] = df.Key.map(extra_column).fillna('-')
    return df

#----------------- functions that transforms settings part of json object into pandas dataframe ----------
def display_settings(json_object):
    df = pd.DataFrame(json_object['ImportSettings'], index = [0]).T.reset_index().rename(columns = {0: 'Value', 'index':'Key'})
    df['Explanation / Alternate Name'] = df.Key.map(extra_column_s).fillna('-')
    return df

app = Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Make your JSON files more readable'),

    dcc.Textarea(
        id='textarea-example',
        value=string_example,
        style={'width': '100%','height':'390px', 'font-size':13},
    ),
    ## div in which we get told if object is correct or not correct
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line', 'marginBottom': 25, 'marginTop': 25}),

    html.H3(id='Employees_header', children = ''),

    dash_table.DataTable(id='data_table',data= [],columns= [] ,style_cell={'textAlign': 'left'}, style_data_conditional=[
            {
                'if': {
                    'state': 'selected'  # 'active' | 'selected'
                },
                'backgroundColor': '#fc9f95',
                "border": "1px #ff8273",
            },
        ],),

    html.H3(id='Settings_header' ,children=''),

    dash_table.DataTable(id='settings_table',data= [],columns= [], style_cell={'textAlign': 'left'}, style_data_conditional=[{
                'if': {
                    'state': 'selected'  # 'active' | 'selected'
                },
                'backgroundColor': '#fc9f95',
                "border": "1px #ff8273",
            },
        ],)
])

# -------------- error when no json object -----------------------------
@app.callback(
    Output('textarea-example-output', 'children'),
    Input('textarea-example', 'value')
)
def update_output(value):
    try: 
        json_object = json.loads(value)
        return 'This is a correct JSON object \n'
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
        if 'Employees' in list(json_object.keys()): 
            df1 = make_table_from_json(json_object, 'Employees')
            df1 = df1.astype(str)
            print(df1)
            df2 = display_settings(json_object)
            df2 = df2.astype(str)
            return df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns], df2.to_dict('records'), [{"name": i, "id": i} for i in df2.columns]
        else:
            try:
                df = make_table_from_json(json_object, 'na')
                print(df)
                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], [] , []
            except:
                return [], [] , [] , []
    except: 
        return [], [] , [] ,[]

# ----- update settings_header and Employees_header on callback------------------------- 
@app.callback(
     Output("Settings_header", "children"),
     Input('settings_table', 'data')
 )
def update_settings_output(data):
    if data != []:
        return 'Settings of this object'
    else:
        return ''

@app.callback(
     Output("Employees_header", "children"),
     Input('data_table', 'data')
 )
def update_settings_output(data):
    if data != []:
        return 'Properties of this object'
    else:
        return ''



# ----- run main -------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

