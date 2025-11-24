import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['SECRET_KEY'] = SECRET_KEY
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

db = SQLAlchemy(app)

from .auth import auth_group
app.register_blueprint(auth_group, url_prefix = '/auth')

from .user import user_group
app.register_blueprint(user_group, url_prefix="/user")

from src.user import routes