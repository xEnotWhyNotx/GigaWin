from dash import Dash, dcc, html, Input, Output, callback, no_update, register_page, State
import dash_daq as daq
import dash
import pandas as pd
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import json
from dash_extensions.javascript import assign

import math


register_page(__name__)

# Загружаем данные
df_for_tern_off = pd.read_pickle('service/df_for_tern_off.pkl')
df_ = pd.read_csv('service/heatloss_data.csv')

def find_all_geo():
    df_TP = df_for_tern_off[['Адрес ТП', 'latitude_x', 'longitude_x']].drop_duplicates()
    df_houses = df_for_tern_off[['Адрес', 'UNOM', 'longitude_y', 'latitude_y']].drop_duplicates()
    return df_TP, df_houses

df_TP_all, df_houses_all = find_all_geo()
df1 = df_TP_all
df_houses = df_houses_all


# получаем данные о домах и их скорости остывания
all_data = df_for_tern_off.merge(df_, left_on='UNOM', right_on='unom', how='left')
all_data = all_data.dropna()

# функция нахождения отклющившихся домов по адресу ЦТП 
def find_ternd_off(adress_list):
    TP_list = []
    houses_list = []
    for adress in adress_list:
        if adress in df_for_tern_off['Адрес ТП'].values:
            TP_list.append(adress)
        else:
            houses_list.append(adress)
    for adress_TP in TP_list:
        for address in df_for_tern_off[df_for_tern_off['Адрес ТП'] == adress_TP]['Адрес'].unique():
            if address not in houses_list:
                houses_list.append(address)
    UNOMS = df_for_tern_off[df_for_tern_off['Адрес'].isin(houses_list)]['UNOM'].unique()
    df_TP = df_for_tern_off[df_for_tern_off['Адрес ТП'].isin(TP_list)][['Адрес ТП', 'latitude_x', 'longitude_x']].drop_duplicates()
    df_houses = df_for_tern_off[df_for_tern_off['Адрес'].isin(houses_list)][['Адрес', 'UNOM', 'longitude_y', 'latitude_y']].drop_duplicates()
    return UNOMS, df_TP, df_houses


#   время остывания дома в часах
def collDown(betta,tn):
    return round(betta*math.log((22 - tn)/(8 - tn)), 2)

# теплоповжарпыдвагшпыароми фактическое Гкал/ч
def heat_col(row, tn):
    row['heatloss'] = round(tn*row['factor']+row['intercept'], 3)
    return row


# Создаем структуру GeoJSON для ЦПТ 
def get_features_TP(df):
    return [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row['longitude_x'], row['latitude_x']]},
            "properties": {"Address": row['Адрес ТП'], "id": index}
        }
        for index, row in df.iterrows()
    ]
features = get_features_TP(df1)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

on_each_feature = assign("""
    function(feature, layer, context){
        layer.bindTooltip(
            '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>id:</b> ' + feature.properties['id'] +
            '</div>',
            {permanent: false, direction: 'top'}
        );
    }
""")

# Создаем структуру GeoJSON для домов 

def get_featurers_houses(df_houses):
    return [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row['longitude_y'], row['latitude_y']]},
            "properties": {"Address": row['Адрес'], "id": index, "UNOM": row['UNOM']}
        }
        for index, row in df_houses.iterrows()
    ]
features_houses = get_featurers_houses(df_houses)

geojson_houses = {
    "type": "FeatureCollection",
    "features": features_houses
}


point_to_layer_houses = assign("""
    function(feature, latlng, context){
        var preds = feature.properties.preds;
        var radius = 5 + (12 * preds); // Base radius 5, max radius 15
        return L.circleMarker(latlng, {
            radius: radius,
            color: 'green',
            weight: 1,
            opacity: 1,
            fillOpacity: 1,
            fillColor: 'green'
        });
    }
""")

on_each_feature_houses = assign("""
    function(feature, layer, context){
        layer.bindTooltip(
            '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>id:</b> ' + feature.properties['id'] + '<br>' +
                '<b>UNOM:</b> ' + feature.properties['UNOM'] + '<br>' +
                '<b>CTP number:</b> ' + feature.properties['ctp_number'] + '<br>' +
                '<b>Heatstation:</b> ' + feature.properties['heatstation'] + '<br>' +
                '<b>Heat consumption:</b> ' + feature.properties['heatloss'] +
            '</div>',
            {permanent: false, direction: 'top'}
        );
    }
""")

# Это для отключенных домов
on_each_feature_houses_turnedoff = assign("""
    function(feature, layer, context){
        layer.bindTooltip(
            '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>UNOM:</b> ' + feature.properties['UNOM'] + '<br>' +
                '<b>CTP number:</b> ' + feature.properties['ctp_number'] + '<br>' +
                '<b>Heatstation:</b> ' + feature.properties['heatstation'] + '<br>' +
                '<b>Time left:</b> ' + feature.properties['time_in_hours'] + '<br>' +
                '<b>Heat consumption:</b> ' + feature.properties['heatloss'] +
            '</div>',
            {permanent: false, direction: 'top'}
        );
    }
""")


point_to_layer_houses_turnedoff = assign("""
    function(feature, latlng, context){
        var preds = feature.properties.preds;
        var color = preds <= 0.5 ? 
            'rgb(' + Math.round(255 * (2 * preds)) + ', 255, 0)' : 
            'rgb(255, ' + Math.round(255 * (2 * (1 - preds))) + ', 0)';
        var radius = 5 + (10 * preds); // Base radius 5, max radius 15
        return L.circleMarker(latlng, {
            radius: radius,
            color: color,
            weight: 1,
            opacity: 1,
            fillOpacity: 1,
            fillColor: color
        });
    }
""")

# Создаем функцию для обновления цвета метки
def update_marker_color(feature, color):
    feature['properties']['color'] = color
    return feature

# URL для стилей карты Mapbox
mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
mapbox_ids = ["light-v10", "dark-v10", "streets-v11", "outdoors-v11", "satellite-streets-v11"]
access_token = 'pk.eyJ1IjoiZW5vdHdoeW5vdCIsImEiOiJjbHhkcDBramwwMzdiMmpzNmUyanV5aDZrIn0.6ipUaOvxYv4AVt9q--1vdA'


# Объект карты 
map = dl.Map(id='map_id', style={'width': '100%', 'height': '500px'}, center=[55.787715, 37.775631], zoom=11,
             attributionControl=False,
             children=[
    dl.TileLayer(url=mapbox_url.format(id="dark-v10", access_token=access_token), id="tile-layer"),

    # ЦПТ
    dl.GeoJSON(data=geojson, cluster=True, zoomToBoundsOnClick=True,
        options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
        onEachFeature=on_each_feature,
        id="geojson"),
                    # ДОМА 
    dl.GeoJSON(data=geojson_houses, cluster=True, zoomToBoundsOnClick=True,
        options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
        pointToLayer=point_to_layer_houses,  # how to draw points
        onEachFeature=on_each_feature_houses,
        id="geojson_houses",
        hoverStyle={'fillOpacity': 0.5}),

    dl.LocateControl(
        locateOptions={'enableHighAccuracy': True},
        iconElementTag='span'
    )
])

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

rootLayout = html.Div([daq.Knob(id='darktheme-daq-knob', className='dark-theme-control', min=-26, max=8, value=0)])

layout = html.Div([
    dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col(width=8, children=[
                html.H1("Интерактивная карта остывания домов при отключении ЦТП", id='title', style={'textAlign': 'center', 'fontSize': '26px', 'marginBottom': '0px'}),
                html.Div(map, id='map-container'),

                html.Div(id='input-container', children=[
                    dcc.Input(id='input-id', type='number', placeholder='Введите id ЦПТ'),
                    html.Button('Отключить ЦТП', id='power-off-button')
                ]),           

                html.Div(id='button-container', children=[
                    html.Button('Сбросить карту', id='reset-map-button')
                ]),

                dcc.Dropdown(
                    id='map-style-dropdown',
                    options=[{'label': style, 'value': style} for style in mapbox_ids],
                    value='dark-v10',
                    placeholder="Выберите стиль карты"
                )
            ]),
            dbc.Col(width=4, children=[
                html.H3("Температура окружающей среды", id='temp_title', style={'textAlign': 'center', 'fontSize': '24px', 'marginBottom': '0px'}),
                dcc.Store(id='temp-store'),
                html.Div(id='dark-theme-components', children=[
                    daq.DarkThemeProvider(theme=theme, children=rootLayout)
                    ], style={
                        'border': 'solid 1px #A2B1C6',
                        'border-radius': '5px',
                        'padding': '50px',
                        'marginTop': '20px'
                    }),
                html.H4('Перевод параметров:', style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li('Address - адрес'),
                    html.Li('UNOM - номер БТИ'),
                    html.Li('CTP number - номер ЦТП'),
                    html.Li('Heatstation - наименование источника'),
                    html.Li('Time left - время критического остывания, ч'),
                    html.Li('Heat consumption - потребляемая мощность, Гкал/ч'),

                ])
            ])
        ])
    ])
])

@callback(Output('temp-store', 'data'),
              Input('darktheme-daq-knob', 'value'))
def filter_countries(temp):
    return temp

    

@callback(
    [Output('geojson', 'data'), Output('tile-layer', 'url')],
    [Input('geojson', 'click_feature'), Input('map-style-dropdown', 'value'), Input('map_id', 'click_lat_lng')],
    prevent_initial_call=True
)
def update_geojson_and_map_style(feature, selected_style, click_lat_lng):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'geojson' and feature:
        feature = update_marker_color(feature, 'red')
        return {
            "type": "FeatureCollection",
            "features": [feature]
        }, no_update

    elif trigger_id == 'map-style-dropdown':
        return no_update, mapbox_url.format(id=selected_style, access_token=access_token)

    elif trigger_id == 'map_id' and click_lat_lng:
        user_feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [click_lat_lng['lng'], click_lat_lng['lat']]},
            "properties": {"Адрес ТП": "Мое местоположение"}
        }
        features.append(user_feature)
        return {
            "type": "FeatureCollection",
            "features": features
        }, no_update

    return no_update, no_update

@callback(
    [Output('input-id', 'value'), Output('map-container', 'children'), Output('temp_title', 'children')],
    [Input('power-off-button', 'n_clicks'), Input('reset-map-button', 'n_clicks'), Input('temp-store', 'data')],
    [State('input-id', 'value')]
)
def update_output(b1, b2, knob_value, input_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id


    if input_value in df_TP_all.index and triggered_id == 'power-off-button':
        TP_address = df_TP_all.loc[input_value]['Адрес ТП']
        
        UNOMS, df_TP, df_houses = find_ternd_off([TP_address])

        center = df_TP.loc[:, ['latitude_x', 'longitude_x']].values.tolist()[0] #TODO

        cut_off_homes = all_data[all_data['UNOM'].isin(UNOMS)]

        cut_off_homes['time_in_hours'] = cut_off_homes['betta'].apply(collDown, args=[knob_value])
        cut_off_homes = cut_off_homes.apply(heat_col, args=[knob_value], axis=1)

        cut_off_homes['preds'] = 1 - (cut_off_homes['time_in_hours'] - cut_off_homes['time_in_hours'].min()) / (cut_off_homes['time_in_hours'].max() - cut_off_homes['time_in_hours'].min())

        features = get_features_TP(df_TP)
        features_houses = get_featurers_houses(df_houses)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        features_houses = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['longitude_y'], row['latitude_y']]},
                "properties": {"Address": row['Адрес'], "UNOM": row['UNOM'], "ctp_number": row['ctp_number'], "heatstation": row['heatstation'],
                                'time_in_hours': row['time_in_hours'], 'heatloss': row['heatloss'], 'preds': row['preds']}
            } for index, row in cut_off_homes.iterrows()
        ]

        geojson_houses = {
            "type": "FeatureCollection",
            "features": features_houses
        }

        map_updated = dl.Map(id='map_id', style={'width': '100%', 'height': '500px'}, center=center, zoom=11, children=[
            dl.TileLayer(url=mapbox_url.format(id="dark-v10", access_token=access_token), id="tile-layer"),

            # ЦПТ
            dl.GeoJSON(data=geojson, cluster=True, zoomToBoundsOnClick=True,
                options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                onEachFeature=on_each_feature,
                id="geojson"),
            # ДОМА 
            dl.GeoJSON(data=geojson_houses, cluster=True, zoomToBoundsOnClick=True,
                options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                pointToLayer=point_to_layer_houses_turnedoff,
                onEachFeature=on_each_feature_houses_turnedoff,
                id="geojson_houses"),
            dl.LocateControl(
                locateOptions={'enableHighAccuracy': True},
                iconElementTag='span'
            )
        ])
        return [None, map_updated, f'Температура окружающей среды {knob_value}']
    else:

        # Обновление всех домов        
        all_homes = all_data[all_data['UNOM'].isin(df_houses_all['UNOM'].tolist())]

        all_homes = all_homes.apply(heat_col, args=[knob_value], axis=1)
        all_homes['preds'] = (all_homes['heatloss'] - all_homes['heatloss'].min()) / (all_homes['heatloss'].max() - all_homes['heatloss'].min())

        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['longitude_x'], row['latitude_x']]},
                "properties": {"Address": row['Адрес ТП'], "id": index}
            }
            for index, row in df_TP_all.iterrows()
        ]

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        features_houses = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['longitude_y'], row['latitude_y']]},
                "properties": {"Address": row['Адрес'], "UNOM": row['UNOM'], "ctp_number": row['ctp_number'], "heatstation": row['heatstation'], 'heatloss': row['heatloss'], 'preds': row['preds']}
            } for index, row in all_homes.iterrows()
        ]

        geojson_houses = {
            "type": "FeatureCollection",
            "features": features_houses
        }

        map_updated = dl.Map(id='map_id', style={'width': '100%', 'height': '500px'}, center=[55.787715, 37.775631], zoom=11, children=[
            dl.TileLayer(url=mapbox_url.format(id="dark-v10", access_token=access_token), id="tile-layer"),

            # ЦПТ
            dl.GeoJSON(data=geojson, cluster=True, zoomToBoundsOnClick=True,
                options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                onEachFeature=on_each_feature,
                id="geojson"),
            # ДОМА 
            dl.GeoJSON(data=geojson_houses, cluster=True, zoomToBoundsOnClick=True,
                options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                onEachFeature=on_each_feature_houses,
                pointToLayer=point_to_layer_houses,
                id="geojson_houses"),
            dl.LocateControl(
                locateOptions={'enableHighAccuracy': True},
                iconElementTag='span'
            )
        ])
        return [None, map_updated, f'Температура окружающей среды {knob_value}']




@callback(
    dash.dependencies.Output('dark-theme-components', 'children'),
    [dash.dependencies.Input('toggle-theme', 'value'),
     dash.dependencies.Input('primary-color', 'value'),
     dash.dependencies.Input('secondary-color', 'value'),
     dash.dependencies.Input('detail-color', 'value')]
)
def edit_theme(dark):

    if(dark):
        theme.update(
            dark=True
        )
    else:
        theme.update(
            dark=False
        )   

    return daq.DarkThemeProvider(theme=theme, children=rootLayout)


@callback(
    dash.dependencies.Output('dark-theme-components', 'style'),
    [dash.dependencies.Input('toggle-theme', 'value')]
)
def switch_bg(dark, currentStyle):
    if(dark):
        currentStyle.update(
            backgroundColor='#303030'
        )
    else:
        currentStyle.update(
            backgroundColor='gray'
        )
    return currentStyle