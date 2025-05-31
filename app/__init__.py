from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app.routes import bp
    app.register_blueprint(bp)
    
    db.init_app(app)

    from app import routes  
    return app
