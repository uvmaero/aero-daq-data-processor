import dash
import dash_core_components as dcc
import dash_html_components as html
import sys
import zipfile
import os
import json
import numpy as np
from datetime import datetime
import argparse

TEMP_DIR = './tmp'

def series_populator(d, base_key, series):
    for k, v in d.items():
        keyname = f'{base_key}.{k}'
        if base_key == "":
            keyname = k
        if isinstance(v, dict):
            # recursively run the populator on this sub-dict
            series_populator(v, keyname, series)
        elif isinstance(v, list):
            # convert list into dict
            d_conv = {}
            for i,val in enumerate(v):
                d_conv[f'{i}'] = val

            # also add min, max, and average options
            d_conv['min'] = np.min(v)
            d_conv['max'] = np.max(v)
            d_conv['avg'] = np.average(v)

            # recursively run the populator on this new dict
            series_populator(d_conv, keyname, series)
        elif keyname in series:
            # if this item is just a single value, append it if it's being selected
            series[keyname].append(v)

        # special case: if this is the `ts` series, also generate a `time` series
        if keyname == 'ts' and 'time' in series:
            series['time'].append(datetime.fromtimestamp(v / 1000)) # timestamps are in ms, so convert to s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Program a device over CAN')
    parser.add_argument('LogFile', default=None, type=str, help='Output from datalogger, zip')
    parser.add_argument('PlotDefFile', default=None, type=str, help='Plot definition file, json')
    args = parser.parse_args()

    # Extract data to a temporary location
    fname = args.LogFile
    fbasename = os.path.basename(fname).split('.')[0]
    extract_dir = f'{TEMP_DIR}/{fbasename}'
    log_file = zipfile.ZipFile(fname, 'r')
    log_file.extractall(extract_dir)

    # Plot descriptor file
    with open(args.PlotDefFile, 'r') as plot_descriptor:
        plots = json.load(plot_descriptor)

    # Load information from manifest file
    with open(f'{extract_dir}/manifest.json') as manifest_file:
        manifest = json.load(manifest_file)

    data_series = {}

    # determine which data series need to be loaded
    for item in plots:
        xseries = plots[item]['x']
        yseries = plots[item]['y']

        if not xseries in data_series.keys():
            data_series[xseries] = []

        if isinstance(yseries, list):
            for i in yseries:
                if not i in data_series.keys():
                    data_series[i] = []
        elif not yseries in data_series.keys():
            data_series[yseries] = []

    # load data series
    for file_num in range(manifest['data_files']):
        with open(f'{extract_dir}/{file_num}.dat', 'r') as dat:
            for line in dat:
                line_json = json.loads(line, encoding="utf8")
                series_populator(line_json, "", data_series)

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(id='centerContainer', children=[
        html.H1('AERO Data Logger'),

        html.H2('Session Info'),
        html.P(f'Date: {manifest["date"]}'),
        html.P(f'Start time: {manifest["start_time"]}'),
        html.P(f'End time: {manifest["end_time"]}')
    ])

    for title, desc in plots.items():
        graphdata = []

        if isinstance(desc["y"], list):
            for s in desc["y"]:
                graphdata.append(
                    {'x': data_series[desc["x"]], 'y': data_series[s], 'type': 'line', 'name': s}
                ) 
        else:
            graphdata.append(
                {'x': data_series[desc["x"]], 'y': data_series[desc["y"]], 'type': 'scatter', 'name': desc["y"]}
            )

        graph = dcc.Graph(
            id=title,
            figure={
                'data': graphdata,
                'layout': {
                    'title': title,
                    'xaxis': {
                        'title': desc["xlabel"]
                    },
                    'yaxis': {
                        'title:': desc["ylabel"]
                    }
                }
            }
        )

        app.layout.children.append(graph)

    app.run_server(debug=True)