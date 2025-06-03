from flask import Flask
from flask_login import LoginManager
from .models import db
from app.models import User

login_manager = LoginManager()
login_manager.login_view = 'main.login'
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "6f3b1c832e2e4d9b9f2fc5a5d4d20e13"

    from app.routes import bp

    app.register_blueprint(bp)

    db.init_app(app)

    from app import routes
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    return app
