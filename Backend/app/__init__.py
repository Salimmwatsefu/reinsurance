from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid warnings
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    db.init_app(app)
    jwt.init_app(app)
    from app.models import User, Claim, Prediction, ModelStats

    from app.routes.auth_routes import auth_bp
    from app.routes.claim_routes import claim_bp
    from app.routes.ml_routes import ml_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(claim_bp, url_prefix='/claim')
    app.register_blueprint(ml_bp, url_prefix='/ml')
    
    return app