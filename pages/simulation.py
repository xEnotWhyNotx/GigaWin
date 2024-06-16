from dash import Dash, dcc, html, Input, Output, callback, no_update, register_page, State
import dash
import pandas as pd
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import json
from dash_extensions.javascript import assign

register_page(__name__, path='/simulation')

# Загружаем данные
df_for_tern_off = pd.read_pickle('df_for_tern_off.pkl')

def find_all_geo():
    df_TP = df_for_tern_off[['Адрес ТП', 'latitude_x', 'longitude_x']].drop_duplicates()
    df_houses = df_for_tern_off[['Адрес', 'UNOM', 'longitude_y', 'latitude_y']].drop_duplicates()
    return df_TP, df_houses

df_TP_all, df_houses_all = find_all_geo()
df1 = df_TP_all
df_houses = df_houses_all

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
        return L.circleMarker(latlng, {
            radius: 5,
            color: 'red',
            weight: 1,
            opacity: 1,
            fillOpacity: 1,
            fillColor: 'red'
        });
    }
""")

on_each_feature_houses = assign("""
    function(feature, layer, context){
        layer.bindTooltip(
            '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>id:</b> ' + feature.properties['id'] + '<br>' +
                '<b>UNOM:</b> ' + feature.properties['UNOM'] +
            '</div>',
            {permanent: false, direction: 'top'}
        );
    }
""")

def update_marker_color(feature, color):
    feature['properties']['color'] = color
    return feature

mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
mapbox_ids = ["light-v10", "dark-v10", "streets-v11", "outdoors-v11", "satellite-streets-v11"]
access_token = 'pk.eyJ1IjoiZW5vdHdoeW5vdCIsImEiOiJjbHhkcDBramwwMzdiMmpzNmUyanV5aDZrIn0.6ipUaOvxYv4AVt9q--1vdA'

map = dl.Map(id='map_id', style={'width': '100%', 'height': '500px'}, center=[55.787715, 37.775631], zoom=11, children=[
    dl.TileLayer(url=mapbox_url.format(id="streets-v11", access_token=access_token), id="tile-layer"),

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

layout = html.Div([
    dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col(width=8, children=[
                html.H1("Интерактивная карта остывания домов при отключении ЦТП", id='title'),
                html.Div(map, id='map-container'),
                dcc.Dropdown(
                    id='temperature-dropdown',
                    options=[{'label': f'{i}°C', 'value': i} for i in range(-30, 51, 10)],
                    value=20,
                    placeholder="Выберите температуру"
                ),

                html.Div(id='input-container', children=[
                    dcc.Input(id='input-id', type='number', placeholder='Введите id ЦПТ'),
                    html.Button('Отключить ЦТП', id='power-off-button')
                ]),           

                html.Div(id='button-container', children=[
                    html.Button('Начать симуляцию', id='my-button'),
                    html.Button('Сбросить карту', id='reset-map-button')
                ]),

                dcc.Dropdown(
                    id='map-style-dropdown',
                    options=[{'label': style, 'value': style} for style in mapbox_ids],
                    value='streets-v11',
                    placeholder="Выберите стиль карты"
                )
            ]),
            dbc.Col(width=4, children=[
                html.H3("Тут что-то будет")
            ])
        ])
    ])
])

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
    [Output('input-id', 'value'), Output('map-container', 'children')],
    [Input('power-off-button', 'n_clicks'), Input('reset-map-button', 'n_clicks')],
    [State('input-id', 'value')]
)
def update_output(b1, b2, input_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id

    if input_value in df_TP_all.index and triggered_id == 'power-off-button':
        TP_address = df_TP_all.loc[input_value]['Адрес ТП']
        
        UNOMS, df_TP, df_houses = find_ternd_off([TP_address])

        center = df_TP.loc[:, ['latitude_x', 'longitude_x']].values.tolist()[0]

        features = get_features_TP(df_TP)
        features_houses = get_featurers_houses(df_houses)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        geojson_houses = {
            "type": "FeatureCollection",
            "features": features_houses
        }

        map_updated = dl.Map(id='map_id', style={'width': '100%', 'height': '500px'}, center=center, zoom=11, children=[
            dl.TileLayer(url=mapbox_url.format(id="streets-v11", access_token=access_token), id="tile-layer"),

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

        return [None, map_updated]
    
    elif triggered_id == 'reset-map-button':
        return [None, map]
    
    else:
        return [None, map]
