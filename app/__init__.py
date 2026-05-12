from flask import Flask, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migration = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

@app.context_processor
def inject_auth_state():
	return {"is_authenticated": session.get("is_authenticated", False)}

from app import routes
from app import models