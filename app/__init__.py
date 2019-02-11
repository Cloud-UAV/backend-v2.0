from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restless import APIManager
from flask_marshmallow import Marshmallow
from config import Config

app = Flask(__name__)
CORS(app)
app.config.from_object(obj=Config)
db = SQLAlchemy(app=app)
ma = Marshmallow(app=app)
manager = APIManager(app=app, flask_sqlalchemy_db=db)
migrate = Migrate(app=app, db=db)


from app import routes
