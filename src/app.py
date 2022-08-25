from dash import Dash, dash_table, html, dcc 
from dash.dependencies import Input, Output
import pandas as pd
import json


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
    df = df.assign(
        DepartmentStartDate = df.DepartmentStartDate.apply (lambda x: clean_time(x)),
        StartDate = df.StartDate.apply (lambda x: clean_time(x)),
        EndDate = df.EndDate.apply (lambda x: clean_time(x)),
        ContractTypeStartDate = df.ContractTypeStartDate.apply (lambda x: clean_time(x)),
        ContractHourStartDate = df.ContractHourStartDate.apply (lambda x: clean_time(x))
    )
    if 'PositionStartDate' in df.columns: 
        df = df.assign(
        PositionStartDate = df.PositionStartDate.apply (lambda x: clean_time(x))
    )
    df = df.T.reset_index().rename(columns = {0: 'Information', 'index':'Key'})
    return df

app = Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Display your jsons nicely'),

    dcc.Textarea(
        id='textarea-example',
        value='Textarea content initialized\nwith multiple lines of text',
        style={'width': '100%', 'height': 300},
    ),
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'}),

    dash_table.DataTable(id='data_table',data= [],columns= [])
])

# @app.callback(
#     Output('textarea-example-output', 'children'),
#     Input('textarea-example', 'value')
# )
# def update_output(value):
#     return 'You have entered: \n{}'.format(value)

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

@app.callback(
    [Output("data_table", "data"), Output('data_table', 'columns')],
    Input('textarea-example', 'value')
)
def update_output(value):
    try: 
        json_object = json.loads(value)
        df = make_table_from_json(json_object)
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
    except:
        json_object = "none"
        return [], []

if __name__ == '__main__':
    app.run_server(debug=True)

