"""Application entry point."""
from dash_dashboard import init_app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)
