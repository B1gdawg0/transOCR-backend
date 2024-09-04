from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['JWT_SECRET_KEY'] = 'f28a27d5e7f3553f8171c7004dd28bceded5518103559304df03f6a6e1899850'
app.config['SECRET_KEY'] = '7fa334fcc1759fe37db255a2a065bdf4692ab2b1021cc9462b44d41b72687464'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'src/ocr_model/data/raw'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
CORS(app, resources={r"/*": {"origins": "*"}})

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
csrf = CSRFProtect(app)

db = SQLAlchemy(app)


from src import routes