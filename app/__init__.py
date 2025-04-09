from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Import routes after app is created to avoid circular imports
from app import routes

def create_app():
    return app 