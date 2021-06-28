from flask import Flask

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        from .musedash.dashboard import init_muse_dashboard
        app = init_muse_dashboard(app)

        return app
