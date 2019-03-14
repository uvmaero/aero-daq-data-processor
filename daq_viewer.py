import dash
import dash_core_components as dcc
import dash_html_components as html
import sys
import zipfile
import os
import json

TEMP_DIR = './tmp'

# Check args
if len(sys.argv) != 2:
    print('Usage: daq_viewer.py [logger file (zip)]\nEx: daq_viewer log.zip')
    exit()

if sys.argv[1] == '--help':
    print('Usage: daq_viewer.py [logger file (zip)]\nEx: daq_viewer log.zip')
    exit()

# Extract data to a temporary location
fname = sys.argv[1]
fbasename = os.path.basename(fname).split('.')[0]
extract_dir = f'{TEMP_DIR}/{fbasename}'
print(fbasename)
log_file = zipfile.ZipFile(fname, 'r')
log_file.extractall(extract_dir)

# Load information from manifest file
with open(f'{extract_dir}/manifest.json') as manifest_file:
    manifest = json.load(manifest_file)

print(manifest)

exit()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1('AERO Data Logger'),

    html.H2('Session Info'),
    html.P(f'Date: {session["date"]}'),
    html.P(f'Start time: {session["start_time"]}'),
    html.P(f'End time: {session["end_time"]}'),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [10, 1, 2], 'type': 'bar', 'name': 'Rinehart temp'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)