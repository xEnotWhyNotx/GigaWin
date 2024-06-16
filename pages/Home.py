import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/')

# Пример данных для визуализаций
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D'],
    'Values': [10, 23, 17, 28]
})

# Пример простой диаграммы
fig = px.bar(df, x='Category', y='Values', title='Пример столбчатой диаграммы')

layout = html.Div([
    html.H1('Домашняя страница проекта ЛЦТ'),
    
    html.Div('Команда: Сергей и Матвей'),
    
    html.Div('''DataSus Developers'''),
    
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    
    html.Div([
        html.H2('Другие визуализации'),
        # Здесь могут быть добавлены другие графики или визуализации
    ]),
    
    html.Div([
        html.H2('Контактная информация'),
        html.P('Email: sergey@example.com'),
        html.P('Email: matvey@example.com'),
    ])
])
