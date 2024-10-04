
from dash import Dash, dcc, html, Input, Output, callback
import random

import pandas as pd
import requests
from lxml import html as p_html
import time



def fetch(location):
    page = requests.get("https://results.eci.gov.in/PcResultGenJune2024/%s.htm" % location,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "DNT": "1",
            "Priority": "u=1",
            "Referer": "https://results.eci.gov.in/PcResultGenJune2024/%s.htm" % location,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "TE": "trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0"
        },
        cookies={},
        auth=(),
    ).text

    tree = p_html.fromstring(page)
    table = tree.xpath('/html/body/main/div/div[3]/div/table/tbody')[0]

    headers = ['Constituency',
    'Const. No.',
    'Leading Candidate',
    'Leading Party',
    'Trailing Candidate',
    'Trailing Party',
    'Margin',
    "Status"]

    stack = []
    for row in table.findall(".//tr"):
        txt = [r.text for r in row.findall(".//td")]
        if len(txt) == 30:

            final_row = txt[:3] + txt[4:5] + txt[15:16] + txt[17:18] + txt[-2:]
            stack.append(final_row)
            
    df = pd.DataFrame(data = stack, columns = headers)
    return df, page


def clean(df):
    df["Constituency"] = df["Constituency"] + df["Status"].apply(lambda x: " (P)" if "in progress" in x.lower() else " (D)")
    df["Margin"] = df["Margin"].replace("-", "0").astype("int")
    #df = df.replace({"Bharatiya Janata Party":"BJP", "Indian National Congress":"INC"})
    df["Leading Party"] = df["Leading Party"].apply(lambda x: "".join(r[0] for r in x.split(" ")))
    leads = df["Leading Party"].value_counts()
    #for r in leads.index: df["Leading Party"] = df["Leading Party"].replace(r, "%s(%d)" % (r , leads[r]))
    df["Label"] = df["Margin"].astype(str) + "\n" + df["Leading Candidate"]

    df.at[random.randint(0,9), "Margin"] = random.randint(1000,1200)
    df.at[random.randint(0,9), "Margin"] = random.randint(1000,300000)
    df = df.sort_values(by = "Margin", ascending=False)
    df["Const. No."] = "X" + df["Const. No."].astype("str")

    return df

def update_data():
    global election_data
    location = 'statewiseS071'
    df, r = fetch(location)
    election_data = clean(df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Div([html.H4(id = "timer"),
            dcc.Graph(id='live-update-graph')
        ], className="six columns"),

        html.Div([html.H4(id = "counter"),
            dcc.Graph(id='live-update-graph2')
        ], className="six columns"),
       
    ], className="row")
    ,dcc.Interval(
                id='interval-component',
                interval=50*1000, # in milliseconds
                n_intervals=0)
])

def counter_fn(df):
    leads = df["Leading Party"].value_counts().to_dict()
    style = {'padding': '5px', 'fontSize': '32px'}
    return [html.Span('%s: %d' %(l, leads[l]), style=style) for l in leads]

def fetch_data(df):
    stack = []
    for party in df["Leading Party"].unique():
        temp = df[df["Leading Party"] ==  party]
        item = {"y":temp["Const. No."].to_list(), "x":temp["Margin"].to_list()
                ,'text':temp["Margin"].astype("str") + " <> "+
                  temp["Constituency"].astype("str").to_list() + " <> " + temp["Leading Candidate"].astype("str").to_list(), 
                 'type': 'bar', 'name': party, "orientation":'h'
                 , "config":{'displayModeBar':False}}
        stack.append(item)

    data = {
        'data': stack,
        'layout': {
                    #'title': 'Dash Data Visualization'
                    "transition":{'duration': 1500}
                    ,"height":1500
                    ,"width":850
                },
        
           
    }
    return data

def temp_fn(df):
    stack = pd.DataFrame()
    for r in range(9):
        temp = df.copy()
        temp["Const. No."] = temp["Const. No."] + "-" + str(r)
        stack = pd.concat([stack, temp.copy()])

    stack = stack.sort_values(by = "Margin", ascending=False)
    return stack

# Multiple components can update everytime interval gets fired.
@callback(Output('live-update-graph', 'figure'), Output('live-update-graph', 'config'), Output('live-update-graph2', 'figure'), Output('live-update-graph2', 'config')
          , Output('timer', 'children'), Output('counter', 'children'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    update_data()
    global election_data

    df = election_data.copy()
    df = temp_fn(df.copy())
    data1 = fetch_data(df.iloc[:45].copy())
    data2 = fetch_data(df.iloc[45:].copy())
    config = {'staticPlot': True}
    return data2, config, data1, config, '%s'%time.strftime("%H:%M:%S"), counter_fn(df)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")