from dash import Dash, dcc, html, Input, Output, register_page, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from dash_extensions.javascript import assign
from Prediction_pypeline import predict


register_page(__name__, path='/prediction')

# Загружаем данные
df_for_tern_off = pd.read_pickle('service/df_for_tern_off.pkl')
df_walls = pd.read_pickle('service/dict_predict_walls.pkl')
df_serie = pd.read_pickle('service/dict_predict_serie.pkl')
# убираем лишний район москвы
df_for_tern_off = df_for_tern_off[df_for_tern_off['latitude_y'] < 55.87]
# df_preds_cat = pd.read_csv('service/preds_cat.csv')
df_preds_cat = predict()

def find_all_geo():
    df_TP = df_for_tern_off[['Адрес ТП', 'latitude_x', 'longitude_x']].drop_duplicates()
    df_houses = df_for_tern_off[['Адрес', 'UNOM', 'longitude_y', 'latitude_y']].drop_duplicates()
    return df_TP, df_houses

df_TP_all, df_houses_all = find_all_geo()

# Объединяем данные по домам с данными из CSV
df_houses_all = df_houses_all.merge(df_preds_cat, on='UNOM', how='left')
df_houses_all.rename(columns={
    'UNOM': 'UNOM',
    'preds': 'preds',
    'Объём поданого теплоносителя в систему ЦО_mean': 'volume_mean',
    'Объём поданого теплоносителя в систему ЦО_std': 'volume_std',
    'Объём поданого теплоносителя в систему ЦО_median': 'volume_median',
    'Расход тепловой энергии _mean': 'energy_mean',
    'Расход тепловой энергии _std': 'energy_std',
    'Расход тепловой энергии _median': 'energy_median',
    'temperature_mean': 'temperature_mean',
    'Количество жалоб_mean': 'complaints_mean',
    'Подмес/Утечка_mean': 'leakage_mean',
    'Подмес/Утечка_std': 'leakage_std',
    'ERR_mean': 'err_mean',
    'ERR_std': 'err_std',
    'target_max': 'target_max',
    'Стены': 'walls',
    'predict_serie': 'predict_serie',
    'total_area': 'total_area',
    'predict_wear': 'predict_wear',
    'old': 'old'
}, inplace=True)

df_houses_all['walls'] = df_houses_all['walls'].replace(df_walls)
df_houses_all['predict_serie'] = df_houses_all['predict_serie'].replace(df_serie)

# Создаем структуру GeoJSON для ЦПТ
features_tp = [
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row['longitude_x'], row['latitude_x']]},
        "properties": {"Address": row['Адрес ТП'], "id": index}
    }
    for index, row in df_TP_all.iterrows()
]

geojson_tp = {
    "type": "FeatureCollection",
    "features": features_tp
}

on_each_feature_tp = assign("""
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
features_houses = [
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row['longitude_y'], row['latitude_y']]},
        "properties": {
            "Address": row['Адрес'],
            "id": index,
            "UNOM": str(row['UNOM']),
            "preds": str(row['preds']),
            "volume_mean": str(row['volume_mean']),
            "volume_std": str(row['volume_std']),
            "volume_median": str(row['volume_median']),
            "energy_mean": str(row['energy_mean']),
            "energy_std": str(row['energy_std']),
            "energy_median": str(row['energy_median']),
            "temperature_mean": str(row['temperature_mean']),
            "complaints_mean": str(row['complaints_mean']),
            "leakage_mean": str(row['leakage_mean']),
            "leakage_std": str(row['leakage_std']),
            "err_mean": str(row['err_mean']),
            "err_std": str(row['err_std']),
            "target_max": str(row['target_max']),
            "walls": str(row['walls']),
            "predict_serie": str(row['predict_serie']),
            "total_area": str(row['total_area']),
            "predict_wear": str(row['predict_wear']),
            "old": str(row['old'])
        }
    }
    for index, row in df_houses_all.iterrows()
]

geojson_houses = {
    "type": "FeatureCollection",
    "features": features_houses
}

point_to_layer_houses = assign("""
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

on_each_feature_houses = assign("""
    function(feature, layer, context){
        layer.bindTooltip(
            '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>UNOM:</b> ' + feature.properties['UNOM'] + '<br>' +
                '<b>PREDICT:</b> ' + feature.properties['preds'] + '<br>' +
                '<b>Volume supplied (mean):</b> ' + feature.properties['volume_mean'] + '<br>' +
                '<b>Energy consumption (mean):</b> ' + feature.properties['energy_mean'] + '<br>' +
                '<b>Average temperature:</b> ' + feature.properties['temperature_mean'] + '<br>' +
                '<b>Number of complaints (mean):</b> ' + feature.properties['complaints_mean'] + '<br>' +
                '<b>Leakage (mean):</b> ' + feature.properties['leakage_mean'] + '<br>' +
                '<b>Error (mean):</b> ' + feature.properties['err_mean'] + '<br>' +
                '<b>Target max value:</b> ' + feature.properties['target_max'] + '<br>' +
                '<b>Walls:</b> ' + feature.properties['walls'] + '<br>' +
                '<b>Predicted series:</b> ' + feature.properties['predict_serie'] + '<br>' +
                '<b>Total area:</b> ' + feature.properties['total_area'] + '<br>' +
                '<b>Wear prediction:</b> ' + feature.properties['predict_wear'] + '<br>' +
                '<b>Age:</b> ' + feature.properties['old'] +
            '</div>',
            {permanent: false, direction: 'top'}
        );
    }
""")

# Функция для получения топ 10 домов
def get_top_10_houses(df):
    top_10 = df.nlargest(10, 'preds')[['UNOM', 'Адрес', 'preds']]
    return top_10.to_dict('records')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1('Карта потенциальных аварий', style={'textAlign': 'center', 'fontSize': '36px'}),
            html.P('Результат получен на основе МЛ модели', style={'textAlign': 'center'}),
            dl.Map(id='map_id', style={'width': '95%', 'height': '700px'}, center=[55.7558, 37.6173], zoom=11,
                   attributionControl=False,
                   children=[
                dl.TileLayer(url="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZW5vdHdoeW5vdCIsImEiOiJjbHhkcDBramwwMzdiMmpzNmUyanV5aDZrIn0.6ipUaOvxYv4AVt9q--1vdA", id="tile-layer"),
                
                # ЦТП
                dl.GeoJSON(data=geojson_tp, cluster=True, zoomToBoundsOnClick=True,
                           options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                           onEachFeature=on_each_feature_tp,
                           id="geojson_tp"),
                
                # ДОМА 
                dl.GeoJSON(data=geojson_houses, cluster=True, zoomToBoundsOnClick=True,
                           options={"spiderfyOnMaxZoom": True, "showCoverageOnHover": True, "zoomToBoundsOnClick": True},
                           pointToLayer=point_to_layer_houses,
                           onEachFeature=on_each_feature_houses,
                           id="geojson_houses"),

                dl.LocateControl(
                    locateOptions={'enableHighAccuracy': True},
                    iconElementTag='span'
                )
            ]),
        ], width=8, style={'paddingRight': '0'}),
        dbc.Col([
            html.H1('Потенциально аварийные здания', style={'textAlign': 'center', 'fontSize': '36px', 'marginBottom': '20px'}),
            html.P('Список зданий с самым высоким риском аварии', style={'textAlign': 'center'}),
            dash_table.DataTable(
                id='top-10-table',
                columns=[
                    {'name': 'UNOM', 'id': 'UNOM'},
                    {'name': 'Адрес', 'id': 'Адрес'},
                    {'name': 'Вероятность отказа', 'id': 'preds'},
                ],
                style_table={'height': 'auto', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '5px', 'backgroundColor': '#f9f9f9', 'color': '#333'},
                style_header={
                    'backgroundColor': '#4CAF50',
                    'fontWeight': 'bold',
                    'color': 'white',
                    'fontSize': '18px'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f2f2f2'
                    },
                    {
                        'if': {'row_index': 'even'},
                        'backgroundColor': '#ffffff'
                    }
                ],
                data=get_top_10_houses(df_houses_all)
            ),
            html.Div([
                html.H4('Перевод параметров:', style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li('Volume supplied - Объём поданого теплоносителя'),
                    html.Li('Energy consumption - Расход тепловой энергии'),
                    html.Li('Average temperature - Средняя температура'),
                    html.Li('Number of complaints (mean) - Количество жалоб (среднее)'),
                    html.Li('Leakage - Подмес/Утечка'),
                    html.Li('Error - Ошибка'),
                    html.Li('Target max value - Максимальное значение целевого показателя'),
                    html.Li('Walls - Стены'),
                    html.Li('Predicted series - Предсказанная серия'),
                    html.Li('Total area - Общая площадь'),
                    html.Li('Wear prediction - Прогноз износа'),
                    html.Li('Age - Возраст')
                ])
            ])
        ], width=4, style={'paddingLeft': '0'})
    ], style={'margin': '0'})
])
