from flask import Flask
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app

app = create_app()
login_manager = LoginManager(app)

