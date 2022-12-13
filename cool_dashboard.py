from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from pandas.core.common import SettingWithCopyWarning
import dash
import warnings
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import plotly.io as pio
pio.renderers.default = 'notebook'
pio.templates.default = "plotly_dark"

warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
data1 = pd.read_excel("globalterrorismdb_0221dist.xlsx")
data2 = pd.read_excel("gtd1993_0221dist.xlsx")
# data1 is the main archives while data2 is the missing 1993 records that were recovered later.
# These two files are loaded into dataframes and concatenated.
raw_data = pd.concat([data1, data2], axis=0, ignore_index=True)
raw_data = raw_data.sort_values('eventid')
# The rows are sorted into proper chronological order
raw_data = raw_data.rename(columns={'iyear': 'Year', 'imonth': 'Month', 'iday': 'Day',
                           'country': 'Country Code', 'country_txt': 'Country', 'region': 'Region Code'})
# fwgbstgby means fatalities/wounded grouped by specific terrorist groups by year
# It will be the one used by the plotly scatter map
fwgbstgby = raw_data[['Month', 'Day', 'Year', 'Country', 'latitude',
                      'longitude', 'gname', 'nkill', 'nkillter', 'nwound', 'nwoundte']]
fwgbstgby['Fatalities'] = fwgbstgby['nkill']-fwgbstgby['nkillter']
fwgbstgby['Wounded'] = fwgbstgby['nwound']-fwgbstgby['nwoundte']
fwgbstgby = fwgbstgby.drop(columns=["nkill", 'nkillter', 'nwound', 'nwoundte'])
fwgbstgby['Count'] = 1
# agbstgby means attacks grouped by specific terrorist groups by year
agbstgby = raw_data[['Year', 'gname']]
agbstgby = pd.DataFrame(agbstgby.groupby(["Year", "gname"])["gname"].count())
agbstgby = agbstgby.rename(columns={'gname': "Attacks"})
# agbcby means attacks grouped by country by year
agbcby = raw_data[['Year', 'Country']]
agbcby = pd.DataFrame(agbcby.groupby(['Year', 'Country'])['Country'].count())
agbcby = agbcby.rename(columns={'Country': "Attacks"})
# mode_of_attack is the backend dataframe for the pie chart
mode_of_attack = raw_data[['Year', 'gname', 'attacktype1_txt']]
mode_of_attack["Count"] = 1

app = dash.Dash(__name__)
server = app.server
colors = {'background': '#1f2630', 'text': '#77afdf'}
app.layout = html.Div(children=[
    html.H1(children="Global Terrorism Analysis", style={
            'textAlign': 'center', 'color': colors['text'], 'fontSize':50, 'marginTop':0}),
    html.H2('Scope', style={'textAlign': 'center',
            'color': colors['text'], 'fontSize':25, 'marginTop':20, }),
    dcc.RadioItems(
        id='options',
        options=[
            {'label': 'World', 'value': 'World'},
            {'label': 'Country', 'value': 'Country'}
        ],
        value='World', style={'color': colors['text'], 'textAlign':'center', 'marginBottom':30, 'fontSize':20}
    ),
    dcc.Markdown(
        '''Hover over points or countries for more info''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''The radio options allow to analyze a scatterplot world map or a choropleth world map.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''The scatterplot world map shows a scatterplot of attacks over the selected years.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''The choropleth world map represents a quantity by color. Thus, the countries are colored
           differently based on the number of attacks in a country.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''Thus, the countries are colored differently based on the number of attacks in a country.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''On top of this, there are two numbers displayed when the user hovers over a country.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''The top is the count of attacks and the bottom is the average attacks over the selected years.''',
        style={'color': colors['text'], 'textAlign':'center', 'fontSize':20}
    ),
    dcc.Markdown(
        '''There are longer loading times for a larger range of years as there is more data to compute''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginBottom':10}
    ),
    dcc.RangeSlider(
        id='year-rangeslider',
        min=1970,
        max=2019,
        step=1,
        marks={i: {'label': str(i), 'style': {
            'color': colors['text']}} for i in range(1970, 2020)},
        value=[1970, 1971],
        allowCross=False
    ),
    dcc.Graph(id='display-selected-graph', style={'verticalAlign': 'middle'}),
    dcc.Markdown(
        '''Below is a treemap that visualizes the hierarchical data of regions and countries''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginBottom':10, 'marginTop':10}
    ),
    dcc.Graph(id='display-treemap', style={'verticalAlign': 'middle'}),
    dcc.Markdown(
        '''Please click on a country on the choropleth map to see the number of attacks over years in the graph below''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginBottom':10, 'marginTop':10}
    ),
    dcc.Graph(id='line-graph', style={'verticalAlign': 'middle'}),
    dcc.Markdown(
        '''This next section allows for selecting multiple terrorist groups and generating attack and fatalities stats over the given years''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginBottom':10, 'marginTop':10}
    ),
    dcc.Dropdown(id='selected-groups',
                 options=[{'label': str(i), 'value': str(i)}
                          for i in raw_data.gname.unique()],
                 multi=True
                 ),
    dcc.Graph(id='kpi', style={'verticalAlign': 'middle'}),
    dcc.Markdown(
        '''This next section is disconnected from the year slider and outputs a pie chart on attack types based on a given group''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginTop':10}
    ),
    dcc.Markdown(
        '''It also outputs a scatter plot showing the number of attacks over the years of a given group''',
        style={'color': colors['text'], 'textAlign':'center',
               'fontSize':20, 'marginBottom':10, }
    ),
    dcc.Dropdown(id='singular-group',
                 options=[{'label': str(i), 'value': str(i)}
                          for i in raw_data.gname.unique()],
                 multi=False
                 ),
    dcc.Graph(id='pie-chart',
              style={'width': '35%', 'display': 'inline-block'}),
    dcc.Graph(id='scat', style={'width': '65%', 'display': 'inline-block'})
], style={'background-color': colors['background']})


@app.callback(
    Output('display-selected-graph', 'figure'),
    Input('options', 'value'),
    Input('year-rangeslider', 'value'))
def set_graph(option, year_range):
    if option == 'World':
        temp1 = fwgbstgby[(fwgbstgby["Year"] >= year_range[0])
                          & (fwgbstgby["Year"] <= year_range[1])]
        fig_world = go.Figure(data=go.Scattergeo(lat=temp1.latitude,
                                                 lon=temp1.longitude,
                                                 hovertemplate='Date: '+temp1['Month'].astype(str)+'/'+temp1['Day'].astype(str)+'/' +
                                                 temp1['Year'].astype(str)+'<br>'+temp1['gname']+'<br>'+'Fatalities: ' +
                                                 temp1['Fatalities'].astype(
                                                     str)+'<br>'+'Wounded: '+temp1['Wounded'].astype(str)+"<extra></extra>",
                                                 marker=dict(size=2)))
        fig_world.update_geos(showcountries=True)
        fig_world.update_layout(width=1900, height=950, margin={
                                'r': 0, "t": 0, "l": 0, "b": 0})
        return fig_world
    else:
        agbcbyt = agbcby.loc[year_range[0]:year_range[1]]
        agbcbyt = agbcbyt.groupby("Country")['Attacks'].sum()
        agbcbyt["avg"] = agbcbyt.values/(year_range[1]-year_range[0])

        fig_country = go.Figure(data=go.Choropleth(
            locationmode='country names',
            locations=agbcbyt.index,
            z=agbcbyt.values,
            text=agbcbyt['avg']
        ))
        fig_country.update_layout(geo=dict(showcountries=True), width=1900, height=950, margin={
                                  'r': 0, "t": 0, "l": 0, "b": 0})
        return fig_country


@app.callback(
    Output('display-treemap', 'figure'),
    Input('year-rangeslider', 'value'))
def display_treemap(year_range):
    df_treemap = raw_data[['Year', 'region_txt', 'Country']]
    df_treemap = df_treemap[(df_treemap['Year'] >= year_range[0]) & (
        df_treemap['Year'] <= year_range[1])]
    df_treemap['Count'] = 1
    treemap = px.treemap(
        df_treemap, path=['region_txt', 'Country'], values='Count', height=700)
    return treemap


@app.callback(
    Output('line-graph', 'figure'),
    Input('year-rangeslider', 'value'),
    Input('display-selected-graph', 'clickData'))
def stats(year_range, clickData):
    temp_num_attacks = []
    temp_years = []
    if clickData is None:
        return px.line(x=None, y=None)
    else:
        country = clickData['points'][0]['location']
        if country is None:
            return px.line(x=None, y=None)
    for i in range(year_range[0], year_range[1]+1, 1):
        temp_years.append(i)
        try:
            temp_num_attacks.append(agbcby.loc[i, country]["Attacks"])
        except KeyError:
            temp_num_attacks.append(0)
    fig_line = px.line(x=temp_years, y=temp_num_attacks, title=country)
    fig_line.update_layout(xaxis=dict(dtick=1))
    return fig_line


@app.callback(
    Output('kpi', 'figure'),
    Input('year-rangeslider', 'value'),
    Input('selected-groups', 'value'))
def indicator_stats(year_range, group_list):
    temp_attack_indicator, temp_fatal_indicator, temp_wound_indicator = 0, 0, 0
    if type(group_list) == 'str':
        temp_fatal_indicator = temp_fatal_indicator+fwgbstgby[(fwgbstgby['gname'] == group_list) & (
            fwgbstgby['Year'] >= year_range[0]) & (fwgbstgby['Year'] <= year_range[1])]['Fatalities'].sum()
        temp_wound_indicator = temp_wound_indicator+fwgbstgby[(fwgbstgby['gname'] == group_list) & (
            fwgbstgby['Year'] >= year_range[0]) & (fwgbstgby['Year'] <= year_range[1])]['Wounded'].sum()
        for j in range(year_range[0], year_range[1]+1, 1):
            try:
                temp_attack_indicator = temp_attack_indicator + \
                    (agbstgby.loc[j, group_list]["Attacks"])
            except KeyError:
                temp_attack_indicator = temp_attack_indicator
    if type(group_list) == list:
        for i in group_list:
            temp_fatal_indicator = temp_fatal_indicator+fwgbstgby[(fwgbstgby['gname'] == i) & (
                fwgbstgby['Year'] >= year_range[0]) & (fwgbstgby['Year'] <= year_range[1])]['Fatalities'].sum()
            temp_wound_indicator = temp_wound_indicator+fwgbstgby[(fwgbstgby['gname'] == i) & (
                fwgbstgby['Year'] >= year_range[0]) & (fwgbstgby['Year'] <= year_range[1])]['Wounded'].sum()
            for j in range(year_range[0], year_range[1]+1, 1):
                try:
                    temp_attack_indicator = temp_attack_indicator + \
                        (agbstgby.loc[j, i]["Attacks"])
                except KeyError:
                    temp_attack_indicator = temp_attack_indicator
    else:
        temp_attack_indicator, temp_fatal_indicator, temp_wound_indicator = 0, 0, 0

    stats = go.Figure()
    stats.add_trace(go.Indicator(
        mode='number',
        value=temp_attack_indicator,
        domain={'x': [0, 0.3], 'y': [0, 1]},
        title="Total # of Attacks"
    ))
    stats.add_trace(go.Indicator(
        mode='number',
        value=temp_fatal_indicator,
        domain={'x': [0.35, 0.65], 'y': [0, 1]},
        title="Total # of Fatalities"
    ))
    stats.add_trace(go.Indicator(
        mode='number',
        value=temp_wound_indicator,
        domain={'x': [0.7, 1], 'y': [0, 1]},
        title="Total # of Wounded"
    ))
    return stats


@app.callback(
    Output('scat', 'figure'),
    Output('pie-chart', 'figure'),
    Input('singular-group', 'value'))
def pie_chart(one_group):
    temp_mode_of_attack = mode_of_attack[mode_of_attack['gname'] == one_group]
    if len(temp_mode_of_attack) == 0:
        pie = px.pie(title="Please Select a Group")
        scat = px.line(x=None, y=None)
        return scat, pie
    else:
        active_years = fwgbstgby[fwgbstgby['gname'] ==
                                 one_group].groupby("Year").count().index
        attacks_carried_out = fwgbstgby[fwgbstgby['gname'] == one_group].groupby("Year")[
            'Count'].count().values
        pie = px.pie(temp_mode_of_attack, values='Count',
                     names='attacktype1_txt')
        scat = px.scatter(x=active_years, y=attacks_carried_out)
        return scat, pie


if __name__ == '__main__':
    app.run_server(debug=False)
