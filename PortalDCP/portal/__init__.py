from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '68c078b063b6560c0e53e58ed830460c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'logar'
login_manager.login_message = 'Para acessar essa página é necessário estar logado'
login_manager.login_message_category = 'alert-info'

from portal import routes
# nesse caso a importação do routes vem
# em baixo pois ele preceisa que o app
# seja criado antes