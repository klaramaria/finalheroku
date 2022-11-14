from dash import Dash, dash_table, html, dcc 
from dash.dependencies import Input, Output, State
import pandas as pd
import json
from employee_keys import extra_column, string_example
from setting_keys import extra_column_s


#------------------ function to convert unix time to readable time ----------------------
def clean_time(time):
    if(time):
        try: 
            if len(time) == 26: #time with timezone localization
                ntime = time[6:-7]
                ntime = int(ntime) + (3.6e+6)*2 # convert to MET
                ntime = pd.to_datetime(ntime, unit = 'ms').strftime("%d/%m/%y %H:%M")
            if len(time) == 21: #without timezone localization
                print(2)
                ntime = time[6:-2]
                ntime = pd.to_datetime(ntime, unit = 'ms').strftime("%d/%m/%y %H:%M")
            if len(time) == 20:
                print(3)
                ntime = time[6:-2]
                ntime = pd.to_datetime(ntime, unit = 'ms').strftime("%d/%m/%y %H:%M")
        except: 
            ntime = 'Time could not be deciphered. Double check the formatting. Otherwise contact Klara about this'
            
    else: 
        ntime = time
    return ntime

#------------------ function that transforms json object into pandas dataframe ----------
def make_table_from_json(json_object, key):
    # df = pd.json_normalize(json_object)
    # key_list = list(json_object.keys())
    #key_list.remove('Name')
    if key == 'Employees':
        df = pd.DataFrame(json_object[key]).fillna('')
        
    else: 
        df = pd.DataFrame(json_object, index = [0]).fillna('')
    time_column_names = ['DepartmentStartDate', 'StartDate', 'EndDate', 'ContractTypeStartDate', 'ContractHourStartDate', 'PositionStartDate']
    for column_name in time_column_names:
        if column_name in df.columns: 
            df = df.assign(
                **{column_name: df[column_name].apply(lambda x: clean_time(x))}
            )
    df = df.T.reset_index().rename(columns = {0: 'Value', 'index':'Key'})
    df['Explanation / Alternate Name'] = df.Key.map(extra_column).fillna('-')
    df = df.astype(str)
    return df

#----------------- functions that transforms settings part of json object into pandas dataframe ----------
def display_settings(json_object):
    df = pd.DataFrame(json_object['ImportSettings'], index = [0]).T.reset_index().rename(columns = {0: 'Value', 'index':'Key'})
    df['Explanation / Alternate Name'] = df.Key.map(extra_column_s).fillna('-')
    return df

app = Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Make your files more readable'),
    dcc.Textarea(
        id='textarea-example',
        value=string_example,
        style={'width': '100%','height':'390px', 'font-size':13},
    ),
    ## div in which we get told if object is correct or not correct
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line', 'marginBottom': 25, 'marginTop': 25}),

    html.Button('Submit', id = 'submit-val'),

    html.H3(id='Employees_header', children = ''),

    dash_table.DataTable(id='data_table',data= [],columns= [] ,style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'minWidth': '250px'}, style_data_conditional=[
            {
                'if': {
                    'state': 'selected'  # 'active' | 'selected'
                },
                'backgroundColor': '#fc9f95',
                "border": "1px #ff8273",
            },
        ],),

    html.H3(id='Settings_header' ,children=''),

    dash_table.DataTable(id='settings_table',data= [],columns= [], style_cell={'textAlign': 'left', 'whiteSpace': 'pre-line'}, style_data_conditional=[{
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
    Output('textarea-example', 'value'),
    State('textarea-example', 'value'),
    Input('submit-val','n_clicks')
)
def update_info(txtvalue, n_clicks):
    if n_clicks != 0: 
        try: 
            json_object = json.loads(txtvalue)
            return 'This is a correct JSON object \n', txtvalue
        except:
            json_object = "none"
            return 'This is not a json object', string_example



# ------ update data_table on callback ----------------
@app.callback(
    [Output("data_table", "data"), Output('data_table', 'columns'),
    Output("settings_table", "data"), Output('settings_table', 'columns')],
    State('textarea-example', 'value'),
    Input('submit-val','n_clicks')
)
def update_output(value, n_clicks):
    if n_clicks != 0:
        try:
            json_object = json.loads(value)
            if 'Employees' in list(json_object.keys()): 
                df1 = make_table_from_json(json_object, 'Employees')
                df2 = display_settings(json_object)
                df2 = df2.astype(str)
                print(df1)
                print(df2)
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

