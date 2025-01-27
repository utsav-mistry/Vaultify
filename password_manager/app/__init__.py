from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail 
from dotenv import load_dotenv
import os

# Initialize the app
app = Flask(__name__)

load_dotenv()

# App configurations
app.config['SECRET_KEY'] = 'vaultify-spms'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587  # Port for sending email
app.config['MAIL_USE_TLS'] = True  # TLS encryption
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Mail
mail = Mail(app)

# Import routes
from app import routes
