from flask import Flask
from SciVerse.ext import db, login_manager, bcrypt
from flask_migrate import Migrate
from SciVerse.routes import bp as routes_bp
from SciVerse.init_data import create_main_user
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(routes_bp)

    with app.app_context():
        db.create_all()
        create_main_user()

    return app

app = create_app()
