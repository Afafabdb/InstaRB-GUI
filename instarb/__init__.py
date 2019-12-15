from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from cryptography.fernet import Fernet
from urlextract import URLExtract

app = Flask(__name__)

app.config['SECRET_KEY'] = '275bde05bb6b0907003b48be371edeb7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instarb.db'

DECRYPT_STRING= 'u10HafbTRt0Kg3iVUaNxkM1OPzZx18H192Acpn--ADc='

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
cipher_suite = Fernet(bytes(DECRYPT_STRING, encoding='utf-8'))
url_extractor = URLExtract()

from instarb import routes