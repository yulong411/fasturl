import os
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.auth import login_manager, bp
    login_manager.init_app(app)
    app.register_blueprint(bp)

    from .routes.main import bp
    app.register_blueprint(bp)

    from .routes.url import bp
    app.register_blueprint(bp) 

    return app

