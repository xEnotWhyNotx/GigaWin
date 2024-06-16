import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
        html.Div(id='particles-js', className='animated-background'),  # Контейнер для particles.js
        html.Div(
            className='content',
            style={
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center',
                'height': '100vh',
                'text-align': 'center',
                'width': '100%',
            },
            children=[
                html.Div([
                    html.H1('Домашняя страница проекта ЛЦТ'),
                    html.Div('Команда: Сергей и Матвей'),
                    html.Div('DataSus Developers'),
                    html.Div([
                        html.H2('Контактная информация'),
                        html.P('Telegram: @xEnotWhyNotx'),
                        html.P('Telegram: @LebedevMatvey'),
                    ])
                ])
            ]
        ),
        # Добавляем скрипты particles.js и конфигурации
        dcc.Store(id='js-particles', data={
            'particles': '/assets/particles.min.js',
            'config': '/assets/particles-config.json'
        }),
        html.Script(src='/assets/particles.min.js'),
        html.Script(
            """
            document.addEventListener('DOMContentLoaded', function() {
                particlesJS.load('particles-js', '/assets/particles-config.json', function() {
                    console.log('particles.js config loaded');
                });
            });
            """
        )
    ]
)
