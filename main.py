from dash import Dash, dcc, html, Input, Output, page_registry, page_container
import dash_bootstrap_components as dbc
from dash_auth import BasicAuth
from config import secret_key, username_password_pairs

app = Dash(__name__,
           external_stylesheets=['assets/styles.css', dbc.themes.BOOTSTRAP],
           use_pages=True)
app.config.suppress_callback_exceptions=True

app.server.secret_key = secret_key  # stored in .env file and is imported from config

auth = BasicAuth(
    app,
    username_password_pairs  # stored in .env file and is imported from config
)

# Dictionary for translating English page names to Russian
page_translations = {
    'Home': 'Главная',
    'Prediction': 'Прогноз',
    'Simulation': 'Симуляция'
}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='particles-js', className='animated-background'),  # Container for particles.js
    html.Div(
        className='content',
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'height': '100vh',
            'width': '100%',
        },
        children=[
            html.Nav(  # nav bar
                children=[
                    html.A(page_translations.get(page['name'], page['name']), href=page["relative_path"], className="nav-link") for page in page_registry.values()
                ],
                className="nav nav-pills nav-fill"
            ),
            page_container  # This will render the content of the current page
        ]
    ),
    # Add particles.js and configuration scripts
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
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
